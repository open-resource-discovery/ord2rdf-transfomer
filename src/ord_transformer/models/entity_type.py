"""EntityType model — describes a business entity / domain aggregate."""

from __future__ import annotations

from typing import Annotated, List, Optional

from pydantic import Field
from rdflib import XSD

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import ORD, ord_id_to_uri, release_status_uri, visibility_uri
from .base import ORDBaseModel
from .supporting import ChangelogEntry, Link, RelatedCapability, RelatedEntityType, ResourceDefinition


class EntityType(ORDBaseModel):
    """An ORD Entity Type classifies domain entities that share common characteristics.

    Maps to ``ord:OrdEntityType`` (subclass of ``ord:ORDResource``).
    """

    class Meta(RdfanticModelMetadata):
        name = "EntityType"
        class_uris = {ORD.OrdEntityType}
        term_builder = lambda self: ord_id_to_uri(self.ord_id)  # noqa: E731

    # ── Core identity ─────────────────────────────────────────────────────────

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
    version: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.version}),
        Field(),
    ]

    # ── Lifecycle / visibility ────────────────────────────────────────────────

    release_status: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.releaseStatus}, uri_factory=release_status_uri),
        Field(alias="releaseStatus"),
    ]
    visibility: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.visibility}, uri_factory=visibility_uri),
        Field(),
    ]
    last_update: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.lastUpdate}, datatype=XSD.dateTime),
        Field(alias="lastUpdate", default=None),
    ]
    deprecation_date: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.deprecationDate}, datatype=XSD.dateTime),
        Field(alias="deprecationDate", default=None),
    ]
    sunset_date: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.sunsetDate}, datatype=XSD.dateTime),
        Field(alias="sunsetDate", default=None),
    ]
    disabled: Annotated[
        Optional[bool],
        RdfanticFieldInfoMetaModel(predicates={ORD.disabled}),
        Field(default=None),
    ]
    abstract: Annotated[
        Optional[bool],
        RdfanticFieldInfoMetaModel(predicates={ORD.abstract}),
        Field(default=None),
    ]
    responsible: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.responsible}),
        Field(default=None),
    ]

    # ── Package membership ────────────────────────────────────────────────────

    part_of_package: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.partOfPackage},
            uri_factory=ord_id_to_uri,
        ),
        Field(alias="partOfPackage"),
    ]

    # ── DDD level ─────────────────────────────────────────────────────────────

    level: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.level}),
        Field(default=None, description="DDD aggregate level: aggregate | sub-entity | …"),
    ]

    # ── Cross-resource relations ───────────────────────────────────────────────

    related_entity_types: Annotated[
        Optional[List[RelatedEntityType]],
        RdfanticFieldInfoMetaModel(predicates={ORD.relatedEntityType}),
        Field(alias="relatedEntityTypes", default=None),
    ]
    related_capabilities: Annotated[
        Optional[List[RelatedCapability]],
        RdfanticFieldInfoMetaModel(predicates={ORD.relatedCapabilities}),
        Field(alias="relatedCapabilities", default=None),
    ]

    # ── Definitions / links ───────────────────────────────────────────────────

    resource_definitions: Annotated[
        Optional[List[ResourceDefinition]],
        RdfanticFieldInfoMetaModel(predicates={ORD.resourceDefinition}),
        Field(alias="resourceDefinitions", default=None),
    ]
    links: Annotated[
        Optional[List[Link]],
        RdfanticFieldInfoMetaModel(predicates={ORD.link}),
        Field(default=None),
    ]
    changelog_entries: Annotated[
        Optional[List[ChangelogEntry]],
        RdfanticFieldInfoMetaModel(predicates={ORD.changelogEntry}),
        Field(alias="changelogEntries", default=None),
    ]

    # ── Metadata ──────────────────────────────────────────────────────────────

    ai_hint: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.aiHint}),
        Field(alias="aiHint", default=None),
    ]
    min_system_version: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.minSystemVersion}),
        Field(alias="minSystemVersion", default=None),
    ]
    policy_level: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.policyLevel}),
        Field(alias="policyLevel", default=None),
    ]
    line_of_business: Annotated[
        Optional[List[str]],
        RdfanticFieldInfoMetaModel(predicates={ORD.lineOfBusiness}),
        Field(alias="lineOfBusiness", default=None),
    ]
    industry: Annotated[
        Optional[List[str]],
        RdfanticFieldInfoMetaModel(predicates={ORD.industry}),
        Field(default=None),
    ]
