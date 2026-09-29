"""Unit tests for RdfSerializer.

Tests the RDF serialization functionality including:
- Basic field serialization (literals, URIs)
- List field serialization (with and without rdf_list)
- Nested model serialization
- Inverse properties
- Term builders
- Error handling
"""

from __future__ import annotations

from typing import Annotated

import pytest
from pydantic import Field
from rdflib import RDF, XSD, BNode, Literal, URIRef

from rdfantic import (
    MaterializationContext,
    PathElement,
    RdfanticBaseModel,
    RdfanticConstantValueModel,
    RdfanticFieldInfoMetaModel,
    RdfanticModelMetadata,
    RdfanticResolvableEnum,
    RdfanticSerializationError,
)
from rdfantic.exceptions import RdfanticModelError
from rdfantic.serialization.rdf_serializer import RdfSerializer

# =============================================================================
# Test Fixtures and Helpers
# =============================================================================


class SimpleContext(MaterializationContext):
    """Simple context for testing."""

    def resolve_term(self, term: str) -> URIRef | str:
        return term

    def create_uri(self, path: list[PathElement], identifier: str, element_type: str | None = None) -> URIRef:
        return URIRef(f"http://test.org/{identifier}")


class SimpleModel(RdfanticBaseModel):
    """Simple model for basic tests."""

    class Meta(RdfanticModelMetadata):
        name = "Simple"
        class_uris = {URIRef("http://test.org/Simple")}
        term_builder = lambda self: URIRef(f"http://test.org/Simple/{self.name}")  # noqa: E731

    name: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/name")}),
    ]


class ModelWithMultiplePredicates(RdfanticBaseModel):
    """Model with field bound to multiple predicates."""

    class Meta(RdfanticModelMetadata):
        name = "MultiPred"
        class_uris = {URIRef("http://test.org/MultiPred")}
        term_builder = lambda self: URIRef(f"http://test.org/MultiPred/{self.value}")  # noqa: E731

    value: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/pred1"), URIRef("http://test.org/pred2")}),
    ]


class ModelWithDatatype(RdfanticBaseModel):
    """Model with explicit datatype."""

    class Meta(RdfanticModelMetadata):
        name = "Typed"
        class_uris = {URIRef("http://test.org/Typed")}
        term_builder = lambda self: URIRef(f"http://test.org/Typed/{self.id}")  # noqa: E731

    id: str
    age: Annotated[
        int,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/age")},
            datatype=XSD.integer,
        ),
    ]
    score: Annotated[
        float,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/score")},
            datatype=XSD.decimal,
        ),
    ]


class ModelWithList(RdfanticBaseModel):
    """Model with list fields."""

    class Meta(RdfanticModelMetadata):
        name = "WithList"
        class_uris = {URIRef("http://test.org/WithList")}
        term_builder = lambda self: URIRef(f"http://test.org/WithList/{self.id}")  # noqa: E731

    id: str
    tags: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/tag")}),
    ]


class ModelWithRdfList(RdfanticBaseModel):
    """Model with rdf:List serialization."""

    class Meta(RdfanticModelMetadata):
        name = "WithRdfList"
        class_uris = {URIRef("http://test.org/WithRdfList")}
        term_builder = lambda self: URIRef(f"http://test.org/WithRdfList/{self.id}")  # noqa: E731

    id: str
    items: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/items")},
            rdf_list=True,
        ),
    ]


class NestedModel(RdfanticBaseModel):
    """Nested model for testing."""

    class Meta(RdfanticModelMetadata):
        name = "Nested"
        class_uris = {URIRef("http://test.org/Nested")}
        term_builder = lambda self: BNode(self.rdfantic.id)  # noqa: E731

    value: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/value")}),
    ]


class ParentModel(RdfanticBaseModel):
    """Parent model with nested child."""

    class Meta(RdfanticModelMetadata):
        name = "Parent"
        class_uris = {URIRef("http://test.org/Parent")}
        term_builder = lambda self: URIRef(f"http://test.org/Parent/{self.id}")  # noqa: E731

    id: str
    child: Annotated[
        NestedModel | None,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/child")}),
        Field(default=None),
    ]


class ModelWithTermBuilder(RdfanticBaseModel):
    """Model with field-level term builder."""

    class Meta(RdfanticModelMetadata):
        name = "WithTermBuilder"
        class_uris = {URIRef("http://test.org/WithTermBuilder")}
        term_builder = lambda self: URIRef(f"http://test.org/WithTermBuilder/{self.id}")  # noqa: E731

    id: str
    related: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/related")},
            str_term_builder=lambda _model, val: URIRef(f"http://test.org/Related/{val}"),
        ),
    ]


