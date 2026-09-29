"""Tests for ORD entity models — instantiation, alias handling, RDF output."""

from __future__ import annotations

import pytest
from rdflib import RDF, URIRef

from ord_transformer.models import (
    ApiResource,
    ConsumptionBundle,
    EntityType,
    EventResource,
    OrdDocument,
    Package,
    Vendor,
)
from ord_transformer.namespaces import ORD, ord_id_to_uri


# ── OrdDocument ───────────────────────────────────────────────────────────────

class TestOrdDocument:
    def test_from_dict(self):
        doc = OrdDocument.model_validate({
            "openResourceDiscovery": "1.9",
            "baseUrl": "https://example.com",
        })
        assert doc.open_resource_discovery == "1.9"
        assert doc.base_url == "https://example.com"

    def test_camelcase_alias(self):
        doc = OrdDocument.model_validate({"openResourceDiscovery": "1.9"})
        assert doc.open_resource_discovery == "1.9"

    def test_optional_fields_default_none(self):
        doc = OrdDocument.model_validate({"openResourceDiscovery": "1.0"})
        assert doc.base_url is None
        assert doc.policy_level is None

    def test_rdf_type(self, context):
        doc = OrdDocument.model_validate({
            "openResourceDiscovery": "1.9",
            "baseUrl": "https://example.com",
        })
        g = doc.model_dump_rdf(context=context, parent=None, predicates=set())
        doc_uri = URIRef("https://example.com")
        assert (doc_uri, RDF.type, ORD.Document) in g


# ── Package ───────────────────────────────────────────────────────────────────

class TestPackage:
    PKG_DATA = {
        "ordId": "sap.example:package:TestPkg:v1",
        "title": "Test Package",
        "version": "1.0.0",
    }

    def test_from_dict(self):
        pkg = Package.model_validate(self.PKG_DATA)
        assert pkg.ord_id == "sap.example:package:TestPkg:v1"
        assert pkg.title == "Test Package"
        assert pkg.version == "1.0.0"

    def test_optional_vendor_absent(self):
        pkg = Package.model_validate(self.PKG_DATA)
        assert pkg.vendor is None

    def test_optional_vendor_present(self):
        data = {**self.PKG_DATA, "vendor": "sap:vendor:SAP:"}
        pkg = Package.model_validate(data)
        assert pkg.vendor == "sap:vendor:SAP:"

    def test_rdf_type(self, context):
        pkg = Package.model_validate(self.PKG_DATA)
        g = pkg.model_dump_rdf(context=context, parent=None, predicates=set())
        subject = ord_id_to_uri("sap.example:package:TestPkg:v1")
        assert (subject, RDF.type, ORD.Package) in g

    def test_vendor_uri_in_graph(self, context):
        """vendor ORD ID should appear as a URI reference, not a literal."""
        data = {**self.PKG_DATA, "vendor": "sap:vendor:SAP:"}
        pkg = Package.model_validate(data)
        g = pkg.model_dump_rdf(context=context, parent=None, predicates=set())
        subject = ord_id_to_uri("sap.example:package:TestPkg:v1")
        vendor_objs = list(g.objects(subject, ORD.vendor))
        assert len(vendor_objs) == 1
        assert isinstance(vendor_objs[0], URIRef), "vendor should be a URI, not a literal"

    def test_extra_fields_ignored(self):
        """Unknown JSON keys should not cause a validation error."""
        data = {**self.PKG_DATA, "unknownKey": "some_value"}
        pkg = Package.model_validate(data)
        assert pkg.ord_id == "sap.example:package:TestPkg:v1"


# ── ConsumptionBundle ─────────────────────────────────────────────────────────

class TestConsumptionBundle:
    CB_DATA = {
        "ordId": "sap.example:consumptionBundle:DefaultBundle:v1",
        "title": "Default Bundle",
        "version": "1.0.0",
    }

    def test_from_dict(self):
        cb = ConsumptionBundle.model_validate(self.CB_DATA)
        assert cb.ord_id == "sap.example:consumptionBundle:DefaultBundle:v1"

    def test_rdf_type(self, context):
        cb = ConsumptionBundle.model_validate(self.CB_DATA)
        g = cb.model_dump_rdf(context=context, parent=None, predicates=set())
        subject = ord_id_to_uri(self.CB_DATA["ordId"])
        assert (subject, RDF.type, ORD.ConsumptionBundle) in g


