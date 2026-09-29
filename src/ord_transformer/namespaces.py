"""RDF namespace definitions and URI helper functions for the ORD vocabulary."""

from __future__ import annotations

from rdflib import Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, RDFS, SKOS, XSD

# ── ORD namespaces ────────────────────────────────────────────────────────────

#: ORD vocabulary namespace  (classes, properties)
ORD = Namespace("https://open-resource-discovery.org/vocab/v1#")

#: ORD instance namespace  (individual resource URIs)
ORD_INSTANCE = Namespace("https://open-resource-discovery.org/instance/")

#: ORD spec namespace
ORD_SPEC = Namespace("https://open-resource-discovery.org/spec-v1/")

# Re-export standard namespaces so callers can import from one place
__all__ = [
    "ORD",
    "ORD_INSTANCE",
    "ORD_SPEC",
    "DCAT",
    "DCTERMS",
    "FOAF",
    "RDF",
    "RDFS",
    "SKOS",
    "XSD",
]


# ── URI construction helpers ──────────────────────────────────────────────────

def ord_id_to_uri(ord_id: str) -> URIRef:
    """Convert an ORD ID string to a stable instance URI.

    The ORD ID colon-separators are replaced with slashes to form a
    hierarchical URI path::

        "sap.example:package:ExamplePackage:v1"
        → <https://open-resource-discovery.org/instance/sap.example/package/ExamplePackage/v1>

    Parameters
    ----------
    ord_id:
        A valid ORD ID, e.g. ``"sap.example:apiResource:ProductAPI:v1"``.

    Returns
    -------
    rdflib.URIRef
    """
    return URIRef(str(ORD_INSTANCE) + ord_id.replace(":", "/"))


def concept_uri(scheme_local: str, value: str) -> URIRef:
    """Build a SKOS concept URI within the ORD vocabulary namespace.

    Parameters
    ----------
    scheme_local:
        Local name of the concept scheme, e.g. ``"ReleaseStatusScheme"``.
    value:
        Concept value, e.g. ``"active"``.
    """
    return URIRef(f"{ORD}{scheme_local}/{value}")


# ── Controlled-vocabulary concept URI factories ───────────────────────────────
# New open vocabulary (ord_new_open_vocab.ttl) represents controlled values as
# SKOS concepts in the ord: namespace rather than plain xsd:string literals.
# Each factory maps a JSON string value to the correct concept URI.

def release_status_uri(value: str) -> URIRef:
    """Map a releaseStatus string to ``ord:ReleaseStatus-{value}``."""
    return ORD[f"ReleaseStatus-{value}"]


def visibility_uri(value: str) -> URIRef:
    """Map a visibility string to ``ord:Visibility-{value}``."""
    return ORD[f"Visibility-{value}"]


# JSON protocol strings may use kebab-case; concept names use camelCase.
_PROTOCOL_NORM: dict[str, str] = {
    "odata-v2": "odataV2",
    "odata-v4": "odataV4",
    "odata-v4-delta": "odataV4Delta",
    "delta-sharing": "deltaSharing",
    "sap-rfc": "sapRfc",
    "sap-ape-api": "sapApeApi",
    "sap-cdi-api": "sapCdiApi",
}


def api_protocol_uri(value: str) -> URIRef:
    """Map an apiProtocol string to ``ord:ApiProtocol-{normalised}``."""
    return ORD[f"ApiProtocol-{_PROTOCOL_NORM.get(value, value)}"]


# ResourceDefinition type strings → ApiDefType concept URIs
_DEF_TYPE_NORM: dict[str, str] = {
    "openapi-v2": "openapiV2",
    "openapi-v3": "openapiV3",
    "openapi-v3.1": "openapiV31",
    "edmx": "edmx",
    "csdl-json": "csdlJson",
    "graphql-sdl": "graphqlSdl",
    "wsdl-v1": "wsdlV1",
    "wsdl-v2": "wsdlV2",
    "raml-v1": "ramlV1",
    "a2a-agent-card": "a2aAgentCard",
    "ord:overlay:v1": "overlayV1",
}


def definition_type_uri(value: str) -> URIRef:
    """Map a resource-definition type string to ``ord:ApiDefType-{normalised}``."""
    return ORD[f"ApiDefType-{_DEF_TYPE_NORM.get(value, value)}"]


