"""SHACL-specific materialization context for URI generation."""

from itertools import chain

from rdflib import URIRef

from rdfantic.context.base import MaterializationContext
from rdfantic.internal.path_element import PathElement
from rdfantic.shacl.uri_builder import ShaclUriBuilder


class ShaclMaterializationContext(MaterializationContext):
    """Materialization context that builds SHACL-compliant URIs."""

    base_uri: str
    strict: bool = False

    def __init__(self, base_uri: str, strict: bool = False):
        self.base_uri = base_uri
        self.strict = strict

    def resolve_term(self, term: str) -> URIRef | str:
        """Return the term as-is for SHACL contexts."""
        return term

    def create_uri(self, path: list[PathElement], identifier: str, element_type: str | None = None) -> URIRef:
        """Build a SHACL resource URI from path, identifier, and optional element type."""
        # Flatten the path elements
        path_ = list(chain.from_iterable(path))
        path_ += [element_type] if element_type else []
        return ShaclUriBuilder.create_shape_uri(self.base_uri, path_, identifier)