class ModelWithListTermBuilder(RdfanticBaseModel):
    """Model with list field and term builder."""

    class Meta(RdfanticModelMetadata):
        name = "WithListTermBuilder"
        class_uris = {URIRef("http://test.org/WithListTermBuilder")}
        term_builder = lambda self: URIRef(f"http://test.org/WithListTermBuilder/{self.id}")  # noqa: E731

    id: str
    refs: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/ref")},
            str_term_builder=lambda _model, val: URIRef(f"http://test.org/Ref/{val}"),
        ),
    ]


class ModelWithInverse(RdfanticBaseModel):
    """Model with inverse property."""

    class Meta(RdfanticModelMetadata):
        name = "WithInverse"
        class_uris = {URIRef("http://test.org/WithInverse")}
        term_builder = lambda self: URIRef(f"http://test.org/WithInverse/{self.id}")  # noqa: E731

    id: str
    known_by: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/knows")},
            inverse=True,
            str_term_builder=lambda _model, val: URIRef(f"http://test.org/Person/{val}"),
        ),
    ]


class ModelWithInverseLiteral(RdfanticBaseModel):
    """Model attempting inverse with literal (should fail)."""

    class Meta(RdfanticModelMetadata):
        name = "WithInverseLiteral"
        class_uris = {URIRef("http://test.org/WithInverseLiteral")}
        term_builder = lambda self: URIRef(f"http://test.org/WithInverseLiteral/{self.id}")  # noqa: E731

    id: str
    bad_inverse: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/badPred")},
            inverse=True,
            # No term_builder - will try to use literal as subject
        ),
    ]


class SampleEnum(RdfanticResolvableEnum):
    """Enum for testing."""

    OPTION_A = "a"
    OPTION_B = "b"

    @property
    def rdf_term(self) -> URIRef | Literal:
        return {
            SampleEnum.OPTION_A: URIRef("http://test.org/OptionA"),
            SampleEnum.OPTION_B: URIRef("http://test.org/OptionB"),
        }[self]


class ModelWithEnum(RdfanticBaseModel):
    """Model with enum field."""

    class Meta(RdfanticModelMetadata):
        name = "WithEnum"
        class_uris = {URIRef("http://test.org/WithEnum")}
        term_builder = lambda self: URIRef(f"http://test.org/WithEnum/{self.id}")  # noqa: E731

    id: str
    option: Annotated[
        SampleEnum,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/option")}),
    ]


class ConstantValueModel(RdfanticConstantValueModel):
    """Constant value model for testing."""

    class Meta(RdfanticModelMetadata):
        name = "ConstantValue"

    year: int
    month: int
    day: int

    @property
    def rdf_term(self) -> Literal:
        return Literal(f"{self.year}-{self.month:02d}-{self.day:02d}", datatype=XSD.date)


class ModelWithConstantValue(RdfanticBaseModel):
    """Model containing a constant value model."""

    class Meta(RdfanticModelMetadata):
        name = "WithConstantValue"
        class_uris = {URIRef("http://test.org/WithConstantValue")}
        term_builder = lambda self: URIRef(f"http://test.org/WithConstantValue/{self.id}")  # noqa: E731

    id: str
    date: Annotated[
        ConstantValueModel,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/date")}),
    ]


class ModelWithOptionalField(RdfanticBaseModel):
    """Model with optional field."""

    class Meta(RdfanticModelMetadata):
        name = "WithOptional"
        class_uris = {URIRef("http://test.org/WithOptional")}
        term_builder = lambda self: URIRef(f"http://test.org/WithOptional/{self.id}")  # noqa: E731

    id: str
    optional_value: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/optionalValue")}),
        Field(default=None),
    ]


class ModelWithMultipleClassUris(RdfanticBaseModel):
    """Model with multiple class URIs."""

    class Meta(RdfanticModelMetadata):
        name = "MultiClass"
        class_uris = {
            URIRef("http://test.org/ClassA"),
            URIRef("http://test.org/ClassB"),
        }
        term_builder = lambda self: URIRef(f"http://test.org/MultiClass/{self.id}")  # noqa: E731

    id: str


class ModelWithNoRdfFields(RdfanticBaseModel):
    """Model with no RDF-annotated fields."""

    class Meta(RdfanticModelMetadata):
        name = "NoRdfFields"
        class_uris = {URIRef("http://test.org/NoRdfFields")}
        term_builder = lambda self: URIRef(f"http://test.org/NoRdfFields/{self.id}")  # noqa: E731

    id: str
    regular_field: str = "default"


class ModelWithModelInFieldTermBuilder(RdfanticBaseModel):
    """Model whose field term builder consults a sibling field on the model."""

    class Meta(RdfanticModelMetadata):
        name = "WithModelInFieldTermBuilder"
        class_uris = {URIRef("http://test.org/WithModelInFieldTermBuilder")}
        term_builder = lambda self: URIRef(f"http://test.org/WithModelInFieldTermBuilder/{self.namespace}")  # noqa: E731

    namespace: str
    links: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/link")},
            str_term_builder=lambda model, value: URIRef(f"http://test.org/{model.namespace}/{value}"),
        ),
    ]


