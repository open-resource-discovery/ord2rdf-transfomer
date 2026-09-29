"""Supporting / embedded ORD entity models.

Covers resource definitions, typed links, changelog entries, consumption-bundle
references, credential exchange strategies, extensibility markers, and typed
resource-reference objects (RelatedApiResource, RelatedEntityType, etc.).
"""

from __future__ import annotations

from typing import Annotated, List, Optional

from pydantic import Field
from rdflib import BNode, URIRef, XSD

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata
from rdfantic.context import ShaclMaterializationContext

from ..namespaces import ORD, definition_type_uri, link_type_uri, ord_id_to_uri, release_status_uri
from .base import ORDBaseModel


def _resolve_definition_uri(url: str, system_base_url: str | None) -> URIRef:
    """Resolve a resource-definition URL to an absolute IRI.

    If *url* is already absolute (starts with a recognised scheme) it is used
    as-is.  If *url* is relative (e.g. ``/api/openapi.json``) it is resolved
    against *system_base_url* by simple concatenation — ``base.rstrip('/') +
    '/' + url.lstrip('/')``.  If no base is available the relative string is
    used directly; rdflib will treat it as a relative IRI which is not ideal,
    but avoids a silent ``file:///`` mis-resolution.
    """
    if url.startswith(("http://", "https://", "urn:")):
        return URIRef(url)
    if system_base_url:
        base = system_base_url.rstrip("/")
        path = url if url.startswith("/") else "/" + url
        return URIRef(base + path)
    return URIRef(url)


# ── ResourceDefinition (base) ─────────────────────────────────────────────────

class ResourceDefinition(ORDBaseModel):
    """Machine-readable definition file attached to an ORD resource.

    This is the generic base; use the typed subclasses
    (``ApiResourceDefinition``, ``EventResourceDefinition``,
    ``CapabilityDefinition``) when the parent resource type is known, so that
    the correct ``rdf:type`` is asserted.

    Maps to ``ord:ORDResourceDefinition``.
    """

    class Meta(RdfanticModelMetadata):
        name = "ResourceDefinition"
        class_uris = {ORD.ORDResourceDefinition}
        term_builder = lambda self: URIRef(self.url) if self.url else BNode()  # noqa: E731

    def _build_subject(self, context: ShaclMaterializationContext) -> URIRef | BNode:
        """Resolve the definition URL using ``context.system_base_url`` for
        relative paths, so the emitted RDF node has an absolute IRI."""
        if self.url:
            return _resolve_definition_uri(
                self.url, getattr(context, "system_base_url", None)
            )
        return BNode()

    type: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.type}, uri_factory=definition_type_uri),
        Field(description="Definition format: openapi-v3 | asyncapi-v2 | edmx | graphql-sdl | …"),
    ]
    media_type: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.mediaType}),
        Field(alias="mediaType", default=None),
    ]
    url: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.url}, datatype=XSD.anyURI),
        Field(default=None),
    ]
    purpose: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.purpose}),
        Field(default=None),
    ]


# ── Typed ResourceDefinition subclasses ───────────────────────────────────────
# Each asserts the concrete ord:*ResourceDefinition type in addition to the
# shared ord:ORDResourceDefinition base type.

class ApiResourceDefinition(ResourceDefinition):
    """Resource definition attached to an ``ord:ApiResource``.

    Maps to ``ord:ApiResourceDefinition`` (subclass of ``ord:ORDResourceDefinition``).
    """

    class Meta(ResourceDefinition.Meta):
        name = "ApiResourceDefinition"
        class_uris = {ORD.ApiResourceDefinition, ORD.ORDResourceDefinition}


class EventResourceDefinition(ResourceDefinition):
    """Resource definition attached to an ``ord:EventResource``.

    Maps to ``ord:EventResourceDefinition`` (subclass of ``ord:ORDResourceDefinition``).
    """

    class Meta(ResourceDefinition.Meta):
        name = "EventResourceDefinition"
        class_uris = {ORD.EventResourceDefinition, ORD.ORDResourceDefinition}


