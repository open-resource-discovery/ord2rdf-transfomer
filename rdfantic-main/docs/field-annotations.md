# Field Annotations

RDF metadata is attached to fields with `typing.Annotated`:

```python
field_name: Annotated[
    <PythonType>,                    # The actual type
    RdfanticFieldInfoMetaModel(      # RDF metadata
        predicates={URIRef(...)},
        ...
    ),
    Field(...),                      # Optional Pydantic field config
]
```

You can also attach **multiple** `RdfanticFieldInfoMetaModel` annotations to the same field — each annotation is processed independently during serialization and SHACL generation.

## Basic Field with Predicate

The minimum: bind a field to one RDF predicate.

```python
street: Annotated[
    str,
    RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Address/street")}),
    Field(description="Address' street"),
]
```

## Multiple Predicates

Bind a single field to **multiple** predicates within a single annotation — the value is emitted once per predicate.

```python
name: Annotated[
    str,
    RdfanticFieldInfoMetaModel(
        predicates={
            URIRef("http://example.org/Person/name"),
            RDFS.label,
        }
    ),
    Field(description="Person's name"),
]
```

The serializer emits both `<person> ex:name "Alice"` and `<person> rdfs:label "Alice"`.

## Multiple Annotations

You can attach **multiple** `RdfanticFieldInfoMetaModel` annotations to the same field. Each annotation is processed independently during serialization and SHACL generation, allowing you to:

- Use different predicates with different settings (datatypes, term builders, inverse flags)
- Emit the same value as both a literal and a URI
- Create both outgoing and incoming relationships from the same field

```python
# Same field with different predicates and different datatypes
value: Annotated[
    str,
    RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/value")}),
    RdfanticFieldInfoMetaModel(
        predicates={URIRef("http://example.org/typedValue")},
        datatype=XSD.string,
    ),
]

# Same field emitted as literal AND as URI
related: Annotated[
    str,
    RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/relatedLiteral")}),
    RdfanticFieldInfoMetaModel(
        predicates={URIRef("http://example.org/relatedUri")},
        str_term_builder=lambda _model, val: URIRef(f"http://example.org/Related/{val}"),
    ),
]

# Same field with normal and inverse relationships
partner: Annotated[
    str,
    RdfanticFieldInfoMetaModel(
        predicates={URIRef("http://example.org/hasPartner")},
        str_term_builder=lambda _model, val: URIRef(f"http://example.org/Partner/{val}"),
    ),
    RdfanticFieldInfoMetaModel(
        predicates={URIRef("http://example.org/partnerOf")},
        inverse=True,
        str_term_builder=lambda _model, val: URIRef(f"http://example.org/Partner/{val}"),
    ),
]
```

For the `partner` example above with value `"bob"`, RDFantic generates:
```turtle
:alice ex:hasPartner :bob .   # Normal direction
:bob ex:partnerOf :alice .    # Inverse direction
```

## Datatype Specification

Use `datatype` to force an XSD datatype on the literal. Without it, RDFantic infers from the Python type when possible.

```python
from rdflib import XSD

age: Annotated[
    float | int,
    RdfanticFieldInfoMetaModel(
        predicates={URIRef("http://example.org/Person/age")},
        datatype=XSD.integer,
    ),
    Field(description="Person's age", ge=0, le=130),
]
```

## Term Builders

`str_term_builder` converts string values into URIs at serialization time. The builder receives **two** arguments: the owning `RdfanticBaseModel` instance and the field's string value.

```python
knows: Annotated[
    list["Person | str"],
    RdfanticFieldInfoMetaModel(
        predicates={URIRef("http://example.org/Person/knows")},
        str_term_builder=lambda model, person_name: URIRef(f"http://example.org/Person/{person_name}"),
    ),
    Field(description="People this person knows"),
]
```

For `list[T]` fields, the builder is called once for each string item in the list.

### Using the Model to Derive URIs

Because the first argument is the owning model, `str_term_builder` can pull namespaces or other context off sibling fields:

```python
class Document(RdfanticBaseModel):
    namespace: str  # e.g. "acme"

    # The URI for each link is built as http://example.org/<namespace>/<link>
    links: Annotated[
        list[str],
        RdfanticFieldInfoMetaModel(
            predicates={URIRef("http://example.org/Document/link")},
            str_term_builder=lambda model, link: URIRef(f"http://example.org/{model.namespace}/{link}"),
        ),
        Field(description="Related documents in the same namespace"),
    ]
```

## Field Class URIs

Use `class_uris` to add `rdf:type` assertions on the field's value node.

```python
author: Annotated[
    str,
    RdfanticFieldInfoMetaModel(
        predicates={URIRef("http://example.org/author")},
        str_term_builder=lambda model, name: URIRef(f"http://example.org/Person/{name}"),
        class_uris={URIRef("http://example.org/Person")},
    ),
    Field(description="The author, typed as Person"),
]
```

This generates:
```turtle
:book ex:author :alice .
:alice a ex:Person .
```

**Important**: `class_uris` can only be used when the field value serializes to an `IdentifiedNode` (URIRef or BNode). You need to use a `str_term_builder` to convert string values to URIs.

## RDF Lists

Set `rdf_list=True` to emit the values as a properly linked `rdf:List` (with `rdf:first` / `rdf:rest` chaining).

```python
hobby: Annotated[
    list[str],
    RdfanticFieldInfoMetaModel(
        predicates={URIRef("http://example.org/Person/hobby")},
        rdf_list=True,
    ),
    Field(default_factory=list, description="Person's hobbies"),
]
```

Without `rdf_list=True`:
```turtle
:alice ex:hobby "Surfing", "Cooking" .
```

With `rdf_list=True`:
```turtle
:alice ex:hobby ( "Surfing" "Cooking" ) .
```

## Inverse Properties

Set `inverse=True` to create inverse (incoming) relationships where the annotated field represents objects that point to this model instance.

```python
known_by: Annotated[
    list[Person | str],
    RdfanticFieldInfoMetaModel(
        predicates={URIRef("http://example.org/Person/knows")},
        inverse=True,
        str_term_builder=lambda _model, person_name: URIRef(f"http://example.org/Person/{person_name}"),
    ),
    Field(description="People who know this person"),
]
```

Without `inverse=True`:
```turtle
:alice ex:knows :bob .  # Alice knows Bob
```

With `inverse=True`:
```turtle
:bob ex:knows :alice .  # Bob knows Alice (inverse representation)
```

**Important**: Inverse properties can only be used with URI references (URIRef) or nested RdfanticBaseModel instances.

## Optional Fields and Defaults

Optional fields use standard Python `| None` and Pydantic's `Field(default=...)`:

```python
baptized: Annotated[
    bool | None,
    RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/baptized")}),
    Field(default=None, description="Whether the person is baptized"),
]

nickname: Annotated[
    list[str],
    RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/nickname")}),
    Field(default_factory=list, description="Nicknames"),
]
```

Fields whose value is `None` at serialization time are simply skipped.
