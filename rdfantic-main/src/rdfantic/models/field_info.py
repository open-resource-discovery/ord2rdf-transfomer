"""Field information and metadata for RDFantic models using Pydantic v2 Annotated pattern.

This module uses Pydantic v2's recommended approach with `typing.Annotated` to attach
RDF metadata to model fields, avoiding subclassing FieldInfo which is marked as final.

The RdfanticFieldInfoMetaModel is implemented as a dataclass rather than a Pydantic
BaseModel because Pydantic treats BaseModel instances in Annotated as type validators,
which conflicts with our use of them as metadata markers.
"""

import warnings
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any, get_args

from pydantic import BaseModel, fields
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from rdflib import URIRef


@dataclass
class RdfanticFieldInfoMetaModel:
    """Metadata model for RDFantic field information.

    This dataclass is used with typing.Annotated to attach RDF metadata to Pydantic fields.
    It is implemented as a dataclass (not a Pydantic BaseModel) so that Pydantic treats
    it as opaque metadata rather than a type validator.

    Attributes
    ----------
    predicates : set[URIRef]
        Set of RDF predicates this field maps to.
    str_term_builder : Callable[[BaseModel, str], URIRef] | None
        Optional callable to build URI terms from string values. Receives the
        owning model instance and the string value as inputs, allowing the
        builder to derive URIs based on sibling field values.
    datatype : str | None
        Optional XSD datatype URI for literal values.
    rdf_list : bool
        Whether to serialize this field as an RDF list (rdf:List).
    inverse : bool
        Whether the relationship is an inverse (incoming) relationship. When True,
        triples are created with the field value as subject and the parent instance
        as object, reversing the normal direction. Only valid for URI references
        (URIRef) or nested RdfanticBaseModel instances.
    class_uris : set[URIRef]
        Optional set of RDF class URIs to assert as rdf:type on the field's value node.
        Only applicable when the field value serializes to an IdentifiedNode (URIRef or
        BNode), not for Literal values. During serialization, each URI in this set will
        generate a triple: (field_value_node, rdf:type, class_uri).

    Example
    -------
    >>> from typing import Annotated
    >>> from pydantic import Field
    >>> from rdflib import URIRef
    >>>
    >>> # Standard (outgoing) relationship
    >>> name: Annotated[
    ...     str,
    ...     RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/name")}),
    ...     Field(description="Person's name")
    ... ]
    >>>
    >>> # Inverse (incoming) relationship
    >>> known_by: Annotated[
    ...     list[str],
    ...     RdfanticFieldInfoMetaModel(
    ...         predicates={URIRef("http://example.org/knows")},
    ...         inverse=True,
    ...         str_term_builder=lambda model, name: URIRef(f"http://example.org/Person/{name}")
    ...     ),
    ...     Field(description="People who know this person")
    ... ]
    >>>
    >>> # Field with class_uris to type the referenced node
    >>> author: Annotated[
    ...     str,
    ...     RdfanticFieldInfoMetaModel(
    ...         predicates={URIRef("http://example.org/author")},
    ...         str_term_builder=lambda model, name: URIRef(f"http://example.org/Person/{name}"),
    ...         class_uris={URIRef("http://example.org/Person")}
    ...     ),
    ...     Field(description="The author, typed as Person")
    ... ]
    """

    predicates: set[URIRef] = dataclass_field(default_factory=set)
    str_term_builder: Callable[[BaseModel, str], URIRef] | None = None
    datatype: str | None = None
    rdf_list: bool = False
    inverse: bool = False
    class_uris: set[URIRef] = dataclass_field(default_factory=set)


