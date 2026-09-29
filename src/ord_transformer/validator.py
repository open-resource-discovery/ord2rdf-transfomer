"""SHACLValidator — validate an RDF graph against SHACL shapes using pyshacl."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rdflib import Graph

from .exceptions import SHACLValidationError


@dataclass
class ValidationResult:
    """Result of a SHACL validation run.

    Attributes
    ----------
    conforms:
        ``True`` if the data graph fully satisfies all shape constraints.
    results_graph:
        The SHACL validation report graph (``sh:ValidationReport``).
    results_text:
        Human-readable summary produced by ``pyshacl``.
    violation_count:
        Number of ``sh:Violation`` results in the report (0 when *conforms*
        is ``True``).
    """

    conforms: bool
    results_graph: Graph
    results_text: str

    @property
    def violation_count(self) -> int:
        """Count of sh:Violation severity results in the validation report.

        SHACL violations are represented as ``sh:ValidationResult`` nodes that
        carry ``sh:resultSeverity sh:Violation``.
        """
        from rdflib.namespace import SH

        return sum(
            1
            for _ in self.results_graph.subjects(
                predicate=SH.resultSeverity,
                object=SH.Violation,
            )
        )

    def __str__(self) -> str:
        status = "CONFORMS" if self.conforms else f"VIOLATIONS ({self.violation_count})"
        return f"ValidationResult({status})"


class SHACLValidator:
    """Validates an ``rdflib.Graph`` against SHACL shape constraints.

    Wraps ``pyshacl.validate`` with sensible defaults and a clean result
    object.

    Parameters
    ----------
    inference:
        RDFS inference mode passed to pyshacl: ``"rdfs"``, ``"owlrl"``,
        ``"both"``, or ``"none"``.  Defaults to ``"rdfs"``.
    abort_on_first:
        If ``True``, stop validation after the first violation.
    allow_infos:
        Include ``sh:Info`` results in the report.
    allow_warnings:
        Include ``sh:Warning`` results in the report.

    Examples
    --------
    .. code-block:: python

        validator = SHACLValidator()
        result = validator.validate(data_graph, shapes_graph)
        if not result.conforms:
            print(result.results_text)
    """

    def __init__(
        self,
        inference: str = "rdfs",
        abort_on_first: bool = False,
        allow_infos: bool = False,
        allow_warnings: bool = False,
        ont_path: Optional[str | Path] = None,
    ) -> None:
        self.inference = inference
        self.abort_on_first = abort_on_first
        self.allow_infos = allow_infos
        self.allow_warnings = allow_warnings
        self.ont_path = Path(ont_path) if ont_path else None

    # ------------------------------------------------------------------
    # Core validation
    # ------------------------------------------------------------------

    def validate(
        self,
        data_graph: Graph,
        shapes_graph: Graph,
    ) -> ValidationResult:
        """Validate *data_graph* against *shapes_graph*.

        Parameters
        ----------
        data_graph:
            The RDF graph to validate (e.g. the output of
            :class:`~ord_transformer.transformer.ORDTransformer`).
        shapes_graph:
            The SHACL shapes graph (e.g. from
            :func:`~ord_transformer.shacl_generator.generate_combined_shapes`).

        Returns
        -------
        ValidationResult

        Raises
        ------
        SHACLValidationError
            If pyshacl itself raises an unexpected error.
        """
        try:
            import pyshacl  # lazy import — only required at validation time
        except ImportError as exc:
            raise SHACLValidationError(
                "pyshacl is required for SHACL validation: pip install pyshacl"
            ) from exc

        # Load ontology graph (e.g. the ORD vocabulary) when configured.
        # This makes SKOS concept definitions visible during validation so that
        # sh:class skos:Concept constraints can resolve correctly.
        ont_graph: Graph | None = None
        if self.ont_path and self.ont_path.exists():
            ont_graph = Graph()
            ont_graph.parse(str(self.ont_path), format="turtle")

        try:
            conforms, results_graph, results_text = pyshacl.validate(
                data_graph,
                shacl_graph=shapes_graph,
                ont_graph=ont_graph,
                inference=self.inference,
                abort_on_first=self.abort_on_first,
                allow_infos=self.allow_infos,
                allow_warnings=self.allow_warnings,
                meta_shacl=False,
                debug=False,
            )
        except Exception as exc:
            raise SHACLValidationError(f"pyshacl validation error: {exc}") from exc

        return ValidationResult(
            conforms=conforms,
            results_graph=results_graph,
            results_text=results_text,
        )

    # ------------------------------------------------------------------
    # Convenience: validate files directly
    # ------------------------------------------------------------------

    def validate_files(
        self,
        data_path: str | Path,
        shapes_path: str | Path,
        data_fmt: str = "turtle",
        shapes_fmt: str = "turtle",
    ) -> ValidationResult:
        """Load graphs from disk and validate.

        Parameters
        ----------
        data_path:
            Path to the RDF data file.
        shapes_path:
            Path to the SHACL shapes file.
        data_fmt / shapes_fmt:
            rdflib parse format for each file (default ``"turtle"``).

        Returns
        -------
        ValidationResult
        """
        data_graph = Graph()
        data_graph.parse(str(data_path), format=data_fmt)

        shapes_graph = Graph()
        shapes_graph.parse(str(shapes_path), format=shapes_fmt)

        return self.validate(data_graph, shapes_graph)