# ── ApiResource ───────────────────────────────────────────────────────────────

class TestApiResource:
    API_DATA = {
        "ordId": "sap.example:apiResource:ProductAPI:v1",
        "title": "Product API",
        "version": "1.0.0",
        "releaseStatus": "active",
        "visibility": "public",
        "partOfPackage": "sap.example:package:CorePackage:v1",
        "apiProtocol": "rest",
    }

    def test_from_dict(self):
        api = ApiResource.model_validate(self.API_DATA)
        assert api.ord_id == "sap.example:apiResource:ProductAPI:v1"
        assert api.release_status == "active"
        assert api.visibility == "public"
        assert api.part_of_package == "sap.example:package:CorePackage:v1"

    def test_rdf_type(self, context):
        api = ApiResource.model_validate(self.API_DATA)
        g = api.model_dump_rdf(context=context, parent=None, predicates=set())
        subject = ord_id_to_uri(self.API_DATA["ordId"])
        assert (subject, RDF.type, ORD.APIResource) in g

    def test_part_of_package_is_uri(self, context):
        """partOfPackage should be emitted as a URI, not a literal."""
        api = ApiResource.model_validate(self.API_DATA)
        g = api.model_dump_rdf(context=context, parent=None, predicates=set())
        subject = ord_id_to_uri(self.API_DATA["ordId"])
        pkg_objs = list(g.objects(subject, ORD.partOfPackage))
        assert len(pkg_objs) == 1
        assert isinstance(pkg_objs[0], URIRef)


# ── EventResource ─────────────────────────────────────────────────────────────

class TestEventResource:
    EVT_DATA = {
        "ordId": "sap.example:eventResource:BPEvents:v1",
        "title": "Business Partner Events",
        "version": "1.0.0",
        "releaseStatus": "active",
        "visibility": "public",
        "partOfPackage": "sap.example:package:CorePackage:v1",
    }

    def test_from_dict(self):
        evt = EventResource.model_validate(self.EVT_DATA)
        assert evt.ord_id == "sap.example:eventResource:BPEvents:v1"

    def test_rdf_type(self, context):
        evt = EventResource.model_validate(self.EVT_DATA)
        g = evt.model_dump_rdf(context=context, parent=None, predicates=set())
        subject = ord_id_to_uri(self.EVT_DATA["ordId"])
        assert (subject, RDF.type, ORD.EventResource) in g


# ── EntityType ────────────────────────────────────────────────────────────────

class TestEntityType:
    ET_DATA = {
        "ordId": "sap.example:entityType:Product:v1",
        "title": "Product",
        "version": "1.0.0",
        "releaseStatus": "active",
        "visibility": "public",
        "partOfPackage": "sap.example:package:CorePackage:v1",
        "level": "aggregate",
    }

    def test_from_dict(self):
        et = EntityType.model_validate(self.ET_DATA)
        assert et.level == "aggregate"

    def test_rdf_type(self, context):
        et = EntityType.model_validate(self.ET_DATA)
        g = et.model_dump_rdf(context=context, parent=None, predicates=set())
        subject = ord_id_to_uri(self.ET_DATA["ordId"])
        assert (subject, RDF.type, ORD.OrdEntityType) in g


# ── Vendor ────────────────────────────────────────────────────────────────────

class TestVendor:
    def test_from_dict(self):
        v = Vendor.model_validate({"ordId": "sap:vendor:SAP:", "title": "SAP SE"})
        assert v.title == "SAP SE"

    def test_rdf_type(self, context):
        v = Vendor.model_validate({"ordId": "sap:vendor:SAP:", "title": "SAP SE"})
        g = v.model_dump_rdf(context=context, parent=None, predicates=set())
        subject = ord_id_to_uri("sap:vendor:SAP:")
        assert (subject, RDF.type, ORD.Vendor) in g
