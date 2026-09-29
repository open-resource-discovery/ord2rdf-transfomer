# Tips and Best Practices

## Forward References

Always start your file with `from __future__ import annotations` when models reference each other:

```python
from __future__ import annotations

class Person(RdfanticBaseModel):
    knows: Annotated[
        list[Person | str],
        RdfanticFieldInfoMetaModel(...),
    ]
```

## Lambda Assignments in Meta

Use `# noqa: E731` on `term_builder = lambda ...`: ruff flags lambda assignments, but lambdas in `Meta` are concise and idiomatic here:

```python
class Meta(RdfanticModelMetadata):
    term_builder = lambda self: URIRef(f"http://example.org/Person/{self.name}")  # noqa: E731
```

## Framework State Access

Use `self.rdfantic.*` in term_builder lambdas to access framework state (id, ctx, path, parent):

```python
term_builder = lambda self: BNode(self.rdfantic.id)  # noqa: E731
```

## Non-RDF Fields

Fields without RDF metadata are ignored — this lets you mix RDF and non-RDF fields freely on the same model:

```python
class Person(RdfanticBaseModel):
    name: Annotated[str, RdfanticFieldInfoMetaModel(...)]  # Serialized to RDF
    cached_value: str | None = None  # Regular Pydantic field, not in RDF
```

## Multiple Annotations Per Field

Attach multiple `RdfanticFieldInfoMetaModel` instances to create diverse RDF mappings from the same Python field:

```python
partner: Annotated[
    str,
    RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/hasPartner")}),
    RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/partnerOf")}, inverse=True),
]
```

## Import from Main Package

All public symbols are exported from the main `rdfantic` package:

```python
from rdfantic import (
    RdfanticBaseModel,
    RdfanticFieldInfoMetaModel,
    RdfanticModelMetadata,
    ShaclMaterializationContext,
)
```

Avoid importing from internal modules like `rdfantic.internal.*` or `rdfantic.serialization.*` — use the public API surface.
