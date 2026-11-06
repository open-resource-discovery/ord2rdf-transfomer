"""ORDTransformer — load an ORD JSON document and produce an rdflib Graph."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SKOS

from rdfantic import ShaclMaterializationContext

from .exceptions import ORDParseError
from .models import (
    ALL_MODELS,
    Agent,
    ApiResource,
    Capability,
    ConsumptionBundle,
    DataProduct,
    EntityType,
    EventResource,
    Group,
    GroupType,
    IntegrationDependency,
    OrdDocument,
    Overlay,
    Package,
    Product,
    Tombstone,
    Vendor,
)
from .namespaces import (
    ORD,
    ORD_INSTANCE,
    VOCAB_IMPL_STDS,
    bind_standard_namespaces,
    implementation_standard_uri,
)

# Resource types whose items may carry a "resourceDefinitions" array with
# relative URL paths that must be resolved before model validation.
_RESOURCE_DEFINITION_HOSTS: tuple[str, ...] = (
    "apiResources",
    "eventResources",
    "capabilities",
    "entityTypes",
    "agents",
    "overlays",
)

# Mapping: ORD JSON top-level array key → RDFantic model class
# All keys follow the ORD spec document structure.
_ARRAY_KEY_TO_MODEL: dict[str, type] = {
    # Taxonomy
    "packages": Package,
    "consumptionBundles": ConsumptionBundle,
    "vendors": Vendor,
    "products": Product,
    "groups": Group,
    "groupTypes": GroupType,
    # Resources
    "apiResources": ApiResource,
    "eventResources": EventResource,
    "entityTypes": EntityType,
    "dataProducts": DataProduct,
    "capabilities": Capability,
    "integrationDependencies": IntegrationDependency,
    "agents": Agent,
    "overlays": Overlay,
    # Lifecycle
    "tombstones": Tombstone,
}


class ORDTransformer:
    """Transform an ORD JSON document into an ``rdflib.Graph``.

    Parameters
    ----------
    base_instance_uri:
        Root URI used as the ``base_uri`` for the
        :class:`~rdfantic.ShaclMaterializationContext`.
        Defaults to ``"https://open-resource-discovery.org/instance/"``.

    Examples
    --------
    .. code-block:: python

        transformer = ORDTransformer()
        graph = transformer.transform_file("data/samples/sample_ord.json")
        graph.serialize("output/ord_data.ttl", format="turtle")
    """

    def __init__(
        self,
        base_instance_uri: str = "https://open-resource-discovery.org/instance/",
    ) -> None:
        self.context = ShaclMaterializationContext(base_instance_uri)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def transform_file(self, path: str | Path) -> Graph:
        """Load an ORD JSON file from *path* and return the transformed graph.

        Parameters
        ----------
        path:
            Filesystem path to the ORD JSON document.

        Returns
        -------
        rdflib.Graph
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"ORD JSON file not found: {path}")
        with path.open(encoding="utf-8") as fh:
            doc = json.load(fh)
        return self.transform(doc)

    def transform(self, ord_doc: dict[str, Any]) -> Graph:
        """Transform an already-parsed ORD JSON dict into an ``rdflib.Graph``.

        Parameters
        ----------
        ord_doc:
            A Python dict representing the ORD document (as returned by
            ``json.load``).

        Returns
        -------
        rdflib.Graph
            A graph with all RDF triples for the document and its resources.
        """
        g = Graph()
        bind_standard_namespaces(g)

        # ── Serialize the top-level Document ──────────────────────────────────
        try:
            doc_model = OrdDocument.model_validate(ord_doc)
        except Exception as exc:
            raise ORDParseError(f"Failed to parse ORD document header: {exc}") from exc

        g += doc_model.model_dump_rdf(
            context=self.context,
            parent=None,
            predicates=set(),
        )

        self._resolve_definition_urls(ord_doc, self._extract_base_url(ord_doc))

        # ── Serialize each top-level entity array ─────────────────────────────
        for json_key, model_cls in _ARRAY_KEY_TO_MODEL.items():
            items = ord_doc.get(json_key, []) or []
            for item_dict in items:
                try:
                    instance = model_cls.model_validate(item_dict)
                except Exception as exc:
                    raise ORDParseError(
                        f"Failed to parse {json_key} item {item_dict.get('ordId', '?')}: {exc}"
                    ) from exc

                g += instance.model_dump_rdf(
                    context=self.context,
                    parent=None,
                    predicates=set(),
                )

        # ── Emit stub skos:Concept triples for vendor-extension values ─────────
        self._mint_extension_concepts(g, ord_doc)

        # ── Mark referenced-but-undefined instance URIs as ExternalReferences ──
        self._mint_external_reference_stubs(g)

        return g

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_base_url(ord_doc: dict[str, Any]) -> str | None:
        """Extract the system base URL from an ORD document.

        The ORD spec allows ``baseUrl`` in two locations:

        1. Top-level field — used by simpler, single-perspective documents::

               { "openResourceDiscovery": "1.9", "baseUrl": "https://..." }

        2. Nested under ``describedSystemInstance`` — used by documents written
           from the *system-instance* perspective::

               { "describedSystemInstance": { "baseUrl": "https://..." } }

        Returns the first non-empty value found, or ``None``.
        """
        return (
            ord_doc.get("baseUrl")
            or (ord_doc.get("describedSystemInstance") or {}).get("baseUrl")
        )

    @staticmethod
    def _resolve_definition_urls(
        ord_doc: dict[str, Any], base_url: str | None
    ) -> None:
        """Resolve relative ``url`` fields in ``resourceDefinitions`` to absolute IRIs.

        ORD resource-definition ``url`` values are often root-relative paths such
        as ``/api/openapi.json``.  ``ResourceDefinition.Meta.term_builder`` calls
        ``URIRef(self.url)`` directly (the ``_build_subject`` hook is not wired into
        rdfantic), so the field must already contain an absolute IRI by the time
        ``model_validate`` runs — otherwise rdflib emits a relative-IRI subject node
        (``</api/openapi.json>``) that many triple stores reject.

        Parameters
        ----------
        ord_doc:
            The parsed ORD document dict, as returned by ``json.load``.
        base_url:
            Value of the document's ``baseUrl`` field, e.g.
            ``"https://tenant.example.com"``.  If ``None`` or empty the method
            returns immediately and leaves all URLs unchanged.
        """
        if not base_url:
            return
        base = base_url.rstrip("/")
        for array_key in _RESOURCE_DEFINITION_HOSTS:
            for item in ord_doc.get(array_key, []) or []:
                for defn in item.get("resourceDefinitions", []) or []:
                    url = defn.get("url")
                    if not url or url.startswith(("http://", "https://", "urn:")):
                        continue
                    path = url if url.startswith("/") else "/" + url
                    defn["url"] = base + path

    def _mint_extension_concepts(
        self, g: Graph, ord_doc: dict[str, Any]
    ) -> None:
        """Emit ``skos:Concept`` stub triples for vendor-extension implementationStandard values.

        ORD allows any Specification ID (``<vendor>:<name>:<version>``) as
        ``implementationStandard``, beyond the two concepts defined in the ORD
        core vocabulary.  The property's ``rdfs:range`` is ``skos:Concept``, so
        unknown values need at least a type declaration and scheme membership to
        be well-formed in the graph.

        For each value not already covered by ``VOCAB_IMPL_STDS``, three triples
        are added::

            ord:ImplementationStandard-sap-ape-api-v1
                a skos:Concept ;
                skos:notation "sap:ape-api:v1" ;
                skos:inScheme ord:ImplementationStandardScheme .

        ``skos:notation`` preserves the original Specification ID string so the
        value is round-trippable without loss.

        Parameters
        ----------
        g:
            The graph to extend (mutated in place).
        ord_doc:
            The raw ORD JSON dict, used to collect ``implementationStandard``
            values before any IRI transformation.
        """
        seen: set[str] = set()
        # JSON keys whose items may carry implementationStandard
        _IMPL_STD_KEYS = ("apiResources", "eventResources")

        for array_key in _IMPL_STD_KEYS:
            for item in ord_doc.get(array_key, []) or []:
                value = item.get("implementationStandard")
                if (
                    value is None
                    or value in VOCAB_IMPL_STDS
                    or value in seen
                ):
                    continue
                seen.add(value)
                concept = implementation_standard_uri(value)
                g.add((concept, RDF.type, SKOS.Concept))
                g.add((concept, SKOS.notation, Literal(value)))
                g.add((concept, SKOS.inScheme, ORD.ImplementationStandardScheme))

    @staticmethod
    def _mint_external_reference_stubs(g: Graph) -> None:
        """Emit ``ord:ExternalReference`` type triples for cross-namespace stub nodes.

        When an ORD resource references another resource by ORD ID (e.g. via
        ``partOfPackage``, ``vendor``, or ``consumptionBundle``), the transformer
        emits a URI triple for the referenced node but does **not** materialise any
        subject triples for it — the referenced node is a *stub*.

        Without this step, RDFS inference during SHACL validation would infer the
        stub's class from the property's ``rdfs:range`` declaration in the ORD
        vocabulary (e.g. ``ord:partOfPackage rdfs:range ord:Package``).  That makes
        the stub a SHACL focus node for ``sh:targetClass ord:Package``, which then
        fires ``sh:MinCountConstraintComponent`` violations for every mandatory
        property (``ord:ordId``, ``ord:title``, ``ord:version``) that the stub
        naturally lacks.

        This method detects stubs as instance-namespace URIs that appear as RDF
        *objects* but never as RDF *subjects* in the graph, and marks each one with
        ``rdf:type ord:ExternalReference``.  Because no SHACL shape targets
        ``ord:ExternalReference``, and the :class:`SHACLValidator` now defaults to
        ``inference="none"`` (preventing RDFS from re-injecting inferred types),
        stubs are transparently excluded from all constraint checking.

        This is the correct approach when the transformer is expected to handle ORD
        documents that *reference* resources defined in other ORD documents — a
        valid and common pattern in multi-system deployments.

        Parameters
        ----------
        g:
            The RDF graph to inspect and extend (mutated in place).
        """
        instance_prefix = str(ORD_INSTANCE)

        # All instance URIs that are fully materialised (appear as subjects)
        defined: set[URIRef] = {
            s
            for s, _p, _o in g
            if isinstance(s, URIRef) and str(s).startswith(instance_prefix)
        }

        # All instance URIs that are cross-referenced (appear as objects)
        referenced: set[URIRef] = {
            o
            for _s, _p, o in g
            if isinstance(o, URIRef) and str(o).startswith(instance_prefix)
        }

        # Stubs = referenced but never materialised as a subject
        for stub_uri in referenced - defined:
            g.add((stub_uri, RDF.type, ORD.ExternalReference))

    # ------------------------------------------------------------------
    # Convenience: serialize directly to a file
    # ------------------------------------------------------------------

    def transform_to_file(
        self,
        ord_path: str | Path,
        output_path: str | Path,
        fmt: str = "turtle",
    ) -> Path:
        """Transform *ord_path* and write the RDF graph to *output_path*.

        Parameters
        ----------
        ord_path:
            Input ORD JSON file.
        output_path:
            Destination RDF file.
        fmt:
            rdflib serialization format: ``"turtle"``, ``"n3"``,
            ``"nt"``, ``"json-ld"``, ``"xml"``.

        Returns
        -------
        pathlib.Path
            The resolved output path.
        """
        graph = self.transform_file(ord_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        graph.serialize(str(output_path), format=fmt)
        return output_path
