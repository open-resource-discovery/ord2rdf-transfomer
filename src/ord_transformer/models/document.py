"""ORD Document model — the top-level ORD metadata carrier."""

from __future__ import annotations

from typing import Annotated, Optional

from pydantic import Field
from rdflib import BNode, URIRef, XSD

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import ORD, ord_id_to_uri
from .base import ORDBaseModel


# ── Inline system-context reference models ────────────────────────────────────

class SystemType(ORDBaseModel):
    """Inline reference to the SystemType described by this document.

    Maps to ``ord:SystemType``. Serialised as a blank node.
    """

    class Meta(RdfanticModelMetadata):
        name = "SystemType"
        class_uris = {ORD.SystemType}
        term_builder = lambda self: BNode()  # noqa: E731

    system_namespace: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.systemNamespace}),
        Field(alias="systemNamespace",
              description="Unique namespace that identifies the system type"),
    ]


class SystemVersion(ORDBaseModel):
    """Inline reference to the SystemVersion described by this document.

    Maps to ``ord:SystemVersion``. Serialised as a blank node.
    """

    class Meta(RdfanticModelMetadata):
        name = "SystemVersion"
        class_uris = {ORD.SystemVersion}
        term_builder = lambda self: BNode()  # noqa: E731

    version: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.version}),
        Field(description="Design-time version of the system type, e.g. '1.0.0'"),
    ]


class SystemInstance(ORDBaseModel):
    """Inline reference to the SystemInstance described by this document.

    Maps to ``ord:SystemInstance``. Serialised as a blank node.
    """

    class Meta(RdfanticModelMetadata):
        name = "SystemInstance"
        class_uris = {ORD.SystemInstance}
        term_builder = lambda self: BNode()  # noqa: E731

    base_url: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.baseUrl}, datatype=XSD.anyURI),
        Field(alias="baseUrl", default=None,
              description="Base URL of the running system instance"),
    ]


# ── Top-level document model ──────────────────────────────────────────────────

class OrdDocument(ORDBaseModel):
    """The top-level ORD document that carries document-level metadata.

    In RDF, the document is identified by its ``baseUrl`` (if provided) or a
    BNode.  All contained resources (packages, APIs, etc.) are serialised
    separately and linked via their own ORD IDs.

    Maps to ``ord:Document``.
    """

    class Meta(RdfanticModelMetadata):
        name = "OrdDocument"
        class_uris = {ORD.Document}

        @staticmethod
        def term_builder(self: "OrdDocument") -> URIRef:  # type: ignore[override]
            if self.base_url:
                return URIRef(self.base_url)
            return URIRef(f"urn:ord:document:{id(self)}")

    open_resource_discovery: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.openResourceDiscovery}),
        Field(
            alias="openResourceDiscovery",
            description="ORD spec version this document conforms to, e.g. '1.9'",
        ),
    ]
    base_url: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.baseUrl}, datatype=XSD.anyURI),
        Field(alias="baseUrl", default=None, description="Base URL of the described system instance"),
    ]
    policy_level: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.policyLevel}),
        Field(alias="policyLevel", default=None),
    ]
    description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None),
    ]
    perspective: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.perspective}),
        Field(default=None,
              description="Document perspective: system-type | system-version | system-instance"),
    ]
    described_system_type: Annotated[
        Optional[SystemType],
        RdfanticFieldInfoMetaModel(predicates={ORD.describedSystemType}),
        Field(alias="describedSystemType", default=None,
              description="Inline SystemType object identifying the described system type"),
    ]
    described_system_version: Annotated[
        Optional[SystemVersion],
        RdfanticFieldInfoMetaModel(predicates={ORD.describedSystemVersion}),
        Field(alias="describedSystemVersion", default=None,
              description="Inline SystemVersion object with the design-time version"),
    ]
    described_system_instance: Annotated[
        Optional[SystemInstance],
        RdfanticFieldInfoMetaModel(predicates={ORD.describedSystemInstance}),
        Field(alias="describedSystemInstance", default=None,
              description="Inline SystemInstance object for the described running instance"),
    ]
