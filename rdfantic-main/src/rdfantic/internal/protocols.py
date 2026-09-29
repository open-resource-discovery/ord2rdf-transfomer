"""Protocol definitions for RDFantic."""

from typing import Protocol, runtime_checkable

from rdflib import Literal, URIRef


@runtime_checkable
class Resolvable(Protocol):
    """Protocol for objects that can be resolved to RDF terms."""

    @property
    def rdf_term(self) -> URIRef | Literal:
        """Get the RDF term representation of this object."""
        ...
