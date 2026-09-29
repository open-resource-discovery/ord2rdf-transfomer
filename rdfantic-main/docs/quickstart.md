# Quick Start

This guide will get you up and running with RDFantic in minutes.

## Installation (not supported yet)

Install RDFantic using pip:

```bash
pip install bkg-rdfantic
```

Or using Poetry:

```bash
poetry add bkg-rdfantic
```

Or using uv:

```bash
uv add bkg-rdfantic
```

## Basic Usage

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

## Next Steps

- Read the [Core Concepts](core-concepts.md) to understand RDFantic's architecture
- Explore [Field Annotations](field-annotations.md) for advanced field configuration
- Learn about [Model Definition](model-definition.md) for complex models
- Check out the [Complete Example](examples.md) for a comprehensive demonstration