def get_rdfantic_metadata(field_info: FieldInfo) -> list[RdfanticFieldInfoMetaModel]:
    """Extract all RdfanticFieldInfoMetaModel instances from a Pydantic FieldInfo's metadata.

    Searches through the field's metadata list (populated by typing.Annotated) to find
    all instances of RdfanticFieldInfoMetaModel.

    Parameters
    ----------
    field_info : FieldInfo
        The Pydantic FieldInfo to extract metadata from.

    Returns
    -------
    list[RdfanticFieldInfoMetaModel]
        List of RDFantic metadata instances found in the annotation. Returns empty list
        if none are found.
    """
    if isinstance(field_info, RdfanticFieldInfo):
        return [field_info.rdfantic_metadata]

    if not field_info.metadata:
        return []

    result = []
    for item in field_info.metadata:
        if isinstance(item, RdfanticFieldInfoMetaModel):
            result.append(item)

    return result


def extract_rdfantic_metadata_from_annotation(annotation: Any) -> list[RdfanticFieldInfoMetaModel]:
    """Extract all RdfanticFieldInfoMetaModel instances directly from a type annotation.

    This function inspects Annotated type hints to find RdfanticFieldInfoMetaModel instances.

    Parameters
    ----------
    annotation : Any
        The type annotation to inspect (typically from __annotations__).

    Returns
    -------
    list[RdfanticFieldInfoMetaModel]
        List of RDFantic metadata instances found in the Annotated args. Returns empty list
        if none are found.
    """
    try:
        args = get_args(annotation)
        if not args:
            return []

        result = []
        # First arg is the actual type, rest are metadata
        for arg in args[1:]:
            if isinstance(arg, RdfanticFieldInfoMetaModel):
                result.append(arg)
        return result
    except (AttributeError, TypeError):
        # AttributeError: annotation is not subscriptable (not Annotated)
        # TypeError: annotation type doesn't support get_args()
        pass

    return []


class RdfanticFieldInfo(fields.FieldInfo):
    """Legacy FieldInfo subclass kept for backward compatibility.

    .. deprecated::
        Subclassing Pydantic's `FieldInfo` is discouraged in Pydantic v2.
        New code should use the `Annotated` pattern with
        :class:`RdfanticFieldInfoMetaModel`. See the README for migration details.

    Stores RDFantic metadata directly on the FieldInfo instance so that
    :func:`get_rdfantic_metadata` can recognize fields produced by the legacy
    :func:`field` helper.
    """

    __slots__ = ("_rdfantic_metadata",)

    def __init__(self, metadata: dict[str, Any] | None, **kwargs: Any):
        super().__init__(**kwargs)
        self._rdfantic_metadata = RdfanticFieldInfoMetaModel(**(metadata or {}))

    @property
    def rdfantic_metadata(self) -> RdfanticFieldInfoMetaModel:
        """Return the RDFantic metadata attached to this field."""
        return self._rdfantic_metadata


def field(
    default: Any = PydanticUndefined,
    *,
    metadata: dict[str, Any] | None = None,
    default_factory: Callable[[], Any] | None = None,
    **kwargs: Any,
) -> RdfanticFieldInfo:
    """Create a legacy RDFantic field with attached metadata.

    .. deprecated::
        Use the `Annotated` pattern with :class:`RdfanticFieldInfoMetaModel`
        instead. This helper is kept only so that older models continue to work
        while they are migrated. See the README for migration details.

    Parameters
    ----------
    default : Any, optional
        Default value for the field.
    metadata : dict[str, Any] | None, optional
        Mapping of RDFantic metadata fields (predicate, datatype, term_builder,
        rdf_list) used to construct a :class:`RdfanticFieldInfoMetaModel`.
    default_factory : Callable[[], Any] | None, optional
        Factory function for default values.
    **kwargs : Any
        Additional Pydantic field arguments forwarded to `FieldInfo`.

    Returns
    -------
    RdfanticFieldInfo
        A FieldInfo subclass instance carrying the RDFantic metadata.
    """
    warnings.warn(
        "field() is deprecated. Use the Annotated pattern with RdfanticFieldInfoMetaModel instead. "
        "See the README for migration details.",
        DeprecationWarning,
        stacklevel=2,
    )
    return RdfanticFieldInfo(metadata=metadata, default=default, default_factory=default_factory, **kwargs)
