"""Agent model — an AI-powered autonomous system resource.

Maps to ``ord:Agent`` (subclass of ``ord:ORDResource``).
Introduced in ORD spec v1.14 (beta).
"""

from __future__ import annotations

from typing import Annotated, List, Optional

from pydantic import Field, field_validator
from rdflib import XSD

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import ORD, ord_id_to_uri, release_status_uri, visibility_uri, industry_uri, lob_uri
from .base import ORDBaseModel
from .supporting import (
    ApiEventResourceLink,
    ChangelogEntry,
    ConsumptionBundleReference,
    Link,
    RelatedEntityType,
    ResourceDefinition,
)


class Agent(ORDBaseModel):
    """An ORD Agent is an AI-powered autonomous system that can perform tasks,
    make decisions, and interact with users or other systems.

    Maps to ``ord:Agent`` (subclass of ``ord:ORDResource``).
    Introduced in ORD spec v1.14 (beta).
    """

    class Meta(RdfanticModelMetadata):
        name = "Agent"
        class_uris = {ORD.Agent}
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
    responsible: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.responsible}),
        Field(default=None),
    ]

    # ── Package / bundle membership ───────────────────────────────────────────

    part_of_package: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.partOfPackage},
            uri_factory=ord_id_to_uri,
        ),
        Field(alias="partOfPackage"),
    ]
    part_of_consumption_bundles: Annotated[
        Optional[List[ConsumptionBundleReference]],
        RdfanticFieldInfoMetaModel(predicates={ORD.partOfConsumptionBundle}),
        Field(alias="partOfConsumptionBundles", default=None),
    ]

    # ── Agent-specific ────────────────────────────────────────────────────────

    integration_dependencies: Annotated[
        Optional[List[str]],
        RdfanticFieldInfoMetaModel(
            predicates={ORD.integrationDependency},
            # uri_factory removed: stored as xsd:string ORD ID literals to
            # match the SHACL shape constraint (sh:datatype xsd:string).
        ),
        Field(alias="integrationDependencies", default=None,
              description="ORD IDs of IntegrationDependencies this agent relies on"),
    ]

    # ── Related resources ─────────────────────────────────────────────────────

    related_entity_types: Annotated[
        Optional[List[RelatedEntityType]],
        RdfanticFieldInfoMetaModel(predicates={ORD.relatedEntityType}),
        Field(alias="relatedEntityTypes", default=None),
    ]

    # ── Definitions / links ───────────────────────────────────────────────────

    resource_definitions: Annotated[
        Optional[List[ResourceDefinition]],
        RdfanticFieldInfoMetaModel(predicates={ORD.resourceDefinition}),
        Field(alias="resourceDefinitions", default=None),
    ]
    api_event_resource_links: Annotated[
        Optional[List[ApiEventResourceLink]],
        RdfanticFieldInfoMetaModel(predicates={ORD.url}),
        Field(alias="apiEventResourceLinks", default=None),
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
        RdfanticFieldInfoMetaModel(predicates={ORD.lineOfBusiness}, uri_factory=lob_uri),
        Field(alias="lineOfBusiness", default=None),
    ]
    industry: Annotated[
        Optional[List[str]],
        RdfanticFieldInfoMetaModel(predicates={ORD.industry}, uri_factory=industry_uri),
        Field(default=None),
    ]

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("related_entity_types", mode="before")
    @classmethod
    def _coerce_related_entity_types(cls, v: object) -> object:
        """Accept plain ORD ID strings as well as ``{"ordId": "..."}`` objects.

        The ORD spec allows ``relatedEntityTypes`` to be a list of bare ORD ID
        strings.  Normalise them to the dict shape that ``RelatedEntityType``
        expects so that both representations are handled transparently.
        """
        if isinstance(v, list):
            return [
                {"ordId": item} if isinstance(item, str) else item
                for item in v
            ]
        return v
