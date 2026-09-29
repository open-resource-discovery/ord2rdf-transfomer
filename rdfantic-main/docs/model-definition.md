# Model Definition

Every RDF-serializable model:

1. Inherits from `RdfanticBaseModel`.
2. Defines a nested `Meta(RdfanticModelMetadata)` class with:
   - `name`: short logical name (used for path building, error messages).
   - `class_uris`: a set of `URIRef` — the RDF classes the instance is an instance of.
   - `term_builder`: a callable that returns the subject URI/BNode for an instance.
   - `instance_name` (optional): a callable that returns a string name for the instance (used for path building in nested models).
   - `shape_name` (optional): a custom name for the SHACL shape; if not provided, defaults to `name` + "Shape".

## Basic Model

```python
from rdflib import BNode, URIRef
from rdfantic import RdfanticBaseModel, RdfanticModelMetadata


class Address(RdfanticBaseModel):
    """A postal address."""

    class Meta(RdfanticModelMetadata):
        name = "Address"
        class_uris = {URIRef("http://example.org/Address")}
        # Use a blank node identified by the model's auto-generated id
        term_builder = lambda self: BNode(self.rdfantic.id)
        # Optional: custom shape name for SHACL generation (default: "AddressShape")
        shape_name = "Addr"
```

> **Note:** Fields without RDF annotation (`RdfanticFieldInfoMetaModel`) are **not** serialized to RDF. They behave as regular Pydantic fields — useful for transient state, computed properties, or non-RDF metadata.

## Nested Models

Reference another `RdfanticBaseModel` directly. RDFantic recursively serializes the nested model and links it via the predicate:

```python
class Person(RdfanticBaseModel):
    ...

    address: Annotated[
        Address | None,
        RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/address")}),
        Field(default=None, description="Person's address"),
    ]
```

## Self-Referential Models

For self-referential or forward references, use `from __future__ import annotations` at the top of the file:

```python
from __future__ import annotations

class Person(RdfanticBaseModel):
    knows: Annotated[
        list[Person | str],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://example.org/Person/knows")},
            str_term_builder=lambda _model, name: URIRef(f"http://example.org/Person/{name}"),
        ),
        Field(description="People this person knows"),
    ]
```

## Constant Value Models

For models that should emit a single literal value (like dates), inherit from `RdfanticConstantValueModel`:

```python
from rdfantic import RdfanticConstantValueModel

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
```