# =============================================================================
# Test Classes
# =============================================================================


class TestRdfSerializerBasicFields:
    """Tests for basic field serialization."""

    @pytest.fixture
    def context(self) -> SimpleContext:
        return SimpleContext()

    def test_simple_string_field(self, context: SimpleContext) -> None:
        """Test serializing a simple string field."""
        model = SimpleModel(name="test")
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/Simple/test")
        assert (subject, URIRef("http://test.org/name"), Literal("test")) in graph

    def test_class_uri_assertion(self, context: SimpleContext) -> None:
        """Test that class URIs are asserted."""
        model = SimpleModel(name="test")
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/Simple/test")
        assert (subject, RDF.type, URIRef("http://test.org/Simple")) in graph

    def test_multiple_class_uris(self, context: SimpleContext) -> None:
        """Test model with multiple class URIs."""
        model = ModelWithMultipleClassUris(id="test")
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/MultiClass/test")
        assert (subject, RDF.type, URIRef("http://test.org/ClassA")) in graph
        assert (subject, RDF.type, URIRef("http://test.org/ClassB")) in graph

    def test_multiple_predicates(self, context: SimpleContext) -> None:
        """Test field bound to multiple predicates."""
        model = ModelWithMultiplePredicates(value="test")
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/MultiPred/test")
        assert (subject, URIRef("http://test.org/pred1"), Literal("test")) in graph
        assert (subject, URIRef("http://test.org/pred2"), Literal("test")) in graph

    def test_explicit_datatype(self, context: SimpleContext) -> None:
        """Test field with explicit datatype."""
        model = ModelWithDatatype(id="test", age=30, score=95.5)
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/Typed/test")

        age_triples = list(graph.triples((subject, URIRef("http://test.org/age"), None)))
        assert len(age_triples) == 1
        assert age_triples[0][2].datatype == XSD.integer

        score_triples = list(graph.triples((subject, URIRef("http://test.org/score"), None)))
        assert len(score_triples) == 1
        assert score_triples[0][2].datatype == XSD.decimal

    def test_optional_field_present(self, context: SimpleContext) -> None:
        """Test optional field when value is present."""
        model = ModelWithOptionalField(id="test", optional_value="value")
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/WithOptional/test")
        assert (subject, URIRef("http://test.org/optionalValue"), Literal("value")) in graph

    def test_optional_field_none(self, context: SimpleContext) -> None:
        """Test optional field when value is None."""
        model = ModelWithOptionalField(id="test", optional_value=None)
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/WithOptional/test")
        triples = list(graph.triples((subject, URIRef("http://test.org/optionalValue"), None)))
        assert len(triples) == 0

    def test_empty_string_field_is_skipped(self, context: SimpleContext) -> None:
        """Empty-string field values must not be emitted as literal triples.

        ``RdfSerializer._add_to_graph`` skips ``str`` values of length zero to
        avoid polluting the graph with meaningless empty-literal triples that
        many source payloads carry (missing-but-present optional fields
        serialized as ``""``). A non-empty value is still emitted; only the
        empty-string case is filtered.
        """
        empty_model = ModelWithOptionalField(id="empty", optional_value="")
        empty_graph = RdfSerializer.model_dump_rdf(empty_model, context)
        empty_subject = URIRef("http://test.org/WithOptional/empty")
        assert not list(empty_graph.triples((empty_subject, URIRef("http://test.org/optionalValue"), None))), (
            "empty-string value must not be serialized"
        )

        # Regression guard: a non-empty value still lands in the graph so we
        # know the filter isn't over-eager.
        filled_model = ModelWithOptionalField(id="filled", optional_value="v")
        filled_graph = RdfSerializer.model_dump_rdf(filled_model, context)
        filled_subject = URIRef("http://test.org/WithOptional/filled")
        assert (filled_subject, URIRef("http://test.org/optionalValue"), Literal("v")) in filled_graph

    def test_model_with_no_rdf_fields(self, context: SimpleContext) -> None:
        """Test model where fields have no RDF annotations."""
        model = ModelWithNoRdfFields(id="test", regular_field="value")
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/NoRdfFields/test")
        # Only class assertion should be present
        assert (subject, RDF.type, URIRef("http://test.org/NoRdfFields")) in graph
        # No other predicates
        assert len(list(graph.triples((subject, None, None)))) == 1


