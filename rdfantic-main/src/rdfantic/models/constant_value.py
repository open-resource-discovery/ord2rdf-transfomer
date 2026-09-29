"""Constant value model for representing RDF resources with fixed predicates."""

from typing import Self

from rdflib import Graph, IdentifiedNode

from rdfantic.context.base import MaterializationContext
from rdfantic.exceptions import RdfanticSerializationError
from rdfantic.models.base import RdfanticBaseModel
from rdfantic.models.metadata import RdfanticModelMetadata


class RdfanticConstantValueModel(RdfanticBaseModel):
    """Model for representing RDF resources with constant predicate relationships.

    This model is used for values that are emitted as a single literal or URI,
    rather than having their fields serialized individually. Subclasses must
    override the `rdf_term` property to define the value.
    """

    class Meta(RdfanticModelMetadata):
        """Metadata configuration for constant value models.

        Subclasses should override this with their own Meta class that sets
        the `name` field. The base class provides a default name.
        """

        name = "ConstantValue"

    def model_dump_rdf(
        self: Self,
        context: MaterializationContext,
        parent: RdfanticBaseModel | None = None,
        predicates: set | None = None,
        inverse: bool = False,
    ) -> Graph:
        """Serialize this constant value model to an RDF graph.

        Parameters
        ----------
        context : MaterializationContext
            The materialization context used for URI resolution and creation.
        parent : RdfanticBaseModel | None, optional
            The parent model instance.
        predicates : set | None, optional
            Set of predicates linking parent to this instance.
        inverse : bool, optional
            Whether to create inverse (incoming) relationships.

        Returns
        -------
        Graph
            An RDFLib Graph representing this constant value.
        """
        self.rdfantic.ctx = context
        self.rdfantic.parent = parent

        term = self.rdf_term

        if predicates is None or term is None:
            return Graph()

        graph = Graph()

        # Add links from parent:
        if parent:
            for predicate in predicates:
                if inverse:
                    if isinstance(term, IdentifiedNode):
                        graph.add((term, predicate, parent.rdf_term))
                    else:
                        raise RdfanticSerializationError("RDF Term in subject position cannot be a Literal.")
                else:
                    graph.add((parent.rdf_term, predicate, term))

        return graph
