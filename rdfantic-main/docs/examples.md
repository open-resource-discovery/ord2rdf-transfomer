# Complete Example

The following example exercises every annotation feature: basic fields, multiple predicates, datatypes, term builders, RDF lists, optional fields, nested models, and both enum kinds.

```python
from __future__ import annotations

from typing import Annotated

from pydantic import Field
from rdflib import BNode, Literal, RDFS, URIRef, XSD

from rdfantic import (
    RdfanticBaseModel,
    RdfanticConstantValueModel,
    RdfanticFieldInfoMetaModel,
    RdfanticLiteralEnum,
    RdfanticModelMetadata,
    RdfanticResolvableEnum,
    ShaclMaterializationContext,
)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Job(RdfanticLiteralEnum):
    """Literal enum — values become xsd:string literals."""

    SE = "Software Engineer"
    DE = "Data Engineer"
    KE = "Knowledge Engineer"


class CustomBool(RdfanticLiteralEnum):
    """Literal enum with a custom XSD datatype."""

    YES = "true"
    NO = "false"

    @property
    def datatype(self) -> str | None:
        return str(XSD.boolean)


class Gender(RdfanticResolvableEnum):
    """Resolvable enum — each member maps to a URI."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"

    @property
    def rdf_term(self) -> URIRef | Literal:
        return {
            Gender.MALE: URIRef("http://example.org/Gender/Male"),
            Gender.FEMALE: URIRef("http://example.org/Gender/Female"),
            Gender.OTHER: URIRef("http://example.org/Gender/Other"),
            Gender.UNKNOWN: URIRef("http://example.org/Gender/Unknown"),
        }[self]


# ---------------------------------------------------------------------------
# Constant-value model — fields are NOT annotated; the whole model is a value
# ---------------------------------------------------------------------------

class Birthdate(RdfanticConstantValueModel):
    """A date emitted as a single literal — no predicates per field."""

    class Meta(RdfanticModelMetadata):
        name = "Birthdate"

    day: int = Field(description="Birthdate's day", ge=1, le=31)
    month: int = Field(description="Birthdate's month", ge=1, le=12)
    year: int = Field(description="Birthdate's year", ge=1, le=9999)

    @property
    def rdf_term(self) -> URIRef | Literal:
        return Literal(f"{self.year}-{self.month:02d}-{self.day:02d}")


# ---------------------------------------------------------------------------
# Address — uses a blank node as its subject
# ---------------------------------------------------------------------------

class Address(RdfanticBaseModel):
    """A postal address represented as a blank node."""

    class Meta(RdfanticModelMetadata):
        name = "Address"
        class_uris = {URIRef("http://example.org/Address")}
        term_builder = lambda self: BNode(self.rdfantic.id)  # noqa: E731
        shape_name = "Addr"  # Custom shape name (default would be "AddressShape")

    street: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Address/street")}),
        Field(description="Address' street"),
    ]
    number: Annotated[
        int,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Address/number")}),
        Field(description="Address' number"),
    ]
    zip_code: Annotated[
        int,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Address/zip_code")}),
        Field(description="Address' zip code"),
    ]
    city: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Address/city")}),
        Field(description="Address' city"),
    ]


# ---------------------------------------------------------------------------
# Person — exercises every annotation feature
# ---------------------------------------------------------------------------

class Person(RdfanticBaseModel):
    """A person with a rich set of RDF-annotated fields."""

    class Meta(RdfanticModelMetadata):
        name = "Person"
        class_uris = {URIRef("http://example.org/Person")}
        term_builder = lambda self: URIRef(f"http://example.org/Person/{self.name}")  # noqa: E731
        instance_name = lambda self: f"{self.name}"  # Used for path building in nested models

    # Multiple predicates — emitted once for each
    name: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://example.org/Person/name"), RDFS.label},
        ),
        Field(description="Person's name"),
    ]

    # Resolvable enum field
    gender: Annotated[
        Gender,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/gender")}),
        Field(default=Gender.UNKNOWN, description="Person's gender"),
    ]

    # Numeric field with explicit datatype + Pydantic validation
    age: Annotated[
        float | int,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://example.org/Person/age")},
            datatype=XSD.integer,
        ),
        Field(description="Person's age", ge=0, le=130),
    ]

    # Nested constant-value model
    dob: Annotated[
        Birthdate,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/birthdate")}),
        Field(description="Date of birth"),
    ]

    # List with str_term_builder — strings → URIs
    knows: Annotated[
        list[Person | str],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://example.org/Person/knows")},
            str_term_builder=lambda _model, person_name: URIRef(f"http://example.org/Person/{person_name}"),
        ),
        Field(description="People this person knows"),
    ]

    # Scalar with str_term_builder — receives the field value directly
    father: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://example.org/Person/father")},
            str_term_builder=lambda _model, father_name: URIRef(f"http://example.org/Person/{father_name}"),
        ),
        Field(description="Father's name"),
    ]

    # List of literal-enum values with cardinality constraints
    jobs: Annotated[
        list[Job],
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/job")}),
        Field(description="Person's jobs", min_length=1, max_length=100),
    ]

    # Optional bool
    baptized: Annotated[
        bool | None,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/baptized")}),
        Field(default=None, description="Person's baptized status"),
    ]

    # Optional literal-enum (with custom datatype)
    right_handed: Annotated[
        CustomBool | None,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/right_handed")}),
        Field(default=None, description="Whether the person is right-handed"),
    ]

    # Optional list of strings
    nickname: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/nickname")}),
        Field(default_factory=list, description="Person's nicknames"),
    ]

    # Optional nested model
    address: Annotated[
        Address | None,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/address")}),
        Field(default=None, description="Person's address"),
    ]

    # RDF list — emitted as ( "Surfing" "Cooking" )
    hobby: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://example.org/Person/hobby")},
            rdf_list=True,
        ),
        Field(default_factory=list, description="Person's hobbies"),
    ]
```

## Using the Model

```python
# 1. Create a context
context = ShaclMaterializationContext("http://example.org/")

# 2. Build an instance
alice = Person(
   name="Alice",
   gender=Gender.FEMALE,
   age=30,
   dob=Birthdate(day=15, month=3, year=1996),
   knows=["Bob"],
   father="Charlie",
   jobs=[Job.SE, Job.KE],
   baptized=True,
   right_handed=CustomBool.YES,
   nickname=["Al", "Ali"],
   address=Address(street="Main Street", number=42, zip_code=12345, city="Springfield"),
   hobby=["Surfing", "Cooking"],
)

# 3. Serialize to RDF
rdf_graph = alice.model_dump_rdf(context=context, parent=None, predicates=set())
print(rdf_graph.serialize(format="turtle"))

# 4. Or generate SHACL constraints
shacl_context = ShaclMaterializationContext("http://example.org/shacl/")
shacl_graph = Person.model_dump_shacl(shacl_context)
print(shacl_graph.serialize(format="turtle"))
```