class TestRdfSerializerListFields:
    """Tests for list field serialization."""

    @pytest.fixture
    def context(self) -> SimpleContext:
        return SimpleContext()

    def test_simple_list(self, context: SimpleContext) -> None:
        """Test serializing a simple list field."""
        model = ModelWithList(id="test", tags=["tag1", "tag2", "tag3"])
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/WithList/test")
        tag_triples = list(graph.triples((subject, URIRef("http://test.org/tag"), None)))
        assert len(tag_triples) == 3

        values = {str(t[2]) for t in tag_triples}
        assert values == {"tag1", "tag2", "tag3"}

    def test_empty_list(self, context: SimpleContext) -> None:
        """Test serializing an empty list field."""
        model = ModelWithList(id="test", tags=[])
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/WithList/test")
        tag_triples = list(graph.triples((subject, URIRef("http://test.org/tag"), None)))
        assert len(tag_triples) == 0

    def test_rdf_list_structure(self, context: SimpleContext) -> None:
        """Test rdf:List serialization structure."""
        model = ModelWithRdfList(id="test", items=["a", "b", "c"])
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/WithRdfList/test")

        # Should have exactly one items predicate pointing to list head
        items_triples = list(graph.triples((subject, URIRef("http://test.org/items"), None)))
        assert len(items_triples) == 1

        # Follow the list structure
        list_head = items_triples[0][2]
        values = []
        current = list_head

        while current != RDF.nil:
            first_triples = list(graph.triples((current, RDF.first, None)))
            assert len(first_triples) == 1
            values.append(str(first_triples[0][2]))

            rest_triples = list(graph.triples((current, RDF.rest, None)))
            assert len(rest_triples) == 1
            current = rest_triples[0][2]

        assert values == ["a", "b", "c"]

    def test_rdf_list_empty(self, context: SimpleContext) -> None:
        """Test empty rdf:List."""
        model = ModelWithRdfList(id="test", items=[])
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/WithRdfList/test")
        items_triples = list(graph.triples((subject, URIRef("http://test.org/items"), None)))
        # Empty list - no triple created
        assert len(items_triples) == 0

    def test_list_with_term_builder(self, context: SimpleContext) -> None:
        """Test list field with term builder converts strings to URIs."""
        model = ModelWithListTermBuilder(id="test", refs=["ref1", "ref2"])
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/WithListTermBuilder/test")
        ref_triples = list(graph.triples((subject, URIRef("http://test.org/ref"), None)))
        assert len(ref_triples) == 2

        refs = {t[2] for t in ref_triples}
        assert refs == {
            URIRef("http://test.org/Ref/ref1"),
            URIRef("http://test.org/Ref/ref2"),
        }

    def test_list_term_builder_reads_sibling_field(self, context: SimpleContext) -> None:
        """Term builder receives the owning model and can read sibling fields."""
        model = ModelWithModelInFieldTermBuilder(namespace="ns1", links=["a", "b"])
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/WithModelInFieldTermBuilder/ns1")
        link_triples = list(graph.triples((subject, URIRef("http://test.org/link"), None)))
        assert len(link_triples) == 2

        # Each object URI must have been built using the model.namespace value
        objects = {t[2] for t in link_triples}
        assert objects == {
            URIRef("http://test.org/ns1/a"),
            URIRef("http://test.org/ns1/b"),
        }

        # Changing namespace on a second instance must flow through the builder
        other = ModelWithModelInFieldTermBuilder(namespace="ns2", links=["a"])
        other_graph = RdfSerializer.model_dump_rdf(other, context)
        other_subject = URIRef("http://test.org/WithModelInFieldTermBuilder/ns2")
        assert (
            other_subject,
            URIRef("http://test.org/link"),
            URIRef("http://test.org/ns2/a"),
        ) in other_graph


