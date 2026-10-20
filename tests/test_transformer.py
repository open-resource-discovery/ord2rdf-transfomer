"""Tests for the ORD JSON → RDF transformer."""

from __future__ import annotations

import pytest
from rdflib import RDF, Graph, Literal, URIRef

from ord_transformer.namespaces import ORD, ord_id_to_uri
from ord_transformer.transformer import ORDTransformer


class TestORDTransformer:
    def test_transform_returns_graph(self, transformed_graph):
        assert isinstance(transformed_graph, Graph)

    def test_graph_non_empty(self, transformed_graph):
        assert len(transformed_graph) > 0

    # ── Package ───────────────────────────────────────────────────────────────

    # ── Package ───────────────────────────────────────────────────────────────

    def test_package_type_in_graph(self, transformed_graph):
        pkg_uri = ord_id_to_uri("acme.demo:package:CorePackage:v1")
        assert (pkg_uri, RDF.type, ORD.Package) in transformed_graph

    def test_package_title_in_graph(self, transformed_graph):
        pkg_uri = ord_id_to_uri("acme.demo:package:CorePackage:v1")
        titles = list(transformed_graph.objects(pkg_uri, ORD.title))
        assert len(titles) >= 1
        assert any("Core Package" in str(t) for t in titles)

    # ── API Resource ──────────────────────────────────────────────────────────

    def test_api_resource_type_in_graph(self, transformed_graph):
        api_uri = ord_id_to_uri("acme.demo:apiResource:CatalogueAPI:v1")
        assert (api_uri, RDF.type, ORD.APIResource) in transformed_graph

    def test_api_resource_links_to_package(self, transformed_graph):
        api_uri = ord_id_to_uri("acme.demo:apiResource:CatalogueAPI:v1")
        pkg_uri = ord_id_to_uri("acme.demo:package:CorePackage:v1")
        pkgs = list(transformed_graph.objects(api_uri, ORD.partOfPackage))
        assert pkg_uri in pkgs

    def test_multiple_api_resources(self, transformed_graph):
        api_uris = list(transformed_graph.subjects(RDF.type, ORD.APIResource))
        assert len(api_uris) >= 3  # sample has 3 APIs

    # ── Event Resource ────────────────────────────────────────────────────────

    def test_event_resource_type_in_graph(self, transformed_graph):
        evt_uri = ord_id_to_uri("acme.demo:eventResource:CatalogueEvents:v1")
        assert (evt_uri, RDF.type, ORD.EventResource) in transformed_graph

    # ── Entity Type ───────────────────────────────────────────────────────────

    def test_entity_type_in_graph(self, transformed_graph):
        et_uri = ord_id_to_uri("acme.demo:entityType:CatalogueItem:v1")
        assert (et_uri, RDF.type, ORD.OrdEntityType) in transformed_graph

    # ── Document ──────────────────────────────────────────────────────────────

    def test_document_type_in_graph(self, transformed_graph):
        doc_uri = URIRef("https://api.acme-demo.org")
        assert (doc_uri, RDF.type, ORD.Document) in transformed_graph

    # ── Vendor ────────────────────────────────────────────────────────────────

    def test_vendor_type_in_graph(self, transformed_graph):
        vendor_uri = ord_id_to_uri("acme.demo:vendor:AcmeCorp:")
        assert (vendor_uri, RDF.type, ORD.Vendor) in transformed_graph

    # ── Consumption Bundle ────────────────────────────────────────────────────

    def test_consumption_bundle_in_graph(self, transformed_graph):
        cb_uri = ord_id_to_uri("acme.demo:consumptionBundle:PublicBundle:v1")
        assert (cb_uri, RDF.type, ORD.ConsumptionBundle) in transformed_graph

    # ── Error handling ────────────────────────────────────────────────────────

    def test_transform_file_not_found(self, transformer):
        with pytest.raises(FileNotFoundError):
            transformer.transform_file("nonexistent_file.json")

    def test_transform_malformed_doc(self, transformer):
        """A document missing openResourceDiscovery should raise ORDParseError."""
        from ord_transformer.exceptions import ORDParseError

        with pytest.raises(ORDParseError):
            transformer.transform({"packages": [{"ordId": "x:package:X:v1"}]})

    # ── Serialization ─────────────────────────────────────────────────────────

    def test_transform_to_file(self, transformer, sample_ord_path, tmp_path):
        out = tmp_path / "test_out.ttl"
        result = transformer.transform_to_file(sample_ord_path, out, fmt="turtle")
        assert result.exists()
        text = result.read_text(encoding="utf-8")
        assert "@prefix" in text
        assert "ord:" in text

    def test_namespace_bindings_present(self, transformed_graph):
        ns_dict = dict(transformed_graph.namespaces())
        prefixes = set(str(k) for k in ns_dict.keys())
        assert "ord" in prefixes
        assert "rdf" in prefixes or "rdf" in str(ns_dict)


# ── Extension concept stub generation ─────────────────────────────────────────

