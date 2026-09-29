"""Enum models for RDF term resolution."""

from abc import abstractmethod
from enum import Enum

from rdflib import Literal, URIRef


class RdfanticResolvableEnum(Enum):
    """Enum that can be resolved to an RDF term.

    Implements the Resolvable protocol without inheriting from it
    to avoid metaclass conflicts between Enum and Protocol.
    """

    @property
    @abstractmethod
    def rdf_term(self) -> URIRef | Literal:
        """Get the RDF term representation of this enum value."""
        ...


class RdfanticLiteralEnum(RdfanticResolvableEnum):
    """Enum that resolves to RDF Literals."""

    @property
    def datatype(self) -> str | None:
        """Get the RDF datatype for this literal enum value."""
        return None

    @property
    def rdf_term(self) -> URIRef | Literal:
        """Get the RDF literal representation of this enum value."""
        if datatype := self.datatype:
            return Literal(self.value, datatype=datatype)
        return Literal(self.value)
