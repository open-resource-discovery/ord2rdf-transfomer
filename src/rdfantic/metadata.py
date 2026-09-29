"""RdfanticModelMetadata — inner-class configuration for RDFantic models."""

from __future__ import annotations

from typing import Callable, Optional, Set

from rdflib import URIRef


class RdfanticModelMetadata:
    """Configuration carrier for a :class:`RdfanticBaseModel` subclass.

    Declare it as a nested ``Meta`` class inside any :class:`RdfanticBaseModel`::

        class Package(RdfanticBaseModel):
            class Meta(RdfanticModelMetadata):
                name = "Package"
                class_uris = {ORD.Package}
                term_builder = lambda self: URIRef(f"https://example.org/{self.ord_id}")

    Attributes
    ----------
    name:
        Human-readable label used as the SHACL ``sh:name`` for the generated
        NodeShape.  Defaults to the empty string.
    class_uris:
        Set of ``rdf:type`` URIs asserted for every serialised instance.
        Must be overridden in each concrete model.
    term_builder:
        Callable ``(instance) -> URIRef`` that builds the subject node for an
        instance.  When *None*, a fresh ``rdflib.BNode`` is used.
    """

    name: str = ""
    class_uris: Set[URIRef] = set()
    term_builder: Optional[Callable] = None