class CapabilityDefinition(ResourceDefinition):
    """Resource definition attached to an ``ord:Capability``.

    Maps to ``ord:CapabilityDefinition`` (subclass of ``ord:ORDResourceDefinition``).
    """

    class Meta(ResourceDefinition.Meta):
        name = "CapabilityDefinition"
        class_uris = {ORD.CapabilityDefinition, ORD.ORDResourceDefinition}


class EntityTypeDefinition(ResourceDefinition):
    """Resource definition attached to an ``ord:OrdEntityType``.

    Maps to ``ord:EntityTypeDefinition`` (subclass of ``ord:ORDResourceDefinition``).
    """

    class Meta(ResourceDefinition.Meta):
        name = "EntityTypeDefinition"
        class_uris = {ORD.EntityTypeDefinition, ORD.ORDResourceDefinition}


class DataProductDefinition(ResourceDefinition):
    """Resource definition attached to an ``ord:DataProduct``.

    Maps to ``ord:DataProductDefinition`` (subclass of ``ord:ORDResourceDefinition``).
    """

    class Meta(ResourceDefinition.Meta):
        name = "DataProductDefinition"
        class_uris = {ORD.DataProductDefinition, ORD.ORDResourceDefinition}


class OverlayDefinition(ResourceDefinition):
    """Resource definition attached to an ``ord:Overlay``.

    Maps to ``ord:OverlayDefinition`` (subclass of ``ord:ORDResourceDefinition``).
    """

    class Meta(ResourceDefinition.Meta):
        name = "OverlayDefinition"
        class_uris = {ORD.OverlayDefinition, ORD.ORDResourceDefinition}


# ── Link (generic) ────────────────────────────────────────────────────────────

class Link(ORDBaseModel):
    """A generic URL link attached to an ORD resource or package.

    Maps to ``ord:Link``.
    """

    class Meta(RdfanticModelMetadata):
        name = "Link"
        class_uris = {ORD.Link}
        term_builder = lambda self: BNode()  # noqa: E731

    url: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.url}, datatype=XSD.anyURI),
        Field(description="URL target"),
    ]
    title: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.title}),
        Field(default=None),
    ]
    description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None),
    ]


# ── PackageLink (typed link for packages) ─────────────────────────────────────

class PackageLink(ORDBaseModel):
    """A semantically typed link specific to a Package.

    Maps to ``ord:PackageLink`` (subclass of ``ord:ORDTypedLink``).
    """

    class Meta(RdfanticModelMetadata):
        name = "PackageLink"
        class_uris = {ORD.PackageLink}
        term_builder = lambda self: BNode()  # noqa: E731

    url: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.url}, datatype=XSD.anyURI),
        Field(description="URL of the typed link"),
    ]
    type: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.linkType}, uri_factory=link_type_uri),
        Field(description="Semantic link type, e.g. 'partial', 'full', 'client-sdk', 'support', …"),
    ]
    custom_type: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.customType}),
        Field(alias="customType", default=None,
              description="Custom type identifier when type='custom'"),
    ]


# ── ApiEventResourceLink (typed link for APIs and events) ─────────────────────

class ApiEventResourceLink(ORDBaseModel):
    """A semantically typed link for API or Event resources.

    Maps to ``ord:ApiEventResourceLink`` (subclass of ``ord:ORDTypedLink``).
    """

    class Meta(RdfanticModelMetadata):
        name = "ApiEventResourceLink"
        class_uris = {ORD.ApiEventResourceLink}
        term_builder = lambda self: BNode()  # noqa: E731

    url: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.url}, datatype=XSD.anyURI),
        Field(),
    ]
    type: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.linkType}, uri_factory=link_type_uri),
        Field(description="api-documentation | consumer-portal | service-level-agreement | …"),
    ]
    custom_type: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.customType}),
        Field(alias="customType", default=None),
    ]


# ── ChangelogEntry ────────────────────────────────────────────────────────────

