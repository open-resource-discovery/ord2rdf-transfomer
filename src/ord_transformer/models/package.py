"""Package model — groups ORD resources for distribution / ownership."""

from __future__ import annotations

from typing import Annotated, List, Optional

from pydantic import Field
from rdflib import XSD

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import ORD, ord_id_to_uri
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
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.shortDescription}),
        Field(alias="shortDescription", default=None, description="Plain-text short description"),
    ]
    description: Annotated[
        Optional[str],
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
        Optional[str],
        RdfanticFieldInfoMetaModel(
            predicates={ORD.vendor},
            uri_factory=ord_id_to_uri,
        ),
        Field(default=None, description="Vendor ORD ID"),
    ]
    license_type: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.licenseType}),
        Field(alias="licenseType", default=None, description="SPDX license identifier"),
    ]
    policy_level: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.policyLevel}),
        Field(alias="policyLevel", default=None),
    ]
    runtime_restriction: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.runtimeRestriction}),
        Field(alias="runtimeRestriction", default=None),
    ]
    support_info: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.supportInfo}),
        Field(alias="supportInfo", default=None),
    ]

    # ── ORDEntity shared properties ───────────────────────────────────────────

    local_id: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.localId}),
        Field(alias="localId", default=None, description="Local ID as known to the described system"),
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

    # ── Embedded collections ──────────────────────────────────────────────────

    package_links: Annotated[
        Optional[List[PackageLink]],
        RdfanticFieldInfoMetaModel(predicates={ORD.url}),
        Field(alias="packageLinks", default=None, description="Typed links specific to packages"),
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
