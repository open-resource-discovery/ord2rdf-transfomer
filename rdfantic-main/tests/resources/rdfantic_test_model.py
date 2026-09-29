from __future__ import annotations

from typing import Annotated

from pydantic import Field
from rdflib import RDFS, XSD, BNode, Literal, URIRef

from rdfantic import (
    RdfanticBaseModel,
    RdfanticConstantValueModel,
    RdfanticFieldInfoMetaModel,
    RdfanticLiteralEnum,
    RdfanticModelMetadata,
    RdfanticResolvableEnum,
    field,
)


class Job(RdfanticLiteralEnum):
    SE = "Software Engineer"
    DE = "Data Engineer"
    KE = "Knowledge Engineer"


class CustomBool(RdfanticLiteralEnum):
    YES = "true"
    NO = "false"

    @property
    def datatype(self) -> str | None:
        return str(XSD.boolean)


class Gender(RdfanticResolvableEnum):
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


class Birthdate(RdfanticConstantValueModel):
    class Meta(RdfanticModelMetadata):
        name = "Birthdate"

    day: int = Field(description="Birthdate's day", ge=1, le=31)
    month: int = Field(description="Birthdate's month", ge=1, le=12)
    year: int = Field(description="Birthdate's year", ge=1, le=9999)

    @property
    def rdf_term(self) -> URIRef | Literal:
        return Literal(f"{self.year}-{self.month:02d}-{self.day:02d}")


class Address(RdfanticBaseModel):
    class Meta(RdfanticModelMetadata):
        name = "Address"
        class_uris = {URIRef("http://example.org/Address")}
        term_builder = lambda self: self.rdfantic.ctx.create_uri(
            self.rdfantic.path, str(hash(self.street)), self.Meta.name
        )  # noqa: E731
        shape_name = "Addr"

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


class Person(RdfanticBaseModel):
    class Meta(RdfanticModelMetadata):
        name = "Person"
        class_uris = {URIRef("http://example.org/Person")}
        term_builder = lambda self: URIRef(f"http://example.org/Person/{self.name}")  # noqa: E731
        instance_name = lambda self: f"{self.name}Test"  # noqa: E731

    # Old way of annotation works as well. But is not recommended.
    name: str = field(
        description="Person's name", metadata={"predicates": {URIRef("http://example.org/Person/name"), RDFS.label}}
    )

    gender: Annotated[
        Gender,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/gender")}),
        Field(default=Gender.UNKNOWN, description="Person's gender"),
    ]

    age: Annotated[
        float | int,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/age")}, datatype=XSD.integer),
        Field(description="Person's age", ge=0, le=130),
    ]

    dob: Annotated[
        Birthdate,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/birthdate")}),
        Field(description="Birthdate's date"),
    ]

    knows: Annotated[
        list[Person | str],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://example.org/Person/knows")},
            str_term_builder=lambda _model, person_name: URIRef(f"http://example.org/Person/{person_name}"),
        ),
        Field(description="Person's knows"),
    ]

    father: Annotated[
        str,
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://example.org/Person/isFatherOf")},
            str_term_builder=lambda _model, father_name: URIRef(f"http://example.org/Person/{father_name}"),
            inverse=True,
        ),
        Field(description="Person's father names"),
    ]

    jobs: Annotated[
        list[Job],
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/job")}),
        Field(description="Person's job", min_length=1, max_length=100),
    ]

    baptized: Annotated[
        bool | None,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/baptized")}),
        Field(default=None, description="Person's baptized"),
    ]

    right_handed: Annotated[
        CustomBool | None,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/right_handed")}),
        Field(default=None, description="Person's right handed"),
    ]

    nickname: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/nickname")}),
        Field(default_factory=list, description="Person's nicknames"),
    ]

    address: Annotated[
        Address | None,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/address")}),
        Field(default=None, description="Person's address"),
    ]

    hobby: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/hobby")}, rdf_list=True),
        Field(default_factory=list, description="Person's hobby"),
    ]

    children: Annotated[
        list[str] | list[Person],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://example.org/Person/child")},
            str_term_builder=lambda _model, child: URIRef(f"http://example.org/Person/{child}"),
        ),
        Field(default_factory=list, description="Person's children"),
    ]


class Company(RdfanticBaseModel):
    class Meta(RdfanticModelMetadata):
        name = "Company"
        class_uris = {}
        term_builder = lambda self: BNode(self.rdfantic.id)

    name: Annotated[
        str, RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Company/name")}, inverse=True)
    ]