# API/Event resource link-type strings → PackageLinkType / ApiEventLinkType concepts
_LINK_TYPE_NORM: dict[str, str] = {
    "api-documentation": "ApiEventLinkType-apiDocumentation",
    "authentication": "PackageLinkType-authentication",
    "client-registration": "PackageLinkType-clientRegistration",
    "console": "PackageLinkType-console",
    "custom": "PackageLinkType-custom",
    "license": "PackageLinkType-license",
    "payment": "PackageLinkType-payment",
    "sandbox": "PackageLinkType-sandbox",
    "sla": "PackageLinkType-sla",
    "support": "PackageLinkType-support",
    "terms-of-use": "PackageLinkType-termsOfUse",
}


def link_type_uri(value: str) -> URIRef:
    """Map a link-type string to the appropriate ORD concept URI."""
    local = _LINK_TYPE_NORM.get(value, f"LinkType-{value}")
    return ORD[local]


# Industry concept URIs (ord:IndustryConceptScheme members)
_INDUSTRY_MAP: dict[str, str] = {
    "Aerospace and Defense": "AerospaceAndDefense",
    "Agribusiness": "Agribusiness",
    "Asset Management": "AssetManagement",
    "Automotive": "Automotive",
    "Banking": "Banking",
    "Chemicals": "Chemicals",
    "Commerce": "Commerce",
    "Consumer Products": "ConsumerProducts",
    "Defense and Security": "DefenseAndSecurity",
    "Engineering Construction and Operations": "EngineeringConstructionAndOperations",
    "Finance": "Finance",
    "Financial Services": "Finance",
    "Grid Operations and Maintenance": "GridOperationsAndMaintenance",
    "Healthcare": "Healthcare",
    "High Tech": "HighTech",
    "Higher Education and Research": "HigherEducationAndResearch",
    "Human Resources": "HumanResources",
    "Industrial Machinery and Components": "IndustrialMachineryAndComponents",
    "Insurance": "Insurance",
    "Life Sciences": "LifeSciences",
    "Maintenance and Engineering": "MaintenanceAndEngineering",
    "Manufacturing": "Manufacturing",
    "Marketing": "Marketing",
    "Media": "Media",
    "Metering": "Metering",
    "Mill Products": "MillProducts",
    "Mining": "Mining",
    "Oil and Gas": "OilAndGas",
    "Oil & Gas": "OilAndGas",
    "Plant Operations and Maintenance": "PlantOperationsAndMaintenance",
    "Professional Services": "ProfessionalServices",
    "Public Sector": "PublicSector",
    "Public Services": "PublicServices",
    "Research and Development Engineering": "ResearchAndDevelopmentEngineering",
    "Retail": "Retail",
    "Sales": "Sales",
    "Service": "Service",
    "Service Industries": "ServiceIndustries",
    "Sourcing and Procurement": "SourcingAndProcurement",
    "Sports and Entertainment": "SportsAndEntertainment",
    "Strategy Compliance and Governance": "StrategyComplianceAndGovernance",
    "Supply Chain": "SupplyChain",
    "Sustainability": "Sustainability",
    "Telecommunications": "Telecommunications",
    "Travel and Transportation": "TravelAndTransportation",
    "Utilities": "Utilities",
    "Wholesale Distribution": "WholesaleDistribution",
}


def industry_uri(value: str) -> URIRef:
    """Map an industry string to its ORD SKOS concept URI."""
    local = _INDUSTRY_MAP.get(value, "".join(w.capitalize() for w in value.split()))
    return ORD[local]


# Line-of-business concept URIs (ord:LineOfBusinessConceptScheme members)
_LOB_MAP: dict[str, str] = {
    "Finance": "Finance",
    "Sales": "Sales",
    "Human Resources": "HumanResources",
    "Supply Chain": "SupplyChain",
    "Marketing": "Marketing",
    "Procurement": "SourcingAndProcurement",
    "Sourcing and Procurement": "SourcingAndProcurement",
    "Manufacturing": "Manufacturing",
    "Service": "Service",
    "Asset Management": "AssetManagement",
    "Sustainability": "Sustainability",
}


def lob_uri(value: str) -> URIRef:
    """Map a lineOfBusiness string to its ORD SKOS concept URI."""
    local = _LOB_MAP.get(value, "".join(w.capitalize() for w in value.split()))
    return ORD[local]


# ── Standard namespace binding helper ─────────────────────────────────────────

def bind_standard_namespaces(graph) -> None:  # type: ignore[type-arg]
    """Bind all well-known prefixes onto *graph* for readable Turtle output."""
    graph.bind("ord", ORD)
    graph.bind("ord-instance", ORD_INSTANCE)
    graph.bind("dcat", DCAT)
    graph.bind("dcterms", DCTERMS)
    graph.bind("foaf", FOAF)
    graph.bind("rdf", RDF)
    graph.bind("rdfs", RDFS)
    graph.bind("skos", SKOS)
    graph.bind("xsd", XSD)
