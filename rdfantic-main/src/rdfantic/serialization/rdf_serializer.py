"""RDF serialization utilities for RDFantic models."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, get_origin

from rdflib import RDF, BNode, Graph, IdentifiedNode, Literal, Node, URIRef

from rdfantic import RdfanticFieldInfoMetaModel
from rdfantic.exceptions import RdfanticSerializationError
from rdfantic.internal.type_analyzer import TypeAnalyzer
from rdfantic.models.field_info import get_rdfantic_metadata

if TYPE_CHECKING:
    from rdfantic.context.base import MaterializationContext
    from rdfantic.models.base import RdfanticBaseModel


class RdfSerializer:
    """Handles RDF graph serialization for RDFantic models.

    This class provides utilities for adding triples to RDF graphs and
    serializing different field types (literals, nested models, lists, etc.).
    """

    @staticmethod
    def model_dump_rdf(
        model: RdfanticBaseModel,
        context: MaterializationContext,
        parent: RdfanticBaseModel | None = None,
        predicates: set | None = None,
        inverse: bool = False,
    ) -> Graph:
        """Serialize a model instance to an RDF graph.

        This is the main entry point for RDF serialization. It orchestrates
        the entire serialization process including parent setup, class assertions,
        and field serialization.

        Parameters
        ----------
        model : RdfanticBaseModel
            The model instance to serialize.
        context : MaterializationContext
            The materialization context used for URI resolution and creation.
        parent : RdfanticBaseModel | None, optional
            The parent model instance for nested serialization.
        predicates : set | None, optional
            Set of predicates linking parent to this instance.
        inverse : bool, optional
            Whether to create inverse (incoming) relationships. When True, triples are
            created with this instance as subject and parent as object, reversing the
            direction. Default is False.

        Returns
        -------
        Graph
            An RDFLib Graph representing this model instance.

        Raises
        ------
        ValueError
            If predicates are provided without a parent instance.
        RdfanticSerializationError
            If inverse is True but the value is not a URIRef or RdfanticBaseModel
            (literals cannot appear in subject position).
        """
        from rdfantic.models.base import RdfanticBaseModel  # noqa: PLC0415

        # Set context and parent on model instance
        model.rdfantic.ctx = context
        model.rdfantic.parent = parent

        # Set up parent relationships and initialize graph
        graph = RdfSerializer._setup_parent_and_graph(model, parent, predicates, inverse)

        # Add class type assertions
        for class_uri in model.Meta.class_uris:
            graph.add((model.rdf_term, RDF.type, class_uri))

        for field_name, field in type(model).model_fields.items():
            # Only process fields with RDF metadata annotation
            field_metadata_list = get_rdfantic_metadata(field)
            field_value = getattr(model, field_name, None)
            if field_value is not None and field_metadata_list:
                type_info = TypeAnalyzer.resolve_type_info(field.annotation)

                # Process each annotation separately
                for field_metadata in field_metadata_list:
                    value = RdfSerializer._get_field_value(model, field_name, field_metadata)

                    if value is None:
                        continue

                    # Handle list fields
                    if type_info.is_list and isinstance(value, list):
                        RdfSerializer._serialize_list_field(graph, model, field_metadata, value, type_info)
                    # Handle single BaseRdfModel
                    elif isinstance(type_info.item_type, type) and issubclass(type(value), RdfanticBaseModel):
                        RdfSerializer._serialize_nested_model(graph, model, value, field_metadata)
                    # Handle simple values (literals, strings, etc.)
                    else:
                        RdfSerializer._serialize_simple_value(graph, model, value, field_metadata, type_info)

        return graph

    @staticmethod
    def _get_field_value(
        model: RdfanticBaseModel, field_name: str, field_metadata: RdfanticFieldInfoMetaModel
    ) -> Any | Node:
        """Extract field value for RDF serialization using specific metadata.

        Resolves field values through the materialization context and applies
        custom term builders if configured in the provided metadata.

        Parameters
        ----------
        model : RdfanticBaseModel
            The model instance to extract the field value from.
        field_name : str
            The name of the field to extract.
        field_metadata : RdfanticFieldInfoMetaModel
            The specific RDF metadata to use for resolution.

        Returns
        -------
        Any | Node
            The resolved field value (may be a URIRef, Literal, or other RDF node).
        """
        value = getattr(model, field_name, None)

        if field_metadata and not field_metadata.datatype:
            # Only try to resolve terms that do not have a datatype
            resolved_value = model.rdfantic.ctx.resolve(value)

            # Could not resolve so far
            if resolved_value == value and field_metadata.str_term_builder and isinstance(value, str):
                builder = field_metadata.str_term_builder
                value = builder(model, value)
            else:
                value = resolved_value

        return value

    @staticmethod
    def _setup_parent_and_graph(
        model: RdfanticBaseModel,
        parent: RdfanticBaseModel | None,
        predicates: set | None,
        inverse: bool,
    ) -> Graph:
        """Set up parent relationships and initialize the RDF graph.

        This method handles:
        - Setting up the path from parent to child
        - Creating triples connecting parent to child via predicates
        - Validating that predicates are only provided with a parent

        Parameters
        ----------
        model : RdfanticBaseModel
            The model instance being serialized.
        parent : RdfanticBaseModel | None
            The parent model instance for nested serialization.
        predicates : set | None
            Set of predicates linking parent to this instance.
        inverse : bool
            Whether to create inverse (incoming) relationships.

        Returns
        -------
        Graph
            An initialized RDF graph with parent-child connection triples.

        Raises
        ------
        ValueError
            If predicates are provided without a parent instance.
        """
        from rdfantic.internal.path_element import PathElement  # noqa: PLC0415

        parent_uri = parent.rdf_term if parent else None
        graph = Graph()

        if parent:
            # Set up the path for nested models
            if parent_name := parent.instance_name:
                model.rdfantic.path = parent.rdfantic.path.copy()
                model.rdfantic.path.append(PathElement(parent.Meta.name, parent_name))
            else:
                model.rdfantic.path = parent.rdfantic.path.copy()

            # Add triples connecting parent to child
            if predicates:
                for predicate in predicates:
                    if inverse:
                        graph.add((model.rdf_term, predicate, parent_uri))
                    else:
                        graph.add((parent_uri, predicate, model.rdf_term))
        elif predicates:
            raise ValueError(
                "No parent was specified but predicates were specified. "
                "Either provide a parent as well or no predicates."
            )

        return graph

    @staticmethod
    def _add_to_graph(
        graph: Graph, subject: Node, predicate: URIRef, value: Any, datatype: str | None, inverse: bool
    ) -> None:
        """Add a triple to the RDF graph with appropriate literal handling.

        Parameters
        ----------
        graph : Graph
            The RDFLib graph to add the triple to.
        subject : URIRef | BNode
            The subject of the triple (when inverse=False) or the object (when inverse=True).
        predicate : URIRef
            The predicate of the triple.
        value : Any
            The object value when inverse=False, or subject value when inverse=True.
            Can be a URIRef, BNode, or literal value.
        datatype : str | None
            Optional XSD datatype URI for literal values.
        inverse : bool
            Whether to create an inverse triple. When True, the value becomes the subject
            and the subject parameter becomes the object, reversing the triple direction.

        Returns
        -------
        None

        Raises
        ------
        RdfanticSerializationError
            If inverse is True but value is not an IdentifiedNode (URIRef or BNode).
            Literals cannot appear in the subject position of RDF triples.
        """
        if inverse and not isinstance(value, IdentifiedNode):
            raise RdfanticSerializationError("Cannot create an inverse triple with Literal subject")

        if not inverse and isinstance(subject, Literal):
            raise RdfanticSerializationError("Cannot create a triple with Literal subject")

        if isinstance(value, IdentifiedNode):
            if inverse:
                graph.add((value, predicate, subject))
            else:
                graph.add((subject, predicate, value))
        else:
            if isinstance(value, str) and len(value) == 0:
                # Skip empty strings
                return None
            literal_value = Literal(value, datatype=datatype)
            graph.add((subject, predicate, literal_value))

    @staticmethod
    def _add_class_uris(graph: Graph, node: Any, class_uris: set[URIRef]) -> None:
        """Add rdf:type triples for class URIs on a node.

        Parameters
        ----------
        graph : Graph
            The RDF graph to add triples to.
        node : Any
            The node to type. Must be an IdentifiedNode (URIRef or BNode).
        class_uris : set[URIRef]
            Set of class URIs to assert as rdf:type on the node.

        Returns
        -------
        None

        Raises
        ------
        RdfanticSerializationError
            If class_uris is non-empty but node is a Literal (Literals cannot have types).
        """
        if not class_uris:
            return

        if not isinstance(node, IdentifiedNode):
            raise RdfanticSerializationError(
                f"Cannot add class_uris to a Literal node. "
                f"class_uris can only be applied to IdentifiedNode (URIRef or BNode), got {type(node).__name__}"
            )

        for class_uri in class_uris:
            graph.add((node, RDF.type, class_uri))

    @staticmethod
    def _serialize_list_field(
        graph: Graph,
        model: RdfanticBaseModel,
        field_metadata: RdfanticFieldInfoMetaModel,
        value: list,
        type_info: Any,
    ) -> None:
        """Serialize a list field to RDF.

        Dispatches to specialized handlers based on whether the list contains
        models/terms or simple literal values.

        Parameters
        ----------
        graph : Graph
            The RDF graph to add triples to.
        model : RdfanticBaseModel
            The model instance being serialized.
        field_metadata : RdfanticFieldInfoMetaModel
            The specific RDF metadata to use.
        value : list
            The list value to serialize.
        type_info : TypeInfo
            Type information for the field.

        Returns
        -------
        None
        """
        base_model, str_value = TypeAnalyzer.base_model_or_str(type_info.item_type)

        # Dispatch to appropriate handler based on list content type
        if base_model or (str_value and field_metadata.str_term_builder):
            RdfSerializer._serialize_model_or_term_list(graph, model, field_metadata, value)
        else:
            RdfSerializer._serialize_simple_list(graph, model, field_metadata, value)

    @staticmethod
    def _serialize_model_or_term_list(
        graph: Graph,
        model: RdfanticBaseModel,
        field_metadata: Any,
        value: list,
    ) -> None:
        """Serialize a list of RdfanticBaseModel instances or strings with term builders.

        This handles cases where list items are either:
        - Nested RdfanticBaseModel instances that need recursive serialization
        - Strings that should be converted to URIRefs via a term_builder

        Parameters
        ----------
        graph : Graph
            The RDF graph to add triples to.
        model : RdfanticBaseModel
            The parent model instance.
        field_metadata : RdfanticFieldInfoMetaModel
            Field metadata containing predicates and term_builder.
        value : list
            The list of models or strings to serialize.

        Returns
        -------
        None
        """
        from rdfantic.models.base import RdfanticBaseModel  # noqa: PLC0415

        for item in value:
            if isinstance(item, str) and field_metadata.str_term_builder:
                # Convert string to URI using term builder
                resolved_item = field_metadata.str_term_builder(model, item)
                for predicate in field_metadata.predicates:
                    RdfSerializer._add_to_graph(
                        graph,
                        model.rdf_term,
                        predicate,
                        resolved_item,
                        field_metadata.datatype,
                        field_metadata.inverse,
                    )
                # Add class_uris type assertions for the resolved URI
                RdfSerializer._add_class_uris(graph, resolved_item, field_metadata.class_uris)
            elif isinstance(item, str):
                raise RdfanticSerializationError("Missing term builder for mixed list type.")
            elif issubclass(type(item), RdfanticBaseModel):
                # Recursively serialize nested model
                graph += item.model_dump_rdf(
                    model.rdfantic.ctx, model, field_metadata.predicates, field_metadata.inverse
                )

    @staticmethod
    def _serialize_simple_list(
        graph: Graph,
        model: RdfanticBaseModel,
        field_metadata: Any,
        value: list,
    ) -> None:
        """Serialize a list of simple literal values.

        Handles lists of primitive types (strings, numbers, booleans) that should
        be serialized as RDF literals. Can create either individual triples for
        each item or an RDF List structure (rdf:first/rdf:rest) depending on
        field_metadata.rdf_list.

        Parameters
        ----------
        graph : Graph
            The RDF graph to add triples to.
        model : RdfanticBaseModel
            The model instance being serialized.
        field_metadata : RdfanticFieldInfoMetaModel
            Field metadata containing predicates, datatype, and rdf_list flag.
        value : list
            The list of simple values to serialize.

        Returns
        -------
        None
        """
        if field_metadata.rdf_list and value:
            # Create RDF List structure (rdf:first/rdf:rest chain)
            RdfSerializer._serialize_rdf_list(graph, model, field_metadata, value)
        else:
            # Create individual triples for each list item
            for item in value:
                resolved_item = model.rdfantic.ctx.resolve(item)
                for predicate in field_metadata.predicates:
                    RdfSerializer._add_to_graph(
                        graph,
                        model.rdf_term,
                        predicate,
                        resolved_item,
                        field_metadata.datatype,
                        field_metadata.inverse,
                    )
                # Add class_uris type assertions (only effective for IdentifiedNodes)
                RdfSerializer._add_class_uris(graph, resolved_item, field_metadata.class_uris)

    @staticmethod
    def _serialize_rdf_list(graph: Graph, model: RdfanticBaseModel, field_metadata: Any, value: list) -> None:
        """Serialize a value as an RDF list (rdf:List).

        Parameters
        ----------
        graph : Graph
            The RDF graph to add triples to.
        model : RdfanticBaseModel
            The model instance being serialized.
        field_metadata : RdfanticFieldInfoMetaModel
            Field metadata containing predicates and datatype.
        value : list
            The list to serialize.

        Returns
        -------
        None
        """
        current = BNode()
        for predicate in field_metadata.predicates:
            graph.add((model.rdf_term, predicate, current))

        for i, item in enumerate(value):
            resolved_item = model.rdfantic.ctx.resolve(item)
            next_node = BNode()
            RdfSerializer._add_to_graph(
                graph,
                current,
                RDF.first,
                resolved_item,
                field_metadata.datatype,
                False,
            )
            # Add class_uris type assertions (only effective for IdentifiedNodes)
            RdfSerializer._add_class_uris(graph, resolved_item, field_metadata.class_uris)

            if i < len(value) - 1:
                graph.add((current, RDF.rest, next_node))
                current = next_node

        graph.add((current, RDF.rest, RDF.nil))

    @staticmethod
    def _serialize_nested_model(
        graph: Graph,
        model: RdfanticBaseModel,
        value: RdfanticBaseModel,
        field_metadata: Any,
    ) -> None:
        """Serialize a nested RDFantic model.

        Parameters
        ----------
        graph : Graph
            The RDF graph to add triples to.
        model : RdfanticBaseModel
            The parent model instance.
        value : RdfanticBaseModel
            The nested model to serialize.
        field_metadata : RdfanticFieldInfoMetaModel
            Field metadata containing predicates.

        Returns
        -------
        None
        """
        graph += value.model_dump_rdf(
            context=model.rdfantic.ctx,
            parent=model,
            predicates=field_metadata.predicates,
            inverse=field_metadata.inverse,
        )

    @staticmethod
    def _serialize_simple_value(
        graph: Graph,
        model: RdfanticBaseModel,
        value: Any,
        field_metadata: Any,
        type_info: Any,
    ) -> None:
        """Serialize a simple (non-list, non-model) field value.

        Parameters
        ----------
        graph : Graph
            The RDF graph to add triples to.
        model : RdfanticBaseModel
            The model instance being serialized.
        value : Any
            The value to serialize.
        field_metadata : RdfanticFieldInfoMetaModel
            Field metadata containing predicates and datatype.
        type_info : TypeInfo
            Type information for the field.

        Returns
        -------
        None
        """
        # Special handling for dict fields: serialize as JSON string
        origin = get_origin(type_info.item_type)
        if origin is dict and isinstance(value, dict):
            for predicate in field_metadata.predicates:
                if field_metadata.inverse:
                    raise RdfanticSerializationError("Cannot add Literal values in subject position")
                elif field_metadata.class_uris:
                    raise RdfanticSerializationError("Cannot add a class to a Literal value")
                graph.add((model.rdf_term, predicate, Literal(json.dumps(value))))
        else:
            for predicate in field_metadata.predicates:
                RdfSerializer._add_to_graph(
                    graph, model.rdf_term, predicate, value, field_metadata.datatype, field_metadata.inverse
                )
            # Add class_uris type assertions (only effective for IdentifiedNodes)
            RdfSerializer._add_class_uris(graph, value, field_metadata.class_uris)
