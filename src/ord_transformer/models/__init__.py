"""ORD entity models — RDFantic-annotated Pydantic models for all ORD types
defined in the ORD vocabulary (``ord_open_vocab.ttl``).
"""

# ── Top-level resource models ─────────────────────────────────────────────────
from .agent import Agent
from .api_resource import ApiResource
from .capability import Capability
from .consumption_bundle import ConsumptionBundle
from .data_product import DataProduct
from .document import OrdDocument
from .entity_type import EntityType
from .event_resource import EventResource
from .integration_dependency import IntegrationDependency
from .overlay import Overlay
from .package import Package
from .vendor import Vendor

# ── Taxonomy models ───────────────────────────────────────────────────────────
from .taxonomy import Group, GroupType, Product, Tombstone

# ── Embedded / supporting models ──────────────────────────────────────────────
from .supporting import (
    ApiEventResourceLink,
    ChangelogEntry,
    ConsumptionBundleReference,
    CredentialExchangeStrategy,
    DataProductInputPort,
    DataProductLink,
    DataProductOutputPort,
    ExposedEntityType,
    Extensible,
    Link,
    PackageLink,
    RelatedApiResource,
    RelatedCapability,
    RelatedEntityType,
    RelatedEventResource,
    ResourceDefinition,
)

# ── ALL_MODELS — every top-level class the transformer and SHACL generator use ─
#: Ordered list of all ORD top-level entity model classes.
ALL_MODELS = [
    # Document
    OrdDocument,
    # Resources
    ApiResource,
    EventResource,
    EntityType,
    DataProduct,
    Capability,
    IntegrationDependency,
    Agent,
    Overlay,
    # Taxonomy
    Package,
    ConsumptionBundle,
    Vendor,
    Product,
    Group,
    GroupType,
    # Lifecycle
    Tombstone,
]

__all__ = [
    # Top-level resources
    "OrdDocument",
    "ApiResource",
    "EventResource",
    "EntityType",
    "DataProduct",
    "Capability",
    "IntegrationDependency",
    "Agent",
    "Overlay",
    # Taxonomy
    "Package",
    "ConsumptionBundle",
    "Vendor",
    "Product",
    "Group",
    "GroupType",
    # Lifecycle
    "Tombstone",
    # Embedded / supporting
    "ResourceDefinition",
    "Link",
    "PackageLink",
    "ApiEventResourceLink",
    "DataProductLink",
    "ChangelogEntry",
    "ConsumptionBundleReference",
    "CredentialExchangeStrategy",
    "Extensible",
    "RelatedApiResource",
    "RelatedEventResource",
    "RelatedEntityType",
    "RelatedCapability",
    "DataProductInputPort",
    "DataProductOutputPort",
    "ExposedEntityType",
    # Registry
    "ALL_MODELS",
]
