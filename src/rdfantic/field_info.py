"""RdfanticFieldInfoMetaModel — per-field RDF annotation metadata."""

from __future__ import annotations

from collections.abc import Callable

from rdflib import URIRef


class RdfanticFieldInfoMetaModel:
    """Metadata placed inside ``typing.Annotated`` to describe a field's RDF representation.

    Every annotated field may carry **one or more** of these objects; each one
    produces an independent set of triples during
    :meth:`~rdfantic.RdfanticBaseModel.model_dump_rdf`.

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
        predicates: set[URIRef],
        *,
        field_class_uris: set[URIRef] | None = None,
        datatype: URIRef | None = None,
        inverse_predicates: set[URIRef] | None = None,
        uri_factory: Callable[[str], URIRef] | None = None,
    ) -> None:
        if not predicates:
            raise ValueError("predicates must contain at least one URIRef")
        self.predicates: set[URIRef] = predicates
        self.field_class_uris: set[URIRef] = field_class_uris or set()
        self.datatype: URIRef | None = datatype
        self.inverse_predicates: set[URIRef] = inverse_predicates or set()
        self.uri_factory: Callable[[str], URIRef] | None = uri_factory

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"RdfanticFieldInfoMetaModel("
            f"predicates={self.predicates!r}, "
            f"datatype={self.datatype!r})"
        )
