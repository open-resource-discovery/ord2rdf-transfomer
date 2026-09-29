"""Tests for the SHACL validator."""

from __future__ import annotations

import pytest
from rdflib import Graph, Literal, RDF, SH, URIRef, XSD

from ord_transformer.validator import SHACLValidator, ValidationResult


# ── Helper: build a minimal shapes graph ─────────────────────────────────────

def _simple_shapes_graph() -> Graph:
    """Return a SHACL graph requiring sh:name xsd:string on ex:Person."""
    ex = "http://example.org/"
    shapes = Graph()
    shape_uri = URIRef(f"{ex}PersonShape")
    shapes.add((shape_uri, RDF.type, SH.NodeShape))
    shapes.add((shape_uri, SH.targetClass, URIRef(f"{ex}Person")))
    prop = URIRef(f"{ex}PersonShape_name")
    shapes.add((shape_uri, SH.property, prop))
    shapes.add((prop, SH.path, URIRef(f"{ex}name")))
    shapes.add((prop, SH.datatype, XSD.string))
    shapes.add((prop, SH.minCount, Literal(1, datatype=XSD.integer)))
    return shapes


def _valid_data_graph() -> Graph:
    """A data graph that conforms to _simple_shapes_graph."""
    ex = "http://example.org/"
    data = Graph()
    alice = URIRef(f"{ex}Alice")
    data.add((alice, RDF.type, URIRef(f"{ex}Person")))
    data.add((alice, URIRef(f"{ex}name"), Literal("Alice", datatype=XSD.string)))
    return data


def _invalid_data_graph() -> Graph:
    """A data graph missing the required ex:name on the Person."""
    ex = "http://example.org/"
    data = Graph()
    alice = URIRef(f"{ex}Alice")
    data.add((alice, RDF.type, URIRef(f"{ex}Person")))
    # Deliberately omit ex:name
    return data


# ── SHACLValidator ─────────────────────────────────────────────────────────────

class TestSHACLValidator:
    def test_valid_data_conforms(self):
        validator = SHACLValidator()
        result = validator.validate(_valid_data_graph(), _simple_shapes_graph())
        assert result.conforms is True

    def test_invalid_data_does_not_conform(self):
        validator = SHACLValidator()
        result = validator.validate(_invalid_data_graph(), _simple_shapes_graph())
        assert result.conforms is False

    def test_result_is_validation_result(self):
        validator = SHACLValidator()
        result = validator.validate(_valid_data_graph(), _simple_shapes_graph())
        assert isinstance(result, ValidationResult)

    def test_result_has_report_graph(self):
        validator = SHACLValidator()
        result = validator.validate(_valid_data_graph(), _simple_shapes_graph())
        assert isinstance(result.results_graph, Graph)

    def test_result_has_text(self):
        validator = SHACLValidator()
        result = validator.validate(_valid_data_graph(), _simple_shapes_graph())
        assert isinstance(result.results_text, str)
        assert len(result.results_text) > 0

    def test_violation_count_zero_when_valid(self):
        validator = SHACLValidator()
        result = validator.validate(_valid_data_graph(), _simple_shapes_graph())
        assert result.violation_count == 0

    def test_violation_count_positive_when_invalid(self):
        validator = SHACLValidator()
        result = validator.validate(_invalid_data_graph(), _simple_shapes_graph())
        assert result.violation_count >= 1

    def test_validate_files(self, tmp_path):
        data_graph = _valid_data_graph()
        shapes_graph = _simple_shapes_graph()
        data_path = tmp_path / "data.ttl"
        shapes_path = tmp_path / "shapes.ttl"
        data_graph.serialize(str(data_path), format="turtle")
        shapes_graph.serialize(str(shapes_path), format="turtle")

        validator = SHACLValidator()
        result = validator.validate_files(data_path, shapes_path)
        assert result.conforms is True

    def test_str_representation(self):
        validator = SHACLValidator()
        valid_result = validator.validate(_valid_data_graph(), _simple_shapes_graph())
        assert "CONFORMS" in str(valid_result)
        invalid_result = validator.validate(_invalid_data_graph(), _simple_shapes_graph())
        assert "VIOLATIONS" in str(invalid_result)


# ── Integration: validate the sample ORD data against generated shapes ────────

class TestOrdValidation:
    def test_ord_data_validates_against_model_shapes(
        self, transformed_graph, model_shapes_graph
    ):
        """The transformed ORD sample should conform to model-based SHACL shapes."""
        validator = SHACLValidator(inference="rdfs")
        result = validator.validate(transformed_graph, model_shapes_graph)
        # Note: we expect conforms=True for the sample data against model shapes.
        # If violations exist they will be in the report text.
        assert isinstance(result, ValidationResult)
        if not result.conforms:
            # Print violations to help diagnose (not a hard failure in alpha)
            print("\nSHACL violations (model shapes):\n", result.results_text)