class TestExtensionConceptStubs:
    """Verify that vendor-extension implementationStandard values get stub
    skos:Concept triples so the graph satisfies rdfs:range skos:Concept."""

    # Minimal ORD document with a vendor Spec ID on an API resource
    _DOC_API = {
        "openResourceDiscovery": "1.9",
        "apiResources": [
            {
                "ordId": "test.stub:apiResource:ApeApi:v1",
                "title": "APE API",
                "version": "1.0.0",
                "releaseStatus": "active",
                "visibility": "public",
                "partOfPackage": "test.stub:package:TestPackage:v1",
                "implementationStandard": "sap:ape-api:v1",
            }
        ],
    }

    # Document with two different vendor Spec IDs (API + Event)
    _DOC_BOTH = {
        "openResourceDiscovery": "1.9",
        "apiResources": [
            {
                "ordId": "test.stub:apiResource:ApeApi:v1",
                "title": "APE API",
                "version": "1.0.0",
                "releaseStatus": "active",
                "visibility": "public",
                "partOfPackage": "test.stub:package:TestPackage:v1",
                "implementationStandard": "sap:ape-api:v1",
            }
        ],
        "eventResources": [
            {
                "ordId": "test.stub:eventResource:CdiEvents:v1",
                "title": "CDI Events",
                "version": "1.0.0",
                "releaseStatus": "active",
                "visibility": "public",
                "partOfPackage": "test.stub:package:TestPackage:v1",
                "implementationStandard": "sap:cdi-api:v1",
            }
        ],
    }

    # Document using the known vocab value — no stub should be emitted
    _DOC_KNOWN = {
        "openResourceDiscovery": "1.9",
        "apiResources": [
            {
                "ordId": "test.stub:apiResource:OsbApi:v1",
                "title": "OSB API",
                "version": "1.0.0",
                "releaseStatus": "active",
                "visibility": "public",
                "partOfPackage": "test.stub:package:TestPackage:v1",
                "implementationStandard": "cff:open-service-broker:v2",
            }
        ],
    }

    def _transform(self, doc: dict) -> Graph:
        return ORDTransformer().transform(doc)

    def test_stub_type_triple_emitted(self):
        """Vendor Spec ID concept gets a:skos:Concept type declaration."""
        from rdflib.namespace import SKOS

        g = self._transform(self._DOC_API)
        concept = ORD["ImplementationStandard-sap-ape-api-v1"]
        assert (concept, RDF.type, SKOS.Concept) in g

    def test_stub_notation_preserves_spec_id(self):
        """skos:notation on the stub equals the original Specification ID string."""
        from rdflib.namespace import SKOS

        g = self._transform(self._DOC_API)
        concept = ORD["ImplementationStandard-sap-ape-api-v1"]
        notations = list(g.objects(concept, SKOS.notation))
        assert len(notations) == 1
        assert str(notations[0]) == "sap:ape-api:v1"

    def test_stub_in_scheme(self):
        """Stub concept is declared as a member of ord:ImplementationStandardScheme."""
        from rdflib.namespace import SKOS

        g = self._transform(self._DOC_API)
        concept = ORD["ImplementationStandard-sap-ape-api-v1"]
        assert (concept, SKOS.inScheme, ORD.ImplementationStandardScheme) in g

    def test_stubs_emitted_for_both_api_and_event_resources(self):
        """Stub generation covers both apiResources and eventResources arrays."""
        from rdflib.namespace import SKOS

        g = self._transform(self._DOC_BOTH)
        ape = ORD["ImplementationStandard-sap-ape-api-v1"]
        cdi = ORD["ImplementationStandard-sap-cdi-api-v1"]
        assert (ape, RDF.type, SKOS.Concept) in g
        assert (cdi, RDF.type, SKOS.Concept) in g

    def test_no_stub_for_known_vocab_value(self):
        """A value in VOCAB_IMPL_STDS does NOT get a stub — it is in the vocab."""
        from rdflib.namespace import SKOS

        from ord_transformer.namespaces import VOCAB_IMPL_STDS

        g = self._transform(self._DOC_KNOWN)
        # cff:open-service-broker:v2 maps to cffOpenServiceBrokerV2 via _IMPL_STD_NORM
        assert "cff:open-service-broker:v2" in VOCAB_IMPL_STDS
        concept = ORD["ImplementationStandard-cffOpenServiceBrokerV2"]
        # The concept IRI is referenced but no stub triples were minted
        assert (concept, RDF.type, SKOS.Concept) not in g

    def test_duplicate_spec_id_emits_one_stub(self):
        """The same Spec ID appearing on multiple resources produces one stub, not duplicates."""
        from rdflib.namespace import SKOS

        doc = {
            "openResourceDiscovery": "1.9",
            "apiResources": [
                {
                    "ordId": "test.stub:apiResource:ApeApi1:v1",
                    "title": "APE API 1",
                    "version": "1.0.0",
                    "releaseStatus": "active",
                    "visibility": "public",
                    "partOfPackage": "test.stub:package:TestPackage:v1",
                    "implementationStandard": "sap:ape-api:v1",
                },
                {
                    "ordId": "test.stub:apiResource:ApeApi2:v1",
                    "title": "APE API 2",
                    "version": "1.0.0",
                    "releaseStatus": "active",
                    "visibility": "public",
                    "partOfPackage": "test.stub:package:TestPackage:v1",
                    "implementationStandard": "sap:ape-api:v1",
                },
            ],
        }
        g = self._transform(doc)
        concept = ORD["ImplementationStandard-sap-ape-api-v1"]
        type_triples = list(g.triples((concept, RDF.type, SKOS.Concept)))
        assert len(type_triples) == 1
