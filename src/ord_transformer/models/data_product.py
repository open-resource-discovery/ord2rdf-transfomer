"""DataProduct model — a curated, versioned, self-describing data asset.

Maps to ``ord:DataProduct`` (subclass of ``ord:ORDResource``).
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, field_validator
from rdflib import XSD

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import (
    ORD,
    industry_uri,
    lob_uri,
    ord_id_to_uri,
    release_status_uri,
    visibility_uri,
)
from .base import ORDBaseModel
from .supporting import (
    ChangelogEntry,
    ConsumptionBundleReference,
    DataProductInputPort,
    DataProductLink,
    DataProductOutputPort,
    Link,
    RelatedEntityType,
)


class DataProduct(ORDBaseModel):
    """An ORD Data Product is a curated, versioned, self-describing data asset.

    Maps to ``ord:DataProduct`` (subclass of ``ord:ORDResource``).
    Introduced in ORD spec v1.0.
    """

    class Meta(RdfanticModelMetadata):
        name = "DataProduct"
        class_uris = {ORD.DataProduct}
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
    responsible: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.responsible}),
        Field(default=None),
    ]

    # ── Data product classification ───────────────────────────────────────────

    type: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.type}),
        Field(default=None, description="base-object | primary-source | derived | …"),
    ]
    category: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.category}),
        Field(default=None, description="business-object | analytical | …"),
    ]
    lifecycle_status: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.lifecycleStatus}),
        Field(
            alias="lifecycleStatus",
            default=None,
            description="Runtime lifecycle status: running | provisioning | …",
        ),
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

    # ── Data ports ────────────────────────────────────────────────────────────

    input_ports: Annotated[
        list[DataProductInputPort] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.inputPort}),
        Field(
            alias="inputPorts", default=None, description="Input data sources for this data product"
        ),
    ]
    output_ports: Annotated[
        list[DataProductOutputPort] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.outputPort}),
        Field(
            alias="outputPorts",
            default=None,
            description="Output ports exposing this data product's data",
        ),
    ]

    # ── Cross-resource relations ───────────────────────────────────────────────

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
        """Convert ``{"supported": "..."}`` object to boolean."""
        if isinstance(v, dict):
            return v.get("supported", "no") != "no"
        return v

    # ── Links / changelog ─────────────────────────────────────────────────────

    data_product_links: Annotated[
        list[DataProductLink] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.url}),
        Field(alias="dataProductLinks", default=None),
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
        RdfanticFieldInfoMetaModel(predicates={ORD.policyLevel}),
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
