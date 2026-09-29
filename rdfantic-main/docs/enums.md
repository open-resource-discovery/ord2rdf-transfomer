# Enums

RDFantic provides two enum bases for different serialization needs.

## RdfanticLiteralEnum — Emits Literals

For enum values that should be serialized as RDF literals:

```python
from rdfantic import RdfanticLiteralEnum

class Job(RdfanticLiteralEnum):
    SE = "Software Engineer"
    DE = "Data Engineer"
    KE = "Knowledge Engineer"
```

By default, `Job.SE` serializes to `"Software Engineer"` (xsd:string).

### Custom Datatype

Override `datatype` to control the XSD type:

```python
class CustomBool(RdfanticLiteralEnum):
    YES = "true"
    NO = "false"

    @property
    def datatype(self) -> str | None:
        return str(XSD.boolean)
```

### Using in Fields

```python
jobs: Annotated[
    list[Job],
    RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/job")}),
    Field(description="Person's jobs", min_length=1, max_length=100),
]
```

## RdfanticResolvableEnum — Emits URIs

For controlled vocabularies where each enum member maps to a specific URI:

```python
from rdfantic import RdfanticResolvableEnum

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
```

`Gender.MALE` will be serialized as `<http://example.org/Gender/Male>`.

### Using in Fields

```python
gender: Annotated[
    Gender,
    RdfanticFieldInfoMetaModel(predicates={URIRef("http://example.org/Person/gender")}),
    Field(default=Gender.UNKNOWN, description="Person's gender"),
]
```
