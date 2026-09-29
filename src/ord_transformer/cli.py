"""Click-based CLI for the ORD RDF Transformer.

Three sub-commands:

``transform``
    Convert an ORD JSON document to an RDF file.

``generate-shapes``
    Generate combined SHACL shapes (model-based + vocabulary-based).

``validate``
    Validate an RDF data file against a SHACL shapes file.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .transformer import ORDTransformer
from .shacl_generator import generate_combined_shapes
from .validator import SHACLValidator


@click.group()
@click.version_option(version="0.1.0", prog_name="ord-transform")
def cli() -> None:
    """ORD RDF Transformer - convert ORD JSON to RDF and validate with SHACL."""


# ── transform ─────────────────────────────────────────────────────────────────

@cli.command("transform")
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_file", type=click.Path(dir_okay=False))
@click.option(
    "--format", "-f",
    "fmt",
    default="turtle",
    show_default=True,
    type=click.Choice(["turtle", "n3", "nt", "json-ld", "xml"], case_sensitive=False),
    help="RDF serialisation format for the output file.",
)
@click.option(
    "--base-uri",
    default="https://open-resource-discovery.org/instance/",
    show_default=True,
    help="Base URI used when building instance URIs from ORD IDs.",
)
def transform_cmd(input_file: str, output_file: str, fmt: str, base_uri: str) -> None:
    """Transform INPUT_FILE (ORD JSON) to OUTPUT_FILE (RDF).

    \b
    Example:
        ord-transform transform data/samples/sample_ord.json output/ord_data.ttl
        ord-transform transform sample.json data.nt --format nt
    """
    click.echo(f"Transforming {input_file} -> {output_file} [{fmt}]")
    try:
        transformer = ORDTransformer(base_instance_uri=base_uri)
        out = transformer.transform_to_file(input_file, output_file, fmt=fmt)
        click.secho(f"[OK] Written: {out}", fg="green")
    except Exception as exc:
        click.secho(f"[ERROR] {exc}", fg="red", err=True)
        sys.exit(1)


# ── generate-shapes ───────────────────────────────────────────────────────────

@cli.command("generate-shapes")
@click.argument("output_file", type=click.Path(dir_okay=False))
@click.option(
    "--vocab",
    "vocab_path",
    default=None,
    type=click.Path(exists=True, dir_okay=False),
    help=(
        "Path to ord_open_vocab.ttl. When supplied, vocabulary-derived shapes "
        "are merged with the model-based shapes."
    ),
)
@click.option(
    "--format", "-f",
    "fmt",
    default="turtle",
    show_default=True,
    type=click.Choice(["turtle", "n3", "nt", "json-ld", "xml"], case_sensitive=False),
)
def generate_shapes_cmd(
    output_file: str,
    vocab_path: str | None,
    fmt: str,
) -> None:
    """Generate combined SHACL shapes and write to OUTPUT_FILE.

    Always produces the full combined output (model-based shapes merged with
    vocabulary-derived shapes when --vocab is supplied).

    \b
    Examples:
        # Model + vocabulary shapes (recommended):
        ord-transform generate-shapes data/shapes/ord_shapes.ttl --vocab data/vocab/ord_open_vocab.ttl
        # Model shapes only (no vocabulary file):
        ord-transform generate-shapes data/shapes/ord_shapes.ttl
    """
    try:
        click.echo("Generating combined SHACL shapes")
        g = generate_combined_shapes(
            vocab_path=Path(vocab_path) if vocab_path else None
        )

        out = Path(output_file)
        out.parent.mkdir(parents=True, exist_ok=True)
        g.serialize(str(out), format=fmt)
        triples = len(g)
        click.secho(f"[OK] Written {triples} triples -> {out}", fg="green")
    except Exception as exc:
        click.secho(f"[ERROR] {exc}", fg="red", err=True)
        sys.exit(1)


# ── validate ──────────────────────────────────────────────────────────────────

@cli.command("validate")
@click.argument("data_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("shapes_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--data-format", default="turtle", show_default=True,
    type=click.Choice(["turtle", "n3", "nt", "json-ld", "xml"], case_sensitive=False),
)
@click.option(
    "--shapes-format", default="turtle", show_default=True,
    type=click.Choice(["turtle", "n3", "nt", "json-ld", "xml"], case_sensitive=False),
)
@click.option(
    "--inference", default="rdfs", show_default=True,
    type=click.Choice(["none", "rdfs", "owlrl", "both"], case_sensitive=False),
    help="RDFS/OWL inference level applied before validation.",
)
@click.option(
    "--report-file",
    default=None,
    type=click.Path(dir_okay=False),
    help="Optional path to write the SHACL validation report (Turtle).",
)
def validate_cmd(
    data_file: str,
    shapes_file: str,
    data_format: str,
    shapes_format: str,
    inference: str,
    report_file: str | None,
) -> None:
    """Validate DATA_FILE against SHAPES_FILE (SHACL).

    \b
    Example:
        ord-transform validate output/ord_data.ttl output/ord_shapes.ttl
        ord-transform validate data.ttl shapes.ttl --report-file report.ttl
    """
    click.echo(f"Validating {data_file} against {shapes_file}")
    try:
        validator = SHACLValidator(inference=inference)
        result = validator.validate_files(
            data_file, shapes_file,
            data_fmt=data_format,
            shapes_fmt=shapes_format,
        )

        if result.conforms:
            click.secho("[CONFORMS] Data graph satisfies all SHACL constraints.", fg="green")
        else:
            click.secho(
                f"[VIOLATIONS: {result.violation_count}] Data graph does NOT conform.",
                fg="red",
            )
            click.echo(result.results_text)

        if report_file:
            report_path = Path(report_file)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            result.results_graph.serialize(str(report_path), format="turtle")
            click.echo(f"  Report written -> {report_path}")

        sys.exit(0 if result.conforms else 1)
    except Exception as exc:
        click.secho(f"✗ Error: {exc}", fg="red", err=True)
        sys.exit(2)


if __name__ == "__main__":
    cli()
