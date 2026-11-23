"""Package model — groups ORD resources for distribution / ownership."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import ORD, ord_id_to_uri, policy_level_uri
from .base import ORDBaseModel
from .supporting import ChangelogEntry, Link, PackageLink


class Package(ORDBaseModel):
    """An ORD Package groups resources for distribution and ownership tracking.

    Maps to ``ord:Package`` (subclass of ``ord:ORDTaxonomy``).
    """

    class Meta(RdfanticModelMetadata):
        name = "Package"
        class_uris = {ORD.Package}
        term_builder = lambda self: ord_id_to_uri(self.ord_id)  # noqa: E731

    # ── Core identity ─────────────────────────────────────────────────────────

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="ordId", description="Stable globally-unique ORD ID"),
    ]
    title: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.title}),
        Field(description="Human-readable package title (≤ 255 chars)"),
    ]
    short_description: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.shortDescription}),
        Field(alias="shortDescription", default=None, description="Plain-text short description"),
    ]
    description: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None, description="CommonMark description"),
    ]
    version: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.version}),
        Field(description="SemVer version string"),
    ]

    # ── Ownership / governance ────────────────────────────────────────────────

    vendor: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.vendor},
            uri_factory=ord_id_to_uri,
        ),
        Field(default=None, description="Vendor ORD ID"),
    ]
    license_type: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.licenseType}),
        Field(alias="licenseType", default=None, description="SPDX license identifier"),
    ]
    policy_level: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.policyLevel}, uri_factory=policy_level_uri),
        Field(alias="policyLevel", default=None),
    ]
    runtime_restriction: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.runtimeRestriction}),
        Field(alias="runtimeRestriction", default=None),
    ]
    support_info: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.supportInfo}),
        Field(alias="supportInfo", default=None),
    ]

    # ── ORDEntity shared properties ───────────────────────────────────────────

    local_id: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.localId}),
        Field(
            alias="localId", default=None, description="Local ID as known to the described system"
        ),
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

    # ── Embedded collections ──────────────────────────────────────────────────

    package_links: Annotated[
        list[PackageLink] | None,
        RdfanticFieldInfoMetaModel(predicates={ORD.url}),
        Field(alias="packageLinks", default=None, description="Typed links specific to packages"),
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
