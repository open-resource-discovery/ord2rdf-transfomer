"""RdfanticFieldInfoMetaModel — per-field RDF annotation metadata."""

from __future__ import annotations

from typing import Callable, Optional, Set

from rdflib import URIRef


class RdfanticFieldInfoMetaModel:
    """Metadata placed inside ``typing.Annotated`` to describe a field's RDF representation.

    Every annotated field may carry **one or more** of these objects; each one
    produces an independent set of triples during :meth:`~rdfantic.RdfanticBaseModel.model_dump_rdf`.

    Parameters
    ----------
    predicates:
        One or more RDF property URIs that relate the subject node to this
        field's value.  At least one is required.
    field_class_uris:
        Optional ``rdf:type`` assertions added to the *object* node when the
        value is resolved as a URI reference (not a literal).
    datatype:
        Explicit XSD datatype URI for the emitted literal.  When *None*, the
        datatype is inferred from the Python type (``str → xsd:string``,
        ``bool → xsd:boolean``, etc.).
    inverse_predicates:
        Additional triples emitted *from* the object node *to* the subject
        node — i.e. the inverse relationship direction.
    uri_factory:
        When provided, a plain Python *string* value is first passed through
        this callable to produce a ``URIRef`` (object node), rather than being
        emitted as a literal.  Typical use: converting an ORD ID string like
        ``"sap.example:package:Foo:v1"`` to a proper resource URI.

    Examples
    --------
    >>> from rdflib import URIRef, XSD
    >>> meta = RdfanticFieldInfoMetaModel(
    ...     predicates={URIRef("https://example.org/name")},
    ...     datatype=XSD.string,
    ... )
    """

    __slots__ = (
        "predicates",
        "field_class_uris",
        "datatype",
        "inverse_predicates",
        "uri_factory",
    )

    def __init__(
        self,
        predicates: Set[URIRef],
        *,
        field_class_uris: Optional[Set[URIRef]] = None,
        datatype: Optional[URIRef] = None,
        inverse_predicates: Optional[Set[URIRef]] = None,
        uri_factory: Optional[Callable[[str], URIRef]] = None,
    ) -> None:
        if not predicates:
            raise ValueError("predicates must contain at least one URIRef")
        self.predicates: Set[URIRef] = predicates
        self.field_class_uris: Set[URIRef] = field_class_uris or set()
        self.datatype: Optional[URIRef] = datatype
        self.inverse_predicates: Set[URIRef] = inverse_predicates or set()
        self.uri_factory: Optional[Callable[[str], URIRef]] = uri_factory

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RdfanticFieldInfoMetaModel("
            f"predicates={self.predicates!r}, "
            f"datatype={self.datatype!r})"
        )
