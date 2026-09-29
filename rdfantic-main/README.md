# RDFantic

A Pydantic v2-based framework for declarative RDF graph serialization and SHACL shape generation.

RDFantic lets you decorate Pydantic models with RDF metadata using the standard `typing.Annotated` pattern. Once annotated, your models can be:

- 🔄 **Serialized to RDF graphs** (`model_dump_rdf`)
- 📐 **Exported as SHACL shapes** (`model_dump_shacl`) for validation
- ✅ **Validated** like any regular Pydantic model

---

## Project Status: Alpha / Active Development

> [!WARNING]
> **RDFantic is in alpha and under active development.**
>
> - **Features are added as needed** — new annotation options, serialization patterns, and SHACL constraints are introduced when concrete use cases require them, not preemptively.
> - **Bugs are resolved as they are encountered** — the API surface is small and well-tested for the supported scenarios, but edge cases outside that envelope may not yet be handled.
> - **Breaking changes may occur** between minor versions while the API stabilizes. Pin your version and read the changelog before upgrading.
> - **Feedback welcome**: if you hit a missing feature or a bug, please open an issue or pull request — the roadmap is shaped by real usage.

---

## Installation

### Development Installation

Clone the repository and install with development dependencies:

```bash
git clone https://github.com/your-org/bkg-rdfantic.git
cd bkg-rdfantic
uv sync # install dev and test dependencies by default
```

---

## Quick Start

```python
from typing import Annotated
from pydantic import Field
from rdflib import URIRef, RDFS

from rdfantic import (
    RdfanticBaseModel,
    RdfanticFieldInfoMetaModel,
    RdfanticModelMetadata,
    ShaclMaterializationContext,
)


class Person(RdfanticBaseModel):
    """A person with a name."""

    class Meta(RdfanticModelMetadata):
        name = "Person"
        class_uris = {URIRef("http://example.org/Person")}
        term_builder = lambda self: URIRef(f"http://example.org/Person/{self.name}")  # noqa: E731

    name: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={RDFS.label}),
        Field(description="Person's name"),
    ]


# Create context, instantiate, and serialize
context = ShaclMaterializationContext("http://example.org/")
alice = Person(name="Alice")
graph = alice.model_dump_rdf(context=context, parent=None, predicates=set())
print(graph.serialize(format="turtle"))
```

---

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Quick Start](docs/quickstart.md)** — Get started in minutes
- **[Core Concepts](docs/core-concepts.md)** — Understand RDFantic's architecture
- **[Model Definition](docs/model-definition.md)** — Define RDF-serializable models
- **[Field Annotations](docs/field-annotations.md)** — Annotate fields with RDF metadata
- **[Enums](docs/enums.md)** — Use enums for literals and URIs
- **[Serialization](docs/serialization.md)** — Serialize to RDF and SHACL
- **[Examples](docs/examples.md)** — Complete working examples
- **[API Reference](docs/api-reference.md)** — Complete API documentation
- **[Tips & Best Practices](docs/tips.md)** — Pro tips for using RDFantic
- **[Building & Publishing](docs/building.md)** — Build and distribute the library

---

## Building the Package

To build RDFantic as a distributable library:

```bash
uv build
```

This creates both wheel and source distributions in the `dist/` directory:
- `bkg_rdfantic-x.y.z-py3-none-any.whl` (wheel)
- `bkg_rdfantic-x.y.z.tar.gz` (source)

For complete instructions on building, testing, and publishing, see the [Building & Publishing Guide](docs/building.md).

---

## Running Tests

RDFantic uses pytest for testing. The test suite includes unit tests and integration tests for RDF serialization and SHACL generation.

### Run all tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=rdfantic --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_rdfantic.py

# Run tests in parallel
uv run pytest -n auto

# Default pytest options are defined with double verbosity
#       (see pyproject.toml)
# Add option below to reduce verbosity
uv run pytest -q
```

---

## Features

- ✅ **Pydantic v2 native** — leverages `typing.Annotated` for clean, type-safe RDF metadata
- ✅ **Multiple predicates per field** — emit the same value under different properties
- ✅ **Multiple annotations per field** — create diverse RDF mappings from the same Python field
- ✅ **Term builders** — dynamically construct URIs from field values
- ✅ **Nested models** — recursive serialization with automatic linking
- ✅ **RDF lists** — proper `rdf:List` serialization with `rdf:first`/`rdf:rest`
- ✅ **Inverse properties** — express relationships from both directions
- ✅ **Enum support** — both literal and URI-based enums
- ✅ **SHACL generation** — automatic constraint extraction from Pydantic validators
- ✅ **Field class URIs** — add `rdf:type` assertions on field values
- ✅ **Datatype control** — explicit XSD datatype specification

---

## Requirements

- Python 3.12+
- Pydantic 2.13.4+
- rdflib 7.6.0+
- pyshacl 0.40.1+

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Clone the repository
2. Install dependencies: `uv sync`
3. Install pre-commit hooks: `uv run pre-commit install`
4. Run tests: `uv run pytest`
5. Run linting: `uv run ruff check .`
6. Run formatting: `uv run ruff format .`

---

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

---

## Acknowledgments

RDFantic is developed and maintained by SAP SE as part of the Business Knowledge Graph initiative.
