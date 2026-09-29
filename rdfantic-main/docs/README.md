# RDFantic Documentation

Welcome to the RDFantic documentation. This directory contains comprehensive guides for using RDFantic.

## Getting Started

- **[Quick Start](quickstart.md)** — Get up and running with RDFantic in minutes

## Core Documentation

- **[Core Concepts](core-concepts.md)** — Understand RDFantic's architecture and main components
- **[Model Definition](model-definition.md)** — Learn how to define RDF-serializable models
- **[Field Annotations](field-annotations.md)** — Master field-level RDF metadata annotations
- **[Enums](enums.md)** — Work with literal and URI-based enums
- **[Serialization](serialization.md)** — Serialize models to RDF and SHACL

## Reference

- **[API Reference](api-reference.md)** — Complete API documentation
- **[Examples](examples.md)** — Complete working examples exercising all features
- **[Tips & Best Practices](tips.md)** — Pro tips for using RDFantic effectively

## Table of Contents

### Quick Start
- Installation
- Basic usage example
- Next steps

### Core Concepts
- RdfanticBaseModel
- RdfanticModelMetadata
- RdfanticFieldInfoMetaModel
- MaterializationContext
- Model instance properties

### Model Definition
- Basic models
- Nested models
- Self-referential models
- Constant value models

### Field Annotations
- Basic field with predicate
- Multiple predicates
- Multiple annotations
- Datatype specification
- Term builders
- Field class URIs
- RDF lists
- Inverse properties
- Optional fields and defaults

### Enums
- RdfanticLiteralEnum (literals)
- RdfanticResolvableEnum (URIs)
- Custom datatypes

### Serialization
- Serializing to RDF
- Generating SHACL shapes
- Customizing SHACL shape names

### Examples
- Complete example with all features
- Usage patterns

### API Reference
- Core classes
- Project structure
- Module overview

### Tips
- Forward references
- Lambda assignments
- Framework state access
- Non-RDF fields
- Multiple annotations
- Import patterns
