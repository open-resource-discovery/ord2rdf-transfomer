"""Overlay model — a versioned metadata patch document for resource definitions.

Maps to ``ord:Overlay`` (subclass of ``ord:ORDResource``).
Introduced in ORD spec v1.15 (alpha).
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field
from rdflib import XSD

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import ORD, ord_id_to_uri, release_status_uri, visibility_uri
from .base import ORDBaseModel
from .supporting import ChangelogEntry, Link, ResourceDefinition


class Overlay(ORDBaseModel):
    """An ORD Overlay is a standalone versioned resource that references a metadata
    patch document enriching resource definitions without modifying the originals.

    Maps to ``ord:Overlay`` (subclass of ``ord:ORDResource``).
    Introduced in ORD spec v1.15 (alpha).
    """

    class Meta(RdfanticModelMetadata):
        name = "Overlay"
        class_uris = {ORD.Overlay}
        term_builder = lambda self: ord_id_to_uri(self.ord_id)  # noqa: E731

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="ordId"),
    ]
    local_id: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.localId}),
        Field(alias="localId", default=None),
    ]
    title: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.title}),
        Field(default=None),
    ]
    short_description: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.shortDescription}),
        Field(alias="shortDescription", default=None),
    ]
    description: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None),
    ]
    version: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.version}),
        Field(),
    ]
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
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.lastUpdate}, datatype=XSD.dateTime),
        Field(alias="lastUpdate", default=None),
    ]
    part_of_package: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.partOfPackage},
            uri_factory=ord_id_to_uri,
        ),
        Field(alias="partOfPackage", default=None),
    ]
    resource_definitions: Annotated[
        list[ResourceDefinition] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.resourceDefinition}),
        Field(alias="resourceDefinitions", default=None),
    ]
    links: Annotated[
        list[Link] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.link}),
        Field(default=None),
    ]
    changelog_entries: Annotated[
        list[ChangelogEntry] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.changelogEntry}),
        Field(alias="changelogEntries", default=None),
    ]
    policy_level: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.policyLevel}),
        Field(alias="policyLevel", default=None),
    ]
    line_of_business: Annotated[
        list[str] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.lineOfBusiness}),
        Field(alias="lineOfBusiness", default=None),
    ]
    industry: Annotated[
        list[str] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.industry}),
        Field(default=None),
    ]
