"""Model metadata configuration for RDFantic models."""

from collections.abc import Callable
from typing import ClassVar

from pydantic import BaseModel, ConfigDict
from rdflib import IdentifiedNode, URIRef


class RdfanticModelMetadata(BaseModel):
    """Base metadata class for RDFantic models.

    This class defines the RDF serialization behavior for a model. Subclass this
    as an inner `Meta` class within your RdfanticBaseModel to configure how the
    model is serialized to RDF and SHACL.

    Attributes
    ----------
    name : str
        Human-readable name for the model. Used for path building and debugging.
        Required for all models.

    namespace : str | None
        Optional namespace URI prefix for generated terms. Currently unused but
        reserved for future namespace management features.

    class_uris : set[URIRef]
        Set of RDF class URIs (rdf:type) to assert for instances of this model.
        When serialized, each instance will have triples like:
        `<instance_uri> rdf:type <class_uri>` for each class URI in this set.
        Use an empty set for models that don't need class assertions.

    term_builder : Callable[[BaseModel], URIRef | Literal] | None
        Function that generates the RDF term (URI, BNode, or Literal) for a model
        instance. Receives the model instance as argument and should return the
        term that identifies this instance in the RDF graph.

        Access framework state via `self.rdfantic`:
        - `self.rdfantic.id` - unique UUID for this instance
        - `self.rdfantic.ctx` - materialization context with URI creation methods
        - `self.rdfantic.path` - path from root for hierarchical URI building
        - `self.rdfantic.parent` - parent model instance

    Examples
    --------
            # Simple URI from a field value
            term_builder = lambda self: URIRef(f"http://example.org/Person/{self.name}")

            # BNode using the instance UUID
            term_builder = lambda self: BNode(self.rdfantic.id)

            # URI using the materialization context
            term_builder = lambda self: self.rdfantic.ctx.create_uri(
                self.rdfantic.path, self.identifier, self.Meta.name
            )

    instance_name : Callable[[BaseModel], str] | None
        Function that returns a string identifier for path building in nested models.
        When a model contains nested RdfanticBaseModel instances, this name is used
        to construct the path hierarchy. The path is then available to child models
        via `self.rdfantic.path` for building hierarchical URIs.

        Example:
            instance_name = lambda self: f"{self.name}_{self.version}"

    shape_name : str | None
        Override for the SHACL shape name. If not set, defaults to `{name}Shape`.
        Use this when you want a different shape name than the model name would
        generate (e.g., abbreviated names like "Addr" instead of "Address").

    Example
    -------
    ```python
    class Person(RdfanticBaseModel):
        class Meta(RdfanticModelMetadata):
            name = "Person"
            class_uris = {URIRef("http://schema.org/Person")}
            term_builder = lambda self: URIRef(f"http://example.org/person/{self.id}")
            instance_name = lambda self: self.name
            shape_name = "PersonShape"

        name: str
        age: int
    ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    name: ClassVar[str]
    namespace: ClassVar[str | None] = None
    class_uris: ClassVar[frozenset[URIRef]] = frozenset()  # Use frozenset to prevent shared mutable state
    term_builder: ClassVar[Callable[[BaseModel], IdentifiedNode] | None] = None
    instance_name: ClassVar[Callable[[BaseModel], str] | None] = None
    shape_name: ClassVar[str | None] = None

    @classmethod
    def get_shape_name(cls) -> str:
        """Get the SHACL shape name for this model.

        Returns the configured shape_name if set, otherwise defaults to the
        model name, with "Shape" suffix appended.

        Returns
        -------
        str
            The shape name with "Shape" suffix (e.g., "PersonShape" or "AddrShape").
        """
        name = cls.shape_name if cls.shape_name is not None else cls.name
        return f"{name}Shape"
