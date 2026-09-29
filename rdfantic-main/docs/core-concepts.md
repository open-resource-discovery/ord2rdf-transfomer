# Core Concepts

RDFantic is built on three core building blocks:

| Concept | Purpose |
|---------|---------|
| **`RdfanticBaseModel`** | Base class for any model that should be RDF-serializable. Extends Pydantic's `BaseModel`. |
| **`RdfanticModelMetadata`** | Inner `Meta` class that declares the RDF class URIs and how to build the subject URI for instances. |
| **`RdfanticFieldInfoMetaModel`** | Field-level metadata (predicates, datatype, term builder, list flag) attached via `Annotated`. Multiple annotations per field supported. |
| **`MaterializationContext`** | Resolves string values to URIs and builds resource URIs (must be set before serialization). |

## Model Instance Properties

Each `RdfanticBaseModel` instance provides:

- **`rdfantic`** — Returns the `RdfanticState` container with framework-specific state:
  - `rdfantic.id` — Unique UUID for this instance
  - `rdfantic.ctx` — Materialization context (set during serialization)
  - `rdfantic.parent` — Parent model in the serialization hierarchy
  - `rdfantic.path` — Path from root for hierarchical URI building
- **`instance_name`** — Returns a string identifier for the instance based on `Meta.instance_name` callable (if defined). Used for path building in nested models. Returns `None` if not configured.
- **`rdf_term`** — Returns the RDF term (URI or BNode) for this instance, computed via `Meta.term_builder`. This property is cached for performance.

The **`Annotated` pattern** is the recommended (and only encouraged) way to attach RDF metadata to fields. Pydantic v2 reads the metadata from the annotation transparently — there's no custom `field()` function to learn.

## Materialization Context

When serializing, you must provide a `MaterializationContext`. The context is responsible for:

- **`resolve_term(term)`** — convert string values into URIs (or leave them as plain strings).
- **`create_uri(path, identifier, element_type)`** — build resource URIs for nested elements.

A minimal implementation:

```python
from rdfantic import MaterializationContext, PathElement
from rdflib import URIRef


class SimpleContext(MaterializationContext):
    def resolve_term(self, term: str) -> URIRef | str:
        # Pass strings through unchanged
        return term

    def create_uri(self, path: list[PathElement], identifier: str, element_type: str | None = None) -> URIRef:
        return URIRef(f"http://example.org/{identifier}")
```

The context is passed explicitly to `model_dump_rdf()` and automatically propagates to nested models during serialization.

RDFantic provides a built-in `ShaclMaterializationContext` for SHACL-compliant URI generation:

```python
from rdfantic import ShaclMaterializationContext

context = ShaclMaterializationContext("http://example.org/", strict=False)
```
