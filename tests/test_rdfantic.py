"""Unit tests for the bundled RDFantic framework (src/rdfantic/)."""

from __future__ import annotations

from typing import Annotated, List, Optional

import pytest
from pydantic import Field
from rdflib import BNode, Graph, Literal, RDF, RDFS, SH, URIRef, XSD

from rdfantic import (
    RdfanticBaseModel,
    RdfanticFieldInfoMetaModel,
    RdfanticModelMetadata,
    ShaclMaterializationContext,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

EXAMPLE = URIRef("http://example.org/")
PERSON_CLASS = URIRef("http://example.org/Person")
KNOWS = URIRef("http://example.org/knows")


def ctx() -> ShaclMaterializationContext:
    return ShaclMaterializationContext("http://example.org/")


# ── Simple model fixture ──────────────────────────────────────────────────────

class Person(RdfanticBaseModel):
    class Meta(RdfanticModelMetadata):
        name = "Person"
        class_uris = {PERSON_CLASS}
        term_builder = lambda self: URIRef(f"http://example.org/people/{self.name}")  # noqa: E731

    name: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={RDFS.label}),
        Field(description="Person name"),
    ]
    age: Annotated[
        Optional[int],
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/age")}),
        Field(default=None),
    ]
    homepage: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://example.org/homepage")},
            datatype=XSD.anyURI,
        ),
        Field(default=None),
    ]
    aliases: Annotated[
        Optional[List[str]],
        RdfanticFieldInfoMetaModel(predicates={RDFS.label}),
        Field(default=None),
    ]
    knows: Annotated[
        Optional["Person"],
        RdfanticFieldInfoMetaModel(predicates={KNOWS}),
        Field(default=None),
    ]


# ── ShaclMaterializationContext ────────────────────────────────────────────────

class TestShaclMaterializationContext:
    def test_stores_base_uri(self):
        c = ShaclMaterializationContext("http://example.org/")
        assert c.base_uri == "http://example.org/"

    def test_empty_base_uri_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            ShaclMaterializationContext("")


# ── model_dump_rdf ─────────────────────────────────────────────────────────────

class TestModelDumpRdf:
    def test_returns_graph(self):
        alice = Person(name="Alice")
        g = alice.model_dump_rdf(context=ctx(), parent=None, predicates=set())
        assert isinstance(g, Graph)

    def test_rdf_type_triple(self):
        alice = Person(name="Alice")
        g = alice.model_dump_rdf(context=ctx(), parent=None, predicates=set())
        subject = URIRef("http://example.org/people/Alice")
        assert (subject, RDF.type, PERSON_CLASS) in g

    def test_string_literal_field(self):
        alice = Person(name="Alice")
        g = alice.model_dump_rdf(context=ctx(), parent=None, predicates=set())
        subject = URIRef("http://example.org/people/Alice")
        labels = list(g.objects(subject, RDFS.label))
        assert Literal("Alice", datatype=XSD.string) in labels

    def test_optional_field_emitted_when_set(self):
        alice = Person(name="Alice", age=30)
        g = alice.model_dump_rdf(context=ctx(), parent=None, predicates=set())
        subject = URIRef("http://example.org/people/Alice")
        ages = list(g.objects(subject, URIRef("http://example.org/age")))
        assert len(ages) == 1
        assert str(ages[0]) == "30"

    def test_optional_field_absent_when_none(self):
        alice = Person(name="Alice")  # age=None
        g = alice.model_dump_rdf(context=ctx(), parent=None, predicates=set())
        subject = URIRef("http://example.org/people/Alice")
        ages = list(g.objects(subject, URIRef("http://example.org/age")))
        assert ages == []

    def test_explicit_datatype(self):
        alice = Person(name="Alice", homepage="http://alice.example.org/")
        g = alice.model_dump_rdf(context=ctx(), parent=None, predicates=set())
        subject = URIRef("http://example.org/people/Alice")
        homepages = list(g.objects(subject, URIRef("http://example.org/homepage")))
        assert len(homepages) == 1
        assert homepages[0].datatype == XSD.anyURI

    def test_list_field(self):
        alice = Person(name="Alice", aliases=["Alicia", "Ali"])
        g = alice.model_dump_rdf(context=ctx(), parent=None, predicates=set())
        subject = URIRef("http://example.org/people/Alice")
        labels = list(g.objects(subject, RDFS.label))
        assert Literal("Alicia", datatype=XSD.string) in labels
        assert Literal("Ali", datatype=XSD.string) in labels

    def test_nested_model(self):
        bob = Person(name="Bob")
        alice = Person(name="Alice", knows=bob)
        g = alice.model_dump_rdf(context=ctx(), parent=None, predicates=set())
        alice_uri = URIRef("http://example.org/people/Alice")
        bob_uri = URIRef("http://example.org/people/Bob")
        # Alice knows Bob
        assert (alice_uri, KNOWS, bob_uri) in g
        # Bob's type is also in the graph (nested serialization)
        assert (bob_uri, RDF.type, PERSON_CLASS) in g

    def test_parent_linking(self):
        """When parent + predicates are supplied, the parent→child triple is emitted."""
        alice = Person(name="Alice")
        parent_uri = URIRef("http://example.org/groups/Admins")
        HAS_MEMBER = URIRef("http://example.org/hasMember")
        g = alice.model_dump_rdf(
            context=ctx(), parent=parent_uri, predicates={HAS_MEMBER}
        )
        alice_uri = URIRef("http://example.org/people/Alice")
        assert (parent_uri, HAS_MEMBER, alice_uri) in g

    def test_uri_factory(self):
        """uri_factory converts a string value to a URIRef in the graph."""
        MY_PRED = URIRef("http://example.org/relatedTo")

        class Org(RdfanticBaseModel):
            class Meta(RdfanticModelMetadata):
                name = "Org"
                class_uris = {URIRef("http://example.org/Org")}
                term_builder = lambda self: URIRef(f"http://example.org/orgs/{self.org_id}")  # noqa: E731

            org_id: Annotated[
                str,
                RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/id")}),
                Field(),
            ]
            related: Annotated[
                Optional[str],
                RdfanticFieldInfoMetaModel(
                    predicates={MY_PRED},
                    uri_factory=lambda v: URIRef(f"http://example.org/orgs/{v}"),
                ),
                Field(default=None),
            ]

        org = Org(org_id="acme", related="partner-corp")
        g = org.model_dump_rdf(context=ctx(), parent=None, predicates=set())
        subject = URIRef("http://example.org/orgs/acme")
        related_obj = URIRef("http://example.org/orgs/partner-corp")
        assert (subject, MY_PRED, related_obj) in g


