# Serialization

## Serializing to RDF

Call `model_dump_rdf` with a context to get an `rdflib.Graph`:

```python
alice = Person(name="Alice", age=30, ...)
context = ShaclMaterializationContext("http://example.org/")
graph = alice.model_dump_rdf(context=context, parent=None, predicates=set())
print(graph.serialize(format="turtle"))
```

### Parameters

- **`context`** — the `MaterializationContext` instance used for URI resolution and creation. Required.
- **`parent`** — the parent model instance (or `None` for the root). Used internally for nested serialization.
- **`predicates`** — a set of predicates linking the parent to this instance. Use `set()` for the root. Note: If predicates are provided, a parent must also be provided.

## Generating SHACL Shapes

RDFantic can generate a SHACL graph describing the constraints encoded in your annotations:

```python
from rdfantic import ShaclMaterializationContext

context = ShaclMaterializationContext("http://example.org/shacl/")
shacl_graph = Person.model_dump_shacl(context)
print(shacl_graph.serialize(format="turtle"))
```

### Parameters

- **`context`** — a `MaterializationContext` instance used to generate SHACL resource URIs. The context has a `strict` property to enforce stricter typing (e.g., add `sh:datatype` constraints for primitive Python types when you didn't specify a `datatype`)

### What Gets Generated

The SHACL generator inspects:

- Pydantic constraints (`ge`, `le`, `min_length`, `max_length`, etc.) → `sh:minInclusive`, `sh:maxLength`, ...
- Optionality (`| None`) → `sh:minCount 0`
- List vs scalar typing → `sh:minCount` / `sh:maxCount`
- `RdfanticFieldInfoMetaModel.datatype` → `sh:datatype`
- Nested `RdfanticBaseModel` types → `sh:class` and recursively-generated `sh:NodeShape`s.

### Customizing SHACL Shape Names

By default, the SHACL node shape name is derived from `Meta.name` + "Shape" (e.g., `Person` → `PersonShape`). You can override this by setting `Meta.shape_name`:

```python
class Address(RdfanticBaseModel):
    class Meta(RdfanticModelMetadata):
        name = "Address"
        shape_name = "Addr"  # Shape will be named "AddrShape" instead of "AddressShape"
        ...
```

The shape name is accessed via the `Meta.get_shape_name()` class method, which appends "Shape" to the configured or default name.
