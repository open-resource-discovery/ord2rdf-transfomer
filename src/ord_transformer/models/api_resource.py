"""ApiResource model — describes an API endpoint exposed by a system."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, field_validator
from rdflib import XSD

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import (
    ORD,
    api_protocol_uri,
    implementation_standard_uri,
    industry_uri,
    lob_uri,
    ord_id_to_uri,
    policy_level_uri,
    release_status_uri,
    supported_use_case_uri,
    usage_uri,
    visibility_uri,
)
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

    Maps to ``ord:ApiResource`` (subclass of ``ord:ORDResource``).
    """

    class Meta(RdfanticModelMetadata):
        name = "ApiResource"
        class_uris = {ORD.ApiResource}
        term_builder = lambda self: ord_id_to_uri(self.ord_id)  # noqa: E731

    # ── Core identity ─────────────────────────────────────────────────────────

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
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.title}),
        Field(),
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
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.lastUpdate}, datatype=XSD.dateTime),
        Field(alias="lastUpdate", default=None, description="RFC 3339 date-time of last change"),
    ]
    deprecation_date: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.deprecationDate}, datatype=XSD.dateTime),
        Field(alias="deprecationDate", default=None),
    ]
    sunset_date: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.sunsetDate}, datatype=XSD.dateTime),
        Field(alias="sunsetDate", default=None),
    ]
    disabled: Annotated[
        bool | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.disabled}),
        Field(default=None),
    ]
    abstract: Annotated[
        bool | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.abstract}),
        Field(
            default=None, description="True if this resource is an abstract interface definition"
        ),
    ]
    responsible: Annotated[
        str | None,
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
        list[ConsumptionBundleReference] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.partOfConsumptionBundle}),
        Field(alias="partOfConsumptionBundles", default=None),
    ]
    default_consumption_bundle: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.defaultConsumptionBundle},
            uri_factory=ord_id_to_uri,
        ),
        Field(alias="defaultConsumptionBundle", default=None),
    ]

    # ── Protocol / technical ──────────────────────────────────────────────────

    api_protocol: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.apiProtocol}, uri_factory=api_protocol_uri),
        Field(
            alias="apiProtocol",
            default=None,
            description=(
                "rest | odata-v2 | odata-v4 | graphql | grpc | websocket | "
                "delta-sharing | sql | a2a | mcp | soap-inbound | soap-outbound | …"
            ),
        ),
    ]
    direction: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.direction}),
        Field(default=None, description="inbound | outbound | mixed"),
    ]
    implementation_standard: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.implementationStandard}, uri_factory=implementation_standard_uri
        ),
        Field(alias="implementationStandard", default=None),
    ]
    custom_implementation_standard: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.customImplementationStandard}),
        Field(alias="customImplementationStandard", default=None),
    ]
    custom_implementation_standard_description: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.customImplementationStandardDescription}),
        Field(alias="customImplementationStandardDescription", default=None),
    ]
    supported_use_cases: Annotated[
        list[str] | None,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.supportedUseCases}, uri_factory=supported_use_case_uri
        ),
        Field(
            alias="supportedUseCases",
            default=None,
            description="data-federation | snapshot | incremental | streaming | …",
        ),
    ]
    usage: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.usage}, uri_factory=usage_uri),
        Field(default=None, description="external | local"),
    ]
    entry_points: Annotated[
        list[str] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.baseUrl}),
        Field(alias="entryPoints", default=None),
    ]

    # ── Definitions / links ───────────────────────────────────────────────────

    resource_definitions: Annotated[
        list[ResourceDefinition] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.resourceDefinition}),
        Field(alias="resourceDefinitions", default=None),
    ]
    api_resource_links: Annotated[
        list[ApiEventResourceLink] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.url}),
        Field(
            alias="apiResourceLinks",
            default=None,
            description="Typed links specific to API resources",
        ),
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

    # ── Cross-resource relations ───────────────────────────────────────────────

    related_api_resources: Annotated[
        list[RelatedApiResource] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.relatedApiResources}),
        Field(alias="relatedApiResources", default=None),
    ]
    related_event_resources: Annotated[
        list[RelatedEventResource] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.relatedEventResources}),
        Field(alias="relatedEventResources", default=None),
    ]
    related_entity_types: Annotated[
        list[RelatedEntityType] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.relatedEntityType}),
        Field(alias="relatedEntityTypes", default=None),
    ]
    extensible: Annotated[
        bool | None,
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
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.aiHint}),
        Field(alias="aiHint", default=None),
    ]
    min_system_version: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.minSystemVersion}),
        Field(alias="minSystemVersion", default=None),
    ]
    policy_level: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.policyLevel}, uri_factory=policy_level_uri),
        Field(alias="policyLevel", default=None),
    ]
    line_of_business: Annotated[
        list[str] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.lineOfBusiness}, uri_factory=lob_uri),
        Field(alias="lineOfBusiness", default=None),
    ]
    industry: Annotated[
        list[str] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.industry}, uri_factory=industry_uri),
        Field(default=None),
    ]