# ── model_dump_shacl ───────────────────────────────────────────────────────────

class TestModelDumpShacl:
    def test_returns_graph(self):
        g = Person.model_dump_shacl()
        assert isinstance(g, Graph)
        assert len(g) > 0

    def test_node_shape_created(self):
        g = Person.model_dump_shacl()
        shapes = list(g.subjects(RDF.type, SH.NodeShape))
        assert len(shapes) == 1

    def test_target_class(self):
        g = Person.model_dump_shacl()
        shape = next(g.subjects(RDF.type, SH.NodeShape))
        target_classes = list(g.objects(shape, SH.targetClass))
        assert PERSON_CLASS in target_classes

    def test_property_shape_for_name(self):
        g = Person.model_dump_shacl()
        shape = next(g.subjects(RDF.type, SH.NodeShape))
        prop_paths = [
            g.value(ps, SH.path)
            for ps in g.objects(shape, SH.property)
        ]
        assert RDFS.label in prop_paths

    def test_required_field_min_count(self):
        """'name' is required — sh:minCount 1 should be present."""
        g = Person.model_dump_shacl()
        shape = next(g.subjects(RDF.type, SH.NodeShape))
        for ps in g.objects(shape, SH.property):
            if g.value(ps, SH.path) == RDFS.label:
                min_count = g.value(ps, SH.minCount)
                assert min_count is not None
                assert int(str(min_count)) >= 1
                break

    def test_optional_field_no_min_count(self):
        """'age' is Optional — sh:minCount should NOT be 1."""
        AGE_PRED = URIRef("http://example.org/age")
        g = Person.model_dump_shacl()
        shape = next(g.subjects(RDF.type, SH.NodeShape))
        for ps in g.objects(shape, SH.property):
            if g.value(ps, SH.path) == AGE_PRED:
                min_count = g.value(ps, SH.minCount)
                assert min_count is None or int(str(min_count)) == 0
                break

    def test_xsd_datatype_inferred(self):
        """Integer field should have sh:datatype xsd:integer."""
        AGE_PRED = URIRef("http://example.org/age")
        g = Person.model_dump_shacl()
        shape = next(g.subjects(RDF.type, SH.NodeShape))
        for ps in g.objects(shape, SH.property):
            if g.value(ps, SH.path) == AGE_PRED:
                dt = g.value(ps, SH.datatype)
                assert dt == XSD.integer
                break
