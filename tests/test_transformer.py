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