class TestRdfSerializerNestedModels:
    """Tests for nested model serialization."""

    @pytest.fixture
    def context(self) -> SimpleContext:
        return SimpleContext()

    def test_nested_model(self, context: SimpleContext) -> None:
        """Test serializing nested model."""
        nested = NestedModel(value="nested_value")
        parent = ParentModel(id="parent", child=nested)
        graph = RdfSerializer.model_dump_rdf(parent, context)

        parent_subject = URIRef("http://test.org/Parent/parent")

        # Parent should have child predicate
        child_triples = list(graph.triples((parent_subject, URIRef("http://test.org/child"), None)))
        assert len(child_triples) == 1

        child_subject = child_triples[0][2]

        # Child should have its class and value
        assert (child_subject, RDF.type, URIRef("http://test.org/Nested")) in graph
        assert (child_subject, URIRef("http://test.org/value"), Literal("nested_value")) in graph

    def test_nested_model_none(self, context: SimpleContext) -> None:
        """Test nested model when None."""
        parent = ParentModel(id="parent", child=None)
        graph = RdfSerializer.model_dump_rdf(parent, context)

        parent_subject = URIRef("http://test.org/Parent/parent")
        child_triples = list(graph.triples((parent_subject, URIRef("http://test.org/child"), None)))
        assert len(child_triples) == 0

    def test_constant_value_model(self, context: SimpleContext) -> None:
        """Test RdfanticConstantValueModel serialization."""
        date = ConstantValueModel(year=2024, month=1, day=15)
        model = ModelWithConstantValue(id="test", date=date)
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/WithConstantValue/test")
        date_triples = list(graph.triples((subject, URIRef("http://test.org/date"), None)))
        assert len(date_triples) == 1

        date_value = date_triples[0][2]
        assert str(date_value) == "2024-01-15"
        assert date_value.datatype == XSD.date

    def test_nested_list_not_accepted(self, context: SimpleContext) -> None:
        """Test that models with nested list types raise RdfanticModelError at definition time."""
        with pytest.raises(RdfanticModelError) as exc_info:

            class Team(RdfanticBaseModel):
                class Meta(RdfanticModelMetadata):
                    name = "Team"
                    class_uris = {URIRef("http://test.org/Team")}
                    term_builder = lambda self: URIRef("http://test.org/Team/t1")  # noqa: E731

                members: Annotated[
                    list[SimpleModel | list[str]],
                    RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/member")}),
                    Field(default_factory=list),
                ]

        assert "nested list" in str(exc_info.value).lower()
        assert "members" in str(exc_info.value)

    def test_direct_nested_list_not_accepted(self, context: SimpleContext) -> None:
        """Test that models with direct nested lists (list[list[T]]) raise RdfanticModelError."""
        with pytest.raises(RdfanticModelError) as exc_info:

            class Matrix(RdfanticBaseModel):
                class Meta(RdfanticModelMetadata):
                    name = "Matrix"
                    class_uris = {URIRef("http://test.org/Matrix")}
                    term_builder = lambda self: URIRef("http://test.org/Matrix/m1")  # noqa: E731

                rows: Annotated[
                    list[list[int]],
                    RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/rows")}),
                    Field(default_factory=list),
                ]

        assert "nested list" in str(exc_info.value).lower()
        assert "rows" in str(exc_info.value)

    def test_missing_term_builder(self, context: SimpleContext) -> None:

        class Team(RdfanticBaseModel):
            class Meta(RdfanticModelMetadata):
                name = "Team"
                class_uris = {URIRef("http://test.org/Team")}
                term_builder = lambda self: URIRef("http://test.org/Team/A")

            members: Annotated[
                list[SimpleModel | str],
                RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/member")}),
                Field(default_factory=list),
            ]

        with pytest.raises(RdfanticSerializationError) as exc_info:
            team = Team(members=[SimpleModel(name="Alice"), "Bob", "Carol"])
            team.model_dump_rdf(context)

        assert "Missing term builder for mixed list type" in str(exc_info.value)


class TestRdfSerializerTermBuilders:
    """Tests for term builder functionality."""

    @pytest.fixture
    def context(self) -> SimpleContext:
        return SimpleContext()

    def test_field_term_builder(self, context: SimpleContext) -> None:
        """Test field-level term builder."""
        model = ModelWithTermBuilder(id="test", related="other")
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/WithTermBuilder/test")
        related_triples = list(graph.triples((subject, URIRef("http://test.org/related"), None)))
        assert len(related_triples) == 1
        assert related_triples[0][2] == URIRef("http://test.org/Related/other")


class TestRdfSerializerEnums:
    """Tests for enum serialization."""

    @pytest.fixture
    def context(self) -> SimpleContext:
        return SimpleContext()

    def test_resolvable_enum(self, context: SimpleContext) -> None:
        """Test RdfanticResolvableEnum serialization."""
        model = ModelWithEnum(id="test", option=SampleEnum.OPTION_A)
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/WithEnum/test")
        option_triples = list(graph.triples((subject, URIRef("http://test.org/option"), None)))
        assert len(option_triples) == 1
        assert option_triples[0][2] == URIRef("http://test.org/OptionA")


class TestRdfSerializerInverseProperties:
    """Tests for inverse property serialization."""

    @pytest.fixture
    def context(self) -> SimpleContext:
        return SimpleContext()

    def test_inverse_property(self, context: SimpleContext) -> None:
        """Test inverse property creates triple in reverse direction."""
        model = ModelWithInverse(id="alice", known_by="bob")
        graph = RdfSerializer.model_dump_rdf(model, context)

        # Triple should be: bob knows alice (not alice knows bob)
        alice = URIRef("http://test.org/WithInverse/alice")
        bob = URIRef("http://test.org/Person/bob")

        assert (bob, URIRef("http://test.org/knows"), alice) in graph
        assert (alice, URIRef("http://test.org/knows"), bob) not in graph

    def test_inverse_property_with_literal_fails(self, context: SimpleContext) -> None:
        """Test that inverse property with literal raises error."""
        model = ModelWithInverseLiteral(id="test", bad_inverse="literal_value")

        with pytest.raises(RdfanticSerializationError):
            RdfSerializer.model_dump_rdf(model, context)


