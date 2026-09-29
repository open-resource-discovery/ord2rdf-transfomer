"""Materialization context for resolving terms and creating URIs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from rdflib import URIRef

if TYPE_CHECKING:
    from rdfantic.internal.path_element import PathElement


class MaterializationContext(ABC):
    """Abstract base class for RDF term resolution and URI creation."""

    def resolve(self, value: Any) -> URIRef | Any:
        """Resolve a value to an RDF term if applicable."""
        from rdfantic.models.enums import RdfanticResolvableEnum  # noqa: PLC0415

        if isinstance(value, str):
            return self.resolve_term(value)
        if isinstance(value, RdfanticResolvableEnum):
            return value.rdf_term
        return value

    @abstractmethod
    def resolve_term(self, term: str) -> URIRef | str:
        """Resolve a string term to an RDF URI or return as-is."""
        ...

    @abstractmethod
    def create_uri(self, path: list[PathElement], identifier: str, element_type: str | None = None) -> URIRef:
        """Create a URI based on path elements, identifier, and optional element type."""
        ...
