# API Reference

## Core Classes

| Symbol | Purpose |
|--------|---------|
| `RdfanticBaseModel` | Base class for RDF-serializable Pydantic models. |
| `RdfanticConstantValueModel` | Subclass for models that emit a single literal (e.g. `Birthdate`). |
| `RdfanticModelMetadata` | Inner `Meta` class declaring `name`, `class_uris`, `term_builder`. |
| `RdfanticFieldInfoMetaModel` | Field-level metadata (`predicates`, `datatype`, `str_term_builder`, `rdf_list`, `inverse`, `class_uris`). Multiple annotations per field supported. |
| `RdfanticLiteralEnum` | Enum base — members serialize as RDF literals. |
| `RdfanticResolvableEnum` | Enum base — each member resolves to a `URIRef` via `rdf_term`. |
| `RdfanticSerializationError` | Exception raised when RDF serialization encounters an invalid state (e.g., inverse with literals). |
| `MaterializationContext` | Abstract class for term resolution and URI generation. |
| `ShaclMaterializationContext` | SHACL-compliant materialization context. |
| `PathElement` | NamedTuple for hierarchical path elements. |

## Project Structure

```
src/rdfantic/
├── __init__.py                      # Public API exports
├── exceptions.py                    # Custom exceptions (RdfanticSerializationError)
│
├── models/                          # Model classes and metadata
│   ├── __init__.py
│   ├── base.py                      # RdfanticBaseModel (main entry point)
│   ├── metadata.py                  # RdfanticModelMetadata
│   ├── constant_value.py            # RdfanticConstantValueModel
│   ├── enums.py                     # RdfanticResolvableEnum, RdfanticLiteralEnum
│   └── field_info.py                # RdfanticFieldInfoMetaModel, field helpers
│
├── serialization/                   # Serialization logic
│   ├── __init__.py
│   ├── rdf_serializer.py            # RdfSerializer (RDF graph output)
│   └── shacl_generator.py           # ShaclGenerator (SHACL shape output)
│
├── context/                         # Materialization contexts
│   ├── __init__.py
│   ├── base.py                      # MaterializationContext (ABC)
│   └── shacl.py                     # ShaclMaterializationContext
│
├── internal/                        # Internal utilities (not public API)
│   ├── __init__.py
│   ├── state.py                     # RdfanticState
│   ├── type_analyzer.py             # TypeAnalyzer, TypeInfo
│   ├── path_element.py              # PathElement
│   └── protocols.py                 # Resolvable protocol
│
└── shacl/                           # SHACL vocabulary models
    ├── __init__.py
    └── models.py                    # Shape, PropertyShape, NodeShape, etc.
```

## Module Overview

| Directory | Purpose |
|-----------|---------|
| `models/` | Model base classes, metadata, enums, and field info |
| `serialization/` | RDF graph and SHACL serialization logic |
| `context/` | Materialization contexts for URI resolution and creation |
| `internal/` | Framework internals (not meant for direct import) |
| `shacl/` | Pydantic models for SHACL vocabulary concepts |
