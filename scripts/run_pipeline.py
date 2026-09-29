"""ORD RDF Transformer — end-to-end pipeline.

Runs three steps for a given ORD JSON document:

  Step 1  Transform  <input>.json  ->  output/<stem>.ttl
  Step 2  Generate SHACL shapes  (skipped when up-to-date)
  Step 3  Validate   <stem>.ttl  against  data/shapes/ord_shapes_generated.ttl

Usage::

    # Default input (example_ord_combined.json)
    python scripts/run_pipeline.py

    # Custom input file
    python scripts/run_pipeline.py data/samples/sample_ord.json

    # Force shapes regeneration even if they are up-to-date
    python scripts/run_pipeline.py --force-shapes

Step 2 is skipped automatically when the shapes file already exists AND is
newer than every model source file (``src/ord_transformer/models/**/*.py``)
and the vocabulary file (``data/vocab/ord_open_vocab.ttl``).  Pass
``--force-shapes`` to override this check.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# ── Ensure src/ is importable when running directly ───────────────────────────
_project_root = Path(__file__).parent.parent
sys.path.insert(0, str(_project_root / "src"))

from ord_transformer.shacl_generator import generate_combined_shapes
from ord_transformer.transformer import ORDTransformer
from ord_transformer.validator import SHACLValidator

# ── Fixed paths ───────────────────────────────────────────────────────────────
OUTPUT = _project_root / "output"
OUTPUT.mkdir(exist_ok=True)

VOCAB_FILE      = _project_root / "data" / "vocab" / "ord_open_vocab.ttl"
SHAPES_DIR      = _project_root / "data" / "shapes"
SHAPES_PREBUILT = SHAPES_DIR / "ord_open_shapes.ttl"      # hand-authored, ships with the project
SHAPES_GENERATED = SHAPES_DIR / "ord_shapes_generated.ttl"  # auto-generated from models + vocab
MODELS_DIR      = _project_root / "src" / "ord_transformer" / "models"

SHAPES_DIR.mkdir(exist_ok=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sep(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def _shapes_are_stale() -> bool:
    """Return True if the shapes file is missing or older than any source file.

    Checks every ``*.py`` under ``src/ord_transformer/models/`` and the
    vocabulary TTL.  Returns False (not stale) only when the shapes file
    exists and is strictly newer than all of them.
    """
    if not SHAPES_GENERATED.exists():
        return True

    shapes_mtime = SHAPES_GENERATED.stat().st_mtime

    # Compare against all model source files
    for py_file in MODELS_DIR.rglob("*.py"):
        if py_file.stat().st_mtime > shapes_mtime:
            return True

    # Compare against the vocabulary file
    if VOCAB_FILE.exists() and VOCAB_FILE.stat().st_mtime > shapes_mtime:
        return True

    return False


# ── Pipeline steps ────────────────────────────────────────────────────────────

def step1_transform(data_file: Path, data_rdf: Path) -> int:
    """Transform ORD JSON -> RDF Turtle.  Returns triple count."""
    _sep("STEP 1 - Transform ORD JSON -> RDF (Turtle)")
    transformer = ORDTransformer()
    transformer.transform_to_file(data_file, data_rdf, fmt="turtle")
    triples = len(transformer.transform_file(data_file))
    print(f"  Input   : {data_file}")
    print(f"  Output  : {data_rdf}")
    print(f"  Triples : {triples:,}")
    return triples


def step2_generate_shapes(force: bool = False) -> None:
    """Generate combined SHACL shapes — skipped when already up-to-date."""
    _sep("STEP 2 - Generate combined SHACL shapes")

    if not force and not _shapes_are_stale():
        print(f"  [SKIP] Shapes are up-to-date: {SHAPES_GENERATED}")
        print("         (pass --force-shapes to regenerate)")
        return

    reason = "forced" if force else "missing or stale"
    print(f"  Reason  : {reason}")

    g = generate_combined_shapes(vocab_path=VOCAB_FILE if VOCAB_FILE.exists() else None)
    g.serialize(str(SHAPES_GENERATED), format="turtle")

    from rdflib import RDF, SH
    node_shapes = sum(1 for _ in g.subjects(predicate=RDF.type, object=SH.NodeShape))
    print(f"  Output     : {SHAPES_GENERATED}")
    print(f"  Triples    : {len(g):,}")
    print(f"  NodeShapes : {node_shapes}")


def step3_validate(data_rdf: Path, report_path: Path) -> bool:
    """Validate RDF data against the SHACL shapes.

    Uses the pre-built shapes file (``data/shapes/ord_open_shapes.ttl``) when
    it exists.  Falls back to the auto-generated ``ord_shapes_generated.ttl``
    if the pre-built file is not present.

    Returns conforms flag.
    """
    _sep("STEP 3 - Validate RDF data against SHACL shapes")

    if not data_rdf.exists():
        print(f"  [SKIP] RDF file not found: {data_rdf}")
        print("         Run Step 1 first.")
        return False

    # Prefer the pre-built shapes (new open vocabulary shapes);
    # fall back to the auto-generated file if absent.
    if SHAPES_PREBUILT.exists():
        shapes_file = SHAPES_PREBUILT
        shapes_label = "pre-built (ord_open_shapes.ttl)"
    elif SHAPES_GENERATED.exists():
        shapes_file = SHAPES_GENERATED
        shapes_label = "generated (ord_shapes_generated.ttl)"
    else:
        print("  [SKIP] No shapes file found.")
        print(f"         Expected: {SHAPES_PREBUILT}")
        print(f"         Fallback: {SHAPES_GENERATED}")
        print("         Run Step 2 first (or pass --force-shapes).")
        return False

    print(f"  Shapes  : {shapes_label}")

    # Pass the vocabulary as an ontology graph so SKOS concept type assertions
    # (e.g. ord:ReleaseStatus-active rdf:type skos:Concept) are visible during
    # sh:class validation, resolving the concept-URI class constraints.
    validator = SHACLValidator(
        inference="rdfs",
        ont_path=VOCAB_FILE if VOCAB_FILE.exists() else None,
    )
    result = validator.validate_files(data_rdf, shapes_file)

    if result.conforms:
        print("  STATUS  : CONFORMS [OK]")
        print(f"  Violations: 0")
    else:
        print(f"  STATUS  : VIOLATIONS FOUND ({result.violation_count})")
        print()
        print(result.results_text[:1200])

    result.results_graph.serialize(str(report_path), format="turtle")
    print(f"\n  Report  : {report_path}")

    return result.conforms


# ── Entry point ───────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    default_input = _project_root / "data" / "samples" / "example_ord_combined.json"
    parser = argparse.ArgumentParser(
        description="ORD RDF Transformer — end-to-end pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=default_input,
        help="Path to the ORD JSON document (default: data/samples/example_ord_combined.json)",
    )
    parser.add_argument(
        "--force-shapes",
        action="store_true",
        default=False,
        help="Force Step 2 even if the shapes file is already up-to-date",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    data_file: Path = args.input

    # Derive output paths from the input stem
    stem        = data_file.stem                          # e.g. "example_ord_combined"
    data_rdf    = OUTPUT / f"{stem}.ttl"
    report_path = OUTPUT / f"{stem}_validation_report.ttl"

    print("\n" + "#" * 60)
    print("  ORD RDF TRANSFORMER - Pipeline")
    print("#" * 60)
    print(f"  Input    : {data_file}")
    print(f"  RDF out  : {data_rdf}")
    print(f"  Report   : {report_path}")
    shapes_in_use = SHAPES_PREBUILT if SHAPES_PREBUILT.exists() else SHAPES_GENERATED
    print(f"  Shapes   : {shapes_in_use}")

    step1_transform(data_file, data_rdf)
    step2_generate_shapes(force=args.force_shapes)
    conforms = step3_validate(data_rdf, report_path)

    _sep("PIPELINE SUMMARY")
    print(f"  Input      : {data_file}")
    print(f"  RDF output : {data_rdf}")
    print(f"  Shapes     : {shapes_in_use}")
    print(f"  Validation : {'CONFORMS' if conforms else 'VIOLATIONS FOUND'}")
    print(f"  Report     : {report_path}")
    print(f"\n{'=' * 60}\n")


if __name__ == "__main__":
    main()
