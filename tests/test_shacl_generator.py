"""Tests for SHACL shape generation (model-based and vocabulary-based)."""

from __future__ import annotations

import pytest
from rdflib import RDF, SH, Graph

from ord_transformer.namespaces import ORD
from ord_transformer.shacl_generator import (
    generate_combined_shapes,
    _generate_model_shapes,
    _generate_vocab_shapes,
)


class TestGenerateModelShapes:
    def test_returns_graph(self, model_shapes_graph):
        assert isinstance(model_shapes_graph, Graph)

    def test_graph_non_empty(self, model_shapes_graph):
        assert len(model_shapes_graph) > 0

    def test_contains_node_shapes(self, model_shapes_graph):
        shapes = list(model_shapes_graph.subjects(RDF.type, SH.NodeShape))
        assert len(shapes) >= 5  # Document, Package, Bundle, ApiResource, EventResource, etc.

    def test_package_shape_exists(self, model_shapes_graph):
        """PackageShape must target ord:Package."""
        found = any(
            (shape, SH.targetClass, ORD.Package) in model_shapes_graph
            for shape in model_shapes_graph.subjects(RDF.type, SH.NodeShape)
        )
        assert found, "No NodeShape targeting ord:Package found"

    def test_api_resource_shape_exists(self, model_shapes_graph):
        found = any(
            (shape, SH.targetClass, ORD.APIResource) in model_shapes_graph
            for shape in model_shapes_graph.subjects(RDF.type, SH.NodeShape)
        )
        assert found

    def test_property_shapes_present(self, model_shapes_graph):
        """Each NodeShape should have at least one sh:property."""
        for shape in model_shapes_graph.subjects(RDF.type, SH.NodeShape):
            props = list(model_shapes_graph.objects(shape, SH.property))
            assert len(props) >= 1, f"Shape {shape} has no sh:property"

    def test_property_shape_has_path(self, model_shapes_graph):
        """Every sh:PropertyShape must have sh:path."""
        for shape in model_shapes_graph.subjects(RDF.type, SH.NodeShape):
            for prop in model_shapes_graph.objects(shape, SH.property):
                path = model_shapes_graph.value(prop, SH.path)
                assert path is not None, f"PropertyShape {prop} missing sh:path"


class TestGenerateVocabShapes:
    def test_returns_graph(self, vocab_shapes_graph):
        assert isinstance(vocab_shapes_graph, Graph)

    def test_graph_non_empty(self, vocab_shapes_graph):
        assert len(vocab_shapes_graph) > 0

    def test_contains_node_shapes(self, vocab_shapes_graph):
        shapes = list(vocab_shapes_graph.subjects(RDF.type, SH.NodeShape))
        assert len(shapes) >= 10  # vocab has many classes

    def test_shapes_target_ord_classes(self, vocab_shapes_graph):
        """All targetClass values should be in the ORD namespace."""
        ord_ns = str(ORD)
        for shape in vocab_shapes_graph.subjects(RDF.type, SH.NodeShape):
            for tc in vocab_shapes_graph.objects(shape, SH.targetClass):
                assert str(tc).startswith(ord_ns), (
                    f"Non-ORD targetClass {tc} in vocab shapes"
                )

    def test_package_vocab_shape_exists(self, vocab_shapes_graph):
        found = any(
            (shape, SH.targetClass, ORD.Package) in vocab_shapes_graph
            for shape in vocab_shapes_graph.subjects(RDF.type, SH.NodeShape)
        )
        assert found

    def test_property_paths_are_uris(self, vocab_shapes_graph):
        """All sh:path values in vocab shapes should be URIRefs."""
        from rdflib import URIRef
        for shape in vocab_shapes_graph.subjects(RDF.type, SH.NodeShape):
            for prop in vocab_shapes_graph.objects(shape, SH.property):
                path = vocab_shapes_graph.value(prop, SH.path)
                if path is not None:
                    assert isinstance(path, URIRef), f"sh:path {path} is not a URIRef"

    def test_vocab_file_not_found_raises(self, tmp_path):
        from ord_transformer.exceptions import VocabularyNotFoundError

        with pytest.raises(VocabularyNotFoundError):
            _generate_vocab_shapes(tmp_path / "nonexistent.ttl")


class TestGenerateCombinedShapes:
    def test_combined_larger_than_model_only(self, vocab_path):
        model_g = _generate_model_shapes()
        combined_g = generate_combined_shapes(vocab_path=vocab_path)
        assert len(combined_g) > len(model_g)

    def test_combined_without_vocab_equals_model(self):
        model_g = _generate_model_shapes()
        combined_g = generate_combined_shapes(vocab_path=None)
        # Both should have the same NodeShapes (only model shapes)
        model_shapes = set(model_g.subjects(RDF.type, SH.NodeShape))
        combined_shapes = set(combined_g.subjects(RDF.type, SH.NodeShape))
        # Combined may add more from vocab; without vocab they should match
        assert model_shapes == combined_shapes