class TestRdfSerializerParentChild:
    """Tests for parent-child relationship handling."""

    @pytest.fixture
    def context(self) -> SimpleContext:
        return SimpleContext()

    def test_predicates_without_parent_raises(self, context: SimpleContext) -> None:
        """Test that providing predicates without parent raises error."""
        model = SimpleModel(name="test")

        with pytest.raises(ValueError, match="No parent was specified"):
            RdfSerializer.model_dump_rdf(model, context, parent=None, predicates={URIRef("http://test.org/pred")})

    def test_parent_child_connection(self, context: SimpleContext) -> None:
        """Test that parent-child connection creates proper triples."""
        parent = SimpleModel(name="parent")
        child = SimpleModel(name="child")

        # Serialize parent first
        parent_graph = RdfSerializer.model_dump_rdf(parent, context)

        # Serialize child with parent
        child_graph = RdfSerializer.model_dump_rdf(
            child,
            context,
            parent=parent,
            predicates={URIRef("http://test.org/hasChild")},
        )

        parent_uri = URIRef("http://test.org/Simple/parent")
        child_uri = URIRef("http://test.org/Simple/child")

        assert (parent_uri, URIRef("http://test.org/hasChild"), child_uri) in child_graph


# =============================================================================
# Test Models for Multiple Annotations
# =============================================================================


class ModelWithMultipleAnnotations(RdfanticBaseModel):
    """Model with multiple RdfanticFieldInfoMetaModel annotations on a single field."""

    class Meta(RdfanticModelMetadata):
        name = "MultiAnnotation"
        class_uris = {URIRef("http://test.org/MultiAnnotation")}
        term_builder = lambda self: URIRef(f"http://test.org/MultiAnnotation/{self.id}")  # noqa: E731

    id: str
    # Two separate annotations on the same field with different predicates
    title: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/title")}),
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://purl.org/dc/terms/title")}),
    ]


class ModelWithMultipleAnnotationsDifferentDatatype(RdfanticBaseModel):
    """Model with multiple annotations using different datatypes."""

    class Meta(RdfanticModelMetadata):
        name = "MultiAnnotationDatatype"
        class_uris = {URIRef("http://test.org/MultiAnnotationDatatype")}
        term_builder = lambda self: URIRef(f"http://test.org/MultiAnnotationDatatype/{self.id}")  # noqa: E731

    id: str
    # Same field with different datatypes per annotation
    value: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/value")}),
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/typedValue")},
            datatype=XSD.string,
        ),
    ]


class ModelWithMultipleAnnotationsListField(RdfanticBaseModel):
    """Model with multiple annotations on a list field."""

    class Meta(RdfanticModelMetadata):
        name = "MultiAnnotationList"
        class_uris = {URIRef("http://test.org/MultiAnnotationList")}
        term_builder = lambda self: URIRef(f"http://test.org/MultiAnnotationList/{self.id}")  # noqa: E731

    id: str
    tags: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/tag")}),
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/label")}),
    ]


class ModelWithMultipleAnnotationsTermBuilder(RdfanticBaseModel):
    """Model with multiple annotations with different term builders."""

    class Meta(RdfanticModelMetadata):
        name = "MultiAnnotationTermBuilder"
        class_uris = {URIRef("http://test.org/MultiAnnotationTermBuilder")}
        term_builder = lambda self: URIRef(f"http://test.org/MultiAnnotationTermBuilder/{self.id}")  # noqa: E731

    id: str
    # One annotation outputs literal, one uses term builder
    related: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://test.org/relatedLiteral")}),
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/relatedUri")},
            str_term_builder=lambda _model, val: URIRef(f"http://test.org/Related/{val}"),
        ),
    ]


class ModelWithMultipleAnnotationsInverse(RdfanticBaseModel):
    """Model with multiple annotations including inverse property."""

    class Meta(RdfanticModelMetadata):
        name = "MultiAnnotationInverse"
        class_uris = {URIRef("http://test.org/MultiAnnotationInverse")}
        term_builder = lambda self: URIRef(f"http://test.org/MultiAnnotationInverse/{self.id}")  # noqa: E731

    id: str
    # One normal, one inverse - both need term builder for URIs
    partner: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/hasPartner")},
            str_term_builder=lambda _model, val: URIRef(f"http://test.org/Partner/{val}"),
        ),
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/partnerOf")},
            inverse=True,
            str_term_builder=lambda _model, val: URIRef(f"http://test.org/Partner/{val}"),
        ),
    ]


# =============================================================================
# Test Classes for Multiple Annotations
# =============================================================================