class ChangelogEntry(ORDBaseModel):
    """A single changelog entry tracking a resource version change.

    Maps to ``ord:ChangelogEntry``.
    """

    class Meta(RdfanticModelMetadata):
        name = "ChangelogEntry"
        class_uris = {ORD.ChangelogEntry}
        term_builder = lambda self: BNode()  # noqa: E731

    version: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.version}),
        Field(),
    ]
    release_status: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.releaseStatus}, uri_factory=release_status_uri),
        Field(alias="releaseStatus", default=None),
    ]
    date: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.date}, datatype=XSD.date),
        Field(default=None, description="ISO 8601 date of the change"),
    ]
    description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None),
    ]


# ── ConsumptionBundleReference ────────────────────────────────────────────────

class ConsumptionBundleReference(ORDBaseModel):
    """A reference from a resource to the consumption bundle it belongs to.

    Maps to ``ord:ConsumptionBundleReference``.
    """

    class Meta(RdfanticModelMetadata):
        name = "ConsumptionBundleReference"
        class_uris = {ORD.ConsumptionBundleReference}
        term_builder = lambda self: BNode()  # noqa: E731

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.consumptionBundle},
            uri_factory=lambda v: __import__(
                "ord_transformer.namespaces", fromlist=["ord_id_to_uri"]
            ).ord_id_to_uri(v),
            # field_class_uris removed: typing the referenced ConsumptionBundle
            # as ord:ConsumptionBundle creates validated stubs for cross-namespace
            # bundles not defined in this document set, causing false SHACL violations.
        ),
        Field(alias="ordId"),
    ]
    default_entry_point: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.defaultEntryPoint}, datatype=XSD.anyURI),
        Field(alias="defaultEntryPoint", default=None),
    ]


# ── CredentialExchangeStrategy ────────────────────────────────────────────────

class CredentialExchangeStrategy(ORDBaseModel):
    """Specifies how credentials for a consumption bundle can be obtained.

    Maps to ``ord:CredentialExchangeStrategy``.
    """

    class Meta(RdfanticModelMetadata):
        name = "CredentialExchangeStrategy"
        class_uris = {ORD.CredentialExchangeStrategy}
        term_builder = lambda self: BNode()  # noqa: E731

    type: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.type}),
        Field(description="Strategy type, e.g. 'custom', 'open', 'sap:cis-outbound:oauth2:…'"),
    ]
    custom_type: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.customType}),
        Field(alias="customType", default=None),
    ]
    description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None),
    ]


# ── Extensible ────────────────────────────────────────────────────────────────

class Extensible(ORDBaseModel):
    """Describes whether and how consumers can extend an ORD resource.

    Maps to ``ord:Extensible``.
    """

    class Meta(RdfanticModelMetadata):
        name = "Extensible"
        class_uris = {ORD.Extensible}
        term_builder = lambda self: BNode()  # noqa: E731

    supported: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.type}),
        Field(description="no | manual | automatic"),
    ]
    description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None),
    ]


# ── Typed resource-reference objects ──────────────────────────────────────────

class RelatedApiResource(ORDBaseModel):
    """A typed reference to a related API Resource.

    Maps to ``ord:RelatedApiResource``.
    """

    class Meta(RdfanticModelMetadata):
        name = "RelatedApiResource"
        class_uris = {ORD.RelatedApiResource}
        term_builder = lambda self: BNode()  # noqa: E731

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.ordId},
            uri_factory=lambda v: __import__(
                "ord_transformer.namespaces", fromlist=["ord_id_to_uri"]
            ).ord_id_to_uri(v),
            field_class_uris={ORD.ApiResource},
        ),
        Field(alias="ordId", description="ORD ID of the related API Resource"),
    ]


class RelatedEventResource(ORDBaseModel):
    """A typed reference to a related Event Resource.

    Maps to ``ord:RelatedEventResource``.
    """

    class Meta(RdfanticModelMetadata):
        name = "RelatedEventResource"
        class_uris = {ORD.RelatedEventResource}
        term_builder = lambda self: BNode()  # noqa: E731

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.ordId},
            uri_factory=lambda v: __import__(
                "ord_transformer.namespaces", fromlist=["ord_id_to_uri"]
            ).ord_id_to_uri(v),
            field_class_uris={ORD.EventResource},
        ),
        Field(alias="ordId", description="ORD ID of the related Event Resource"),
    ]


