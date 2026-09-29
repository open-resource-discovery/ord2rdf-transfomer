"""ApiResource model — describes an API endpoint exposed by a system."""

from __future__ import annotations

from typing import Annotated, List, Optional

from pydantic import Field, field_validator
from rdflib import XSD

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import ORD, ord_id_to_uri, release_status_uri, visibility_uri, api_protocol_uri, industry_uri, lob_uri
from .base import ORDBaseModel
from .supporting import (
    ApiEventResourceLink,
    ChangelogEntry,
    ConsumptionBundleReference,
    Link,
    RelatedApiResource,
    RelatedEntityType,
    RelatedEventResource,
    ResourceDefinition,
)


class ApiResource(ORDBaseModel):
    """An ORD API Resource describes a single API (REST, OData, SOAP, gRPC, etc.).

    Maps to ``ord:ApiResource`` (subclass of ``ord:ORDResource`` and ``ord:DataService``).
    """

    class Meta(RdfanticModelMetadata):
        name = "ApiResource"
        class_uris = {ORD.APIResource}
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
        Field(alias="releaseStatus", description="active | beta | deprecated | decommissioned"),
    ]
    visibility: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.visibility}, uri_factory=visibility_uri),
        Field(description="public | internal | private"),
    ]
    last_update: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.lastUpdate}, datatype=XSD.dateTime),
        Field(alias="lastUpdate", default=None, description="RFC 3339 date-time of last change"),
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
        Field(default=None, description="True if this resource is an abstract interface definition"),
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
        Field(alias="partOfPackage", description="ORD ID of the owning Package"),
    ]
    part_of_consumption_bundles: Annotated[
        Optional[List[ConsumptionBundleReference]],
        RdfanticFieldInfoMetaModel(predicates={ORD.partOfConsumptionBundle}),
        Field(alias="partOfConsumptionBundles", default=None),
    ]
    default_consumption_bundle: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(
            predicates={ORD.defaultConsumptionBundle},
            uri_factory=ord_id_to_uri,
        ),
        Field(alias="defaultConsumptionBundle", default=None),
    ]

    # ── Protocol / technical ──────────────────────────────────────────────────

    api_protocol: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.apiProtocol}, uri_factory=api_protocol_uri),
        Field(alias="apiProtocol", default=None,
              description="rest | odata-v2 | odata-v4 | soap | graphql | grpc | …"),
    ]
    direction: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.direction}),
        Field(default=None, description="inbound | outbound | mixed"),
    ]
    implementation_standard: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.implementationStandard}),
        Field(alias="implementationStandard", default=None),
    ]
    custom_implementation_standard: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.customImplementationStandard}),
        Field(alias="customImplementationStandard", default=None),
    ]
    custom_implementation_standard_description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.customImplementationStandardDescription}),
        Field(alias="customImplementationStandardDescription", default=None),
    ]
    supported_use_cases: Annotated[
        Optional[List[str]],
        RdfanticFieldInfoMetaModel(predicates={ORD.supportedUseCases}),
        Field(alias="supportedUseCases", default=None,
              description="data-federation | snapshot | incremental | streaming | …"),
    ]
    usage: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.usage}),
        Field(default=None, description="external | local"),
    ]
    entry_points: Annotated[
        Optional[List[str]],
        RdfanticFieldInfoMetaModel(predicates={ORD.baseUrl}),
        Field(alias="entryPoints", default=None),
    ]

    # ── Definitions / links ───────────────────────────────────────────────────

    resource_definitions: Annotated[
        Optional[List[ResourceDefinition]],
        RdfanticFieldInfoMetaModel(predicates={ORD.resourceDefinition}),
        Field(alias="resourceDefinitions", default=None),
    ]
    api_resource_links: Annotated[
        Optional[List[ApiEventResourceLink]],
        RdfanticFieldInfoMetaModel(predicates={ORD.url}),
        Field(alias="apiResourceLinks", default=None,
              description="Typed links specific to API resources"),
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

    # ── Cross-resource relations ───────────────────────────────────────────────

    related_api_resources: Annotated[
        Optional[List[RelatedApiResource]],
        RdfanticFieldInfoMetaModel(predicates={ORD.relatedApiResources}),
        Field(alias="relatedApiResources", default=None),
    ]
    related_event_resources: Annotated[
        Optional[List[RelatedEventResource]],
        RdfanticFieldInfoMetaModel(predicates={ORD.relatedEventResources}),
        Field(alias="relatedEventResources", default=None),
    ]
    related_entity_types: Annotated[
        Optional[List[RelatedEntityType]],
        RdfanticFieldInfoMetaModel(predicates={ORD.relatedEntityType}),
        Field(alias="relatedEntityTypes", default=None),
    ]
    extensible: Annotated[
        Optional[bool],
        RdfanticFieldInfoMetaModel(predicates={ORD.extensible}),
        Field(default=None),
    ]

    @field_validator("extensible", mode="before")
    @classmethod
    def _coerce_extensible(cls, v: object) -> object:
        """Convert ``{"supported": "..."}`` object to boolean.
        ``"no"`` → ``False``; ``"manual"`` / ``"automatic"`` → ``True``."""
        if isinstance(v, dict):
            return v.get("supported", "no") != "no"
        return v

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
