"""ConsumptionBundle model — groups APIs for credential-based access."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import ORD, ord_id_to_uri
from .base import ORDBaseModel
from .supporting import ChangelogEntry, CredentialExchangeStrategy, Link


class ConsumptionBundle(ORDBaseModel):
    """An ORD Consumption Bundle groups API resources for credential exchange.

    Maps to ``ord:ConsumptionBundle`` (subclass of ``ord:ORDTaxonomy``).
    """

    class Meta(RdfanticModelMetadata):
        name = "ConsumptionBundle"
        class_uris = {ORD.ConsumptionBundle}
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

    # ── Governance ────────────────────────────────────────────────────────────

    policy_level: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.policyLevel}),
        Field(alias="policyLevel", default=None),
    ]
    credential_exchange_strategy: Annotated[
        list[CredentialExchangeStrategy] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.credentialExchangeStrategy}),
        Field(
            alias="credentialExchangeStrategies",
            default=None,
            description="Supported credential exchange strategies",
        ),
    ]

    # ── Embedded ──────────────────────────────────────────────────────────────

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