class TestRdfSerializerMultipleAnnotations:
    """Tests for fields with multiple RdfanticFieldInfoMetaModel annotations."""

    @pytest.fixture
    def context(self) -> SimpleContext:
        return SimpleContext()

    def test_multiple_annotations_creates_multiple_triples(self, context: SimpleContext) -> None:
        """Test that multiple annotations on a field create triples for each."""
        model = ModelWithMultipleAnnotations(id="test", title="My Title")
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/MultiAnnotation/test")

        # Should have triple for first annotation
        assert (subject, URIRef("http://test.org/title"), Literal("My Title")) in graph
        # Should have triple for second annotation
        assert (subject, URIRef("http://purl.org/dc/terms/title"), Literal("My Title")) in graph

    def test_multiple_annotations_with_different_datatypes(self, context: SimpleContext) -> None:
        """Test multiple annotations with different datatypes on the same field."""
        model = ModelWithMultipleAnnotationsDifferentDatatype(id="test", value="hello")
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/MultiAnnotationDatatype/test")

        # First annotation: no datatype
        value_triples = list(graph.triples((subject, URIRef("http://test.org/value"), None)))
        assert len(value_triples) == 1
        assert value_triples[0][2] == Literal("hello")

        # Second annotation: with XSD.string datatype
        typed_triples = list(graph.triples((subject, URIRef("http://test.org/typedValue"), None)))
        assert len(typed_triples) == 1
        assert typed_triples[0][2].datatype == XSD.string

    def test_multiple_annotations_on_list_field(self, context: SimpleContext) -> None:
        """Test multiple annotations on a list field creates triples for each annotation."""
        model = ModelWithMultipleAnnotationsListField(id="test", tags=["a", "b"])
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/MultiAnnotationList/test")

        # First annotation: /tag predicate
        tag_triples = list(graph.triples((subject, URIRef("http://test.org/tag"), None)))
        assert len(tag_triples) == 2
        tag_values = {str(t[2]) for t in tag_triples}
        assert tag_values == {"a", "b"}

        # Second annotation: /label predicate
        label_triples = list(graph.triples((subject, URIRef("http://test.org/label"), None)))
        assert len(label_triples) == 2
        label_values = {str(t[2]) for t in label_triples}
        assert label_values == {"a", "b"}

    def test_multiple_annotations_with_term_builder(self, context: SimpleContext) -> None:
        """Test multiple annotations where one has term builder and one doesn't."""
        model = ModelWithMultipleAnnotationsTermBuilder(id="test", related="other")
        graph = RdfSerializer.model_dump_rdf(model, context)

        subject = URIRef("http://test.org/MultiAnnotationTermBuilder/test")

        # First annotation: literal value
        literal_triples = list(graph.triples((subject, URIRef("http://test.org/relatedLiteral"), None)))
        assert len(literal_triples) == 1
        assert literal_triples[0][2] == Literal("other")

        # Second annotation: URI via term builder
        uri_triples = list(graph.triples((subject, URIRef("http://test.org/relatedUri"), None)))
        assert len(uri_triples) == 1
        assert uri_triples[0][2] == URIRef("http://test.org/Related/other")

    def test_multiple_annotations_with_inverse(self, context: SimpleContext) -> None:
        """Test multiple annotations with normal and inverse directions."""
        model = ModelWithMultipleAnnotationsInverse(id="alice", partner="bob")
        graph = RdfSerializer.model_dump_rdf(model, context)

        alice = URIRef("http://test.org/MultiAnnotationInverse/alice")
        bob = URIRef("http://test.org/Partner/bob")

        # First annotation: normal direction (alice hasPartner bob)
        assert (alice, URIRef("http://test.org/hasPartner"), bob) in graph

        # Second annotation: inverse direction (bob partnerOf alice)
        assert (bob, URIRef("http://test.org/partnerOf"), alice) in graph


# =============================================================================
# Test Models for Field class_uris
# =============================================================================


class ModelWithFieldClassUris(RdfanticBaseModel):
    """Model with class_uris on a field to type the referenced node."""

    class Meta(RdfanticModelMetadata):
        name = "WithFieldClassUris"
        class_uris = {URIRef("http://test.org/WithFieldClassUris")}
        term_builder = lambda self: URIRef(f"http://test.org/WithFieldClassUris/{self.id}")  # noqa: E731

    id: str
    author: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/author")},
            str_term_builder=lambda _model, name: URIRef(f"http://test.org/Person/{name}"),
            class_uris={URIRef("http://test.org/Person")},
        ),
    ]


class ModelWithFieldMultipleClassUris(RdfanticBaseModel):
    """Model with multiple class_uris on a field."""

    class Meta(RdfanticModelMetadata):
        name = "WithFieldMultipleClassUris"
        class_uris = {URIRef("http://test.org/WithFieldMultipleClassUris")}
        term_builder = lambda self: URIRef(f"http://test.org/WithFieldMultipleClassUris/{self.id}")  # noqa: E731

    id: str
    creator: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/creator")},
            str_term_builder=lambda _model, name: URIRef(f"http://test.org/Agent/{name}"),
            class_uris={URIRef("http://test.org/Person"), URIRef("http://test.org/Agent")},
        ),
    ]