class RelatedEntityType(ORDBaseModel):
    """A directional typed reference from one resource to a related EntityType.

    Maps to ``ord:RelatedEntityType``.
    """

    class Meta(RdfanticModelMetadata):
        name = "RelatedEntityType"
        class_uris = {ORD.RelatedEntityType}
        term_builder = lambda self: __import__(  # noqa: E731
            "ord_transformer.namespaces", fromlist=["ord_id_to_uri"]
        ).ord_id_to_uri(self.ord_id)

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.ordId},
            # uri_factory removed: ordId is stored as xsd:string literal.
            # The term_builder (see Meta) handles making this node itself an IRI.
        ),
        Field(alias="ordId", description="ORD ID of the related Entity Type"),
    ]


class RelatedCapability(ORDBaseModel):
    """A directional typed reference from one resource to a related Capability.

    Maps to ``ord:RelatedCapability``.
    """

    class Meta(RdfanticModelMetadata):
        name = "RelatedCapability"
        class_uris = {ORD.RelatedCapability}
        term_builder = lambda self: BNode()  # noqa: E731

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.ordId},
            uri_factory=lambda v: __import__(
                "ord_transformer.namespaces", fromlist=["ord_id_to_uri"]
            ).ord_id_to_uri(v),
            field_class_uris={ORD.Capability},
        ),
        Field(alias="ordId", description="ORD ID of the related Capability"),
    ]


# ── DataProductInputPort / DataProductOutputPort ──────────────────────────────

class DataProductInputPort(ORDBaseModel):
    """Where a Data Product retrieves its input data from (reference to IntegrationDependency).

    Maps to ``ord:DataProductInputPort``.
    """

    class Meta(RdfanticModelMetadata):
        name = "DataProductInputPort"
        class_uris = {ORD.DataProductInputPort}
        term_builder = lambda self: ord_id_to_uri(self.ord_id)  # noqa: E731

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="ordId", description="ORD ID of the referenced IntegrationDependency"),
    ]


class DataProductOutputPort(ORDBaseModel):
    """API or Event resources through which a Data Product exposes its data.

    Maps to ``ord:DataProductOutputPort``.
    """

    class Meta(RdfanticModelMetadata):
        name = "DataProductOutputPort"
        class_uris = {ORD.DataProductOutputPort}
        term_builder = lambda self: ord_id_to_uri(self.ord_id)  # noqa: E731

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="ordId", description="ORD ID of the referenced API or Event Resource"),
    ]


# ── DataProductLink (typed link for data products) ───────────────────────────

class DataProductLink(ORDBaseModel):
    """A semantically typed link specific to a Data Product.

    Maps to ``ord:DataProductLink`` (subclass of ``ord:ORDTypedLink``).
    """

    class Meta(RdfanticModelMetadata):
        name = "DataProductLink"
        class_uris = {ORD.DataProductLink}
        term_builder = lambda self: BNode()  # noqa: E731

    url: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.url}, datatype=XSD.anyURI),
        Field(),
    ]
    type: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.linkType}, uri_factory=link_type_uri),
        Field(description="payment | terms-of-use | service-level-agreement | …"),
    ]
    custom_type: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.customType}),
        Field(alias="customType", default=None),
    ]


# ── ExposedEntityType ─────────────────────────────────────────────────────────

class ExposedEntityType(ORDBaseModel):
    """Declares that an ApiResource or EventResource exposes instances of a particular EntityType.

    Maps to ``ord:ExposedEntityType``.
    """

    class Meta(RdfanticModelMetadata):
        name = "ExposedEntityType"
        class_uris = {ORD.ExposedEntityType}
        term_builder = lambda self: __import__(  # noqa: E731
            "ord_transformer.namespaces", fromlist=["ord_id_to_uri"]
        ).ord_id_to_uri(self.ord_id)

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={ORD.ordId},
            # uri_factory removed: ordId is stored as xsd:string literal.
            # The term_builder handles making this node itself an IRI.
        ),
        Field(alias="ordId", description="ORD ID of the exposed EntityType"),
    ]
