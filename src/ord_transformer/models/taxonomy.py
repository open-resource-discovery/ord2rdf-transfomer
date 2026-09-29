"""Taxonomy models — Product, Group, GroupType, Tombstone.

These are ORD Taxonomy entities (subclasses of ``ord:ORDTaxonomy``) and
``ord:Tombstone`` for decommissioned resources.
"""

from __future__ import annotations

from typing import Annotated, List, Optional

from pydantic import AliasChoices, Field
from rdflib import XSD

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import ORD, ord_id_to_uri
from .base import ORDBaseModel


# ── Product ───────────────────────────────────────────────────────────────────

class Product(ORDBaseModel):
    """A commercial product or service in ORD's software portfolio taxonomy.

    Maps to ``ord:Product`` (subclass of ``ord:ORDTaxonomy``).
    """

    class Meta(RdfanticModelMetadata):
        name = "Product"
        class_uris = {ORD.Product}
        term_builder = lambda self: ord_id_to_uri(self.ord_id)  # noqa: E731

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="ordId"),
    ]
    local_id: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.localId}),
        Field(alias="localId", default=None),
    ]
    title: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.title}),
        Field(),
    ]
    short_description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.shortDescription}),
        Field(alias="shortDescription", default=None),
    ]
    description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None),
    ]
    vendor: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(
            predicates={ORD.vendor},
            uri_factory=ord_id_to_uri,
        ),
        Field(default=None),
    ]
    parent: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(
            predicates={ORD.parent},
            uri_factory=ord_id_to_uri,
        ),
        Field(default=None, description="ORD ID of parent Product for hierarchical structure"),
    ]
    correlation_ids: Annotated[
        Optional[List[str]],
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="correlationIds", default=None),
    ]


# ── Group ─────────────────────────────────────────────────────────────────────

class Group(ORDBaseModel):
    """A Group instance that resources can be assigned to.

    Maps to ``ord:Group`` (subclass of ``ord:ORDTaxonomy``).
    Introduced in ORD spec v1.9.
    """

    class Meta(RdfanticModelMetadata):
        name = "Group"
        class_uris = {ORD.Group}
        term_builder = lambda self: ord_id_to_uri(self.ord_id)  # noqa: E731

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(
            validation_alias=AliasChoices("groupId", "ordId"),
            serialization_alias="groupId",
            description="ORD ID of this Group (JSON key: groupId)",
        ),
    ]
    local_id: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.localId}),
        Field(alias="localId", default=None),
    ]
    title: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.title}),
        Field(),
    ]
    short_description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.shortDescription}),
        Field(alias="shortDescription", default=None),
    ]
    description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None),
    ]
    group_type_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.type},
            uri_factory=ord_id_to_uri,
        ),
        Field(alias="groupTypeId",
              description="ORD ID of the GroupType that defines the semantics of this Group"),
    ]


# ── GroupType ─────────────────────────────────────────────────────────────────

class GroupType(ORDBaseModel):
    """A GroupType defines the semantics of Group assignments.

    Maps to ``ord:GroupType`` (subclass of ``ord:ORDTaxonomy``).
    Introduced in ORD spec v1.9.
    """

    class Meta(RdfanticModelMetadata):
        name = "GroupType"
        class_uris = {ORD.GroupType}
        term_builder = lambda self: ord_id_to_uri(self.ord_id)  # noqa: E731

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(
            validation_alias=AliasChoices("groupTypeId", "ordId"),
            serialization_alias="groupTypeId",
            description="ORD ID of this GroupType (JSON key: groupTypeId)",
        ),
    ]
    local_id: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.localId}),
        Field(alias="localId", default=None),
    ]
    title: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.title}),
        Field(),
    ]
    short_description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.shortDescription}),
        Field(alias="shortDescription", default=None),
    ]
    description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None),
    ]


# ── Tombstone ─────────────────────────────────────────────────────────────────

class Tombstone(ORDBaseModel):
    """A Tombstone marks that a previously published ORD resource has been removed.

    Maps to ``ord:Tombstone`` (subclass of ``ord:Concept``).
    """

    class Meta(RdfanticModelMetadata):
        name = "Tombstone"
        class_uris = {ORD.Tombstone}
        term_builder = lambda self: ord_id_to_uri(
            self.ord_id or self.package_ord_id or self.api_resource_ord_id or "tombstone"
        )  # noqa: E731

    # Exactly ONE of the following ID fields must be set
    ord_id: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        RdfanticFieldInfoMetaModel(predicates={ORD.removedResource}, uri_factory=ord_id_to_uri),
        Field(alias="ordId", default=None,
              description="The ORD ID of the removed resource (for general resources)"),
    ]
    package_ord_id: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="packageOrdId", default=None,
              description="ORD ID of the removed Package"),
    ]
    api_resource_ord_id: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="apiResourceOrdId", default=None,
              description="ORD ID of the removed API Resource"),
    ]
    event_resource_ord_id: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="eventResourceOrdId", default=None,
              description="ORD ID of the removed Event Resource"),
    ]
    entity_type_ord_id: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="entityTypeOrdId", default=None,
              description="ORD ID of the removed Entity Type"),
    ]
    data_product_ord_id: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="dataProductOrdId", default=None,
              description="ORD ID of the removed Data Product"),
    ]
    removed_date: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.removedDate}, datatype=XSD.dateTime),
        Field(
            validation_alias=AliasChoices("removalDate", "removedDate"),
            serialization_alias="removedDate",
            default=None,
            description="RFC 3339 date-time when the resource was tombstoned",
        ),
    ]
    description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None),
    ]