class ModelWithFieldClassUrisLiteral(RdfanticBaseModel):
    """Model with class_uris on a literal field (should raise error)."""

    class Meta(RdfanticModelMetadata):
        name = "WithFieldClassUrisLiteral"
        class_uris = {URIRef("http://test.org/WithFieldClassUrisLiteral")}
        term_builder = lambda self: URIRef(f"http://test.org/WithFieldClassUrisLiteral/{self.id}")  # noqa: E731

    id: str
    # class_uris specified but field is a literal - should raise error
    name: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/name")},
            class_uris={URIRef("http://test.org/SomeType")},
        ),
    ]


class ModelWithFieldClassUrisList(RdfanticBaseModel):
    """Model with class_uris on a list field with term builder."""

    class Meta(RdfanticModelMetadata):
        name = "WithFieldClassUrisList"
        class_uris = {URIRef("http://test.org/WithFieldClassUrisList")}
        term_builder = lambda self: URIRef(f"http://test.org/WithFieldClassUrisList/{self.id}")  # noqa: E731

    id: str
    authors: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/author")},
            str_term_builder=lambda _model, name: URIRef(f"http://test.org/Person/{name}"),
            class_uris={URIRef("http://test.org/Person")},
        ),
    ]


class ModelWithFieldClassUrisRdfList(RdfanticBaseModel):
    """Model with class_uris on an rdf:List field (should raise error for literals)."""

    class Meta(RdfanticModelMetadata):
        name = "WithFieldClassUrisRdfList"
        class_uris = {URIRef("http://test.org/WithFieldClassUrisRdfList")}
        term_builder = lambda self: URIRef(f"http://test.org/WithFieldClassUrisRdfList/{self.id}")  # noqa: E731

    id: str
    # rdf_list with class_uris on literal items - should raise error
    items: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://test.org/items")},
            rdf_list=True,
            class_uris={URIRef("http://test.org/Item")},
        ),
    ]


# =============================================================================
# Test Classes for Field class_uris
# =============================================================================


class TestRdfSerializerFieldClassUris:
    """Tests for class_uris on RdfanticFieldInfoMetaModel."""

    @pytest.fixture
    def context(self) -> SimpleContext:
        return SimpleContext()

    def test_field_class_uris_adds_type_triple(self, context: SimpleContext) -> None:
        """Test that class_uris on a field adds rdf:type triples for the field value."""
        model = ModelWithFieldClassUris(id="book1", author="alice")
        graph = RdfSerializer.model_dump_rdf(model, context)

        book_uri = URIRef("http://test.org/WithFieldClassUris/book1")
        author_uri = URIRef("http://test.org/Person/alice")

        # The author triple should exist
        assert (book_uri, URIRef("http://test.org/author"), author_uri) in graph

        # The author node should be typed as Person
        assert (author_uri, RDF.type, URIRef("http://test.org/Person")) in graph

    def test_field_multiple_class_uris(self, context: SimpleContext) -> None:
        """Test that multiple class_uris on a field all get added as type triples."""
        model = ModelWithFieldMultipleClassUris(id="doc1", creator="bob")
        graph = RdfSerializer.model_dump_rdf(model, context)

        creator_uri = URIRef("http://test.org/Agent/bob")

        # Both types should be present
        assert (creator_uri, RDF.type, URIRef("http://test.org/Person")) in graph
        assert (creator_uri, RDF.type, URIRef("http://test.org/Agent")) in graph

    def test_field_class_uris_raises_for_literals(self, context: SimpleContext) -> None:
        """Test that class_uris raises an error when field value is a literal."""
        model = ModelWithFieldClassUrisLiteral(id="test", name="Test Name")

        with pytest.raises(RdfanticSerializationError, match="Cannot add class_uris to a Literal node"):
            RdfSerializer.model_dump_rdf(model, context)

    def test_field_class_uris_on_list_with_term_builder(self, context: SimpleContext) -> None:
        """Test that class_uris works for each item in a list with term builder."""
        model = ModelWithFieldClassUrisList(id="book1", authors=["alice", "bob"])
        graph = RdfSerializer.model_dump_rdf(model, context)

        alice_uri = URIRef("http://test.org/Person/alice")
        bob_uri = URIRef("http://test.org/Person/bob")

        # Both authors should be typed as Person
        assert (alice_uri, RDF.type, URIRef("http://test.org/Person")) in graph
        assert (bob_uri, RDF.type, URIRef("http://test.org/Person")) in graph

    def test_field_class_uris_on_rdf_list_raises_for_literals(self, context: SimpleContext) -> None:
        """Test that class_uris on rdf:List items that are literals raises an error."""
        model = ModelWithFieldClassUrisRdfList(id="test", items=["a", "b", "c"])

        with pytest.raises(RdfanticSerializationError, match="Cannot add class_uris to a Literal node"):
            RdfSerializer.model_dump_rdf(model, context)
