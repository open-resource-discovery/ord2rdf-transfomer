"""SHACL shape generation utilities for RDFantic models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic.fields import FieldInfo
from rdflib import RDF, XSD, Graph, URIRef

from rdfantic.internal.type_analyzer import TypeAnalyzer, TypeInfo
from rdfantic.models.field_info import RdfanticFieldInfoMetaModel, get_rdfantic_metadata
from rdfantic.shacl import NodeShape

if TYPE_CHECKING:
    from rdfantic.context.shacl import ShaclMaterializationContext
    from rdfantic.models.base import RdfanticBaseModel
    from rdfantic.shacl.models import PropertyShape, Shape

DT_MAP = {str: XSD.string, int: XSD.integer, float: XSD.float, bool: XSD.boolean}

# Mapping from Pydantic constraint names to SHACL property names
DESCRIPTOR_MAP = {
    "min_length": "min_count",
    "max_length": "max_count",
    "gt": "min_exclusive",
    "ge": "min_inclusive",
    "lt": "max_exclusive",
    "le": "max_inclusive",
}


class ShaclGenerator:
    """Generates SHACL shapes from RDFantic models.

    This class provides utilities for exporting SHACL shape definitions
    from Pydantic models with RDF annotations.
    """

    @staticmethod
    def model_dump_shacl(model_class: type[RdfanticBaseModel], context: ShaclMaterializationContext) -> Graph:
        """Generate SHACL graph for a model.

        Parameters
        ----------
        model_class : type[RdfanticBaseModel]
            The model class to generate shapes for.
        context : ShaclMaterializationContext
            Context for SHACL generation.

        Returns
        -------
        Graph
            RDF graph containing SHACL shape definitions.
        """
        graph = Graph()
        shapes = ShaclGenerator._export_shacl(model_class, set(), context.strict)
        for shape in shapes:
            graph += shape.model_dump_rdf(context=context, parent=None, predicates=set())
        return graph

    @staticmethod
    def _export_shacl(model_class: type[RdfanticBaseModel], covered: set[type], strict: bool) -> list[Shape]:
        """Export SHACL shapes for a model and its nested models.

        Parameters
        ----------
        model_class : type[RdfanticBaseModel]
            The model class to generate shapes for.
        covered : set[type]
            Set of model types already processed to avoid circular references.
        strict : bool
            Whether to enforce strict type constraints in SHACL shapes.

        Returns
        -------
        list[Shape]
            List of SHACL shape instances.
        """
        shapes: list[Shape] = []

        if model_class.Meta.class_uris:
            target_classes = model_class.Meta.class_uris

            # Generate property shapes for all fields (also collects nested model shapes)
            property_shapes, nested_shapes = ShaclGenerator._generate_property_shapes(model_class, covered, strict)

            # Generate the node shape for the model
            shape = ShaclGenerator._generate_model_shape(model_class, target_classes, property_shapes, strict)

            # Combine: nested shapes first, then this model's shape
            shapes.extend(nested_shapes)
            shapes.append(shape)

        return shapes

    @staticmethod
    def _generate_property_shapes(
        model_class: type[RdfanticBaseModel],
        covered: set[type],
        strict: bool,
    ) -> tuple[list[PropertyShape], list[Shape]]:
        """Generate PropertyShape instances for all fields in a model.

        Parameters
        ----------
        model_class : type[RdfanticBaseModel]
            The model class to generate property shapes for.
        covered : set[type]
            Set of model types already processed to avoid circular references.
        strict : bool
            Whether to enforce strict type constraints in SHACL shapes.

        Returns
        -------
        tuple[list[PropertyShape], list[Shape]]
            A tuple of (property_shapes, nested_model_shapes).
        """
        property_shapes: list[PropertyShape] = []
        nested_shapes: list[Shape] = []

        for field_name, field in model_class.model_fields.items():
            # Only process fields with RDF metadata annotation
            field_metadata_list = get_rdfantic_metadata(field)
            for field_metadata_obj in field_metadata_list:
                # Generate property shape(s) for this field
                field_property_shapes, field_nested_shapes = ShaclGenerator._generate_field_property_shapes(
                    model_class, field_name, field, field_metadata_obj, covered, strict
                )
                property_shapes.extend(field_property_shapes)
                nested_shapes.extend(field_nested_shapes)

        return property_shapes, nested_shapes

    @staticmethod
    def _generate_field_property_shapes(
        model_class: type[RdfanticBaseModel],
        field_name: str,
        field: FieldInfo,
        field_metadata_obj: RdfanticFieldInfoMetaModel,
        covered: set[type],
        strict: bool,
    ) -> tuple[list[PropertyShape], list[Shape]]:
        """Generate PropertyShape instances for a single field.

        A field may have multiple property shapes if it has multiple predicates.

        Parameters
        ----------
        model_class : type[RdfanticBaseModel]
            The model class containing the field.
        field_name : str
            The name of the field.
        field : FieldInfo
            Field information.
        field_metadata_obj : RdfanticFieldInfoMetaModel
            RDF metadata for the field.
        covered : set[type]
            Set of model types already processed.
        strict : bool
            Whether to enforce strict type constraints.

        Returns
        -------
        tuple[list[PropertyShape], list[Shape]]
            A tuple of (property_shapes, nested_model_shapes).
        """
        from rdfantic.shacl.models import PropertyPath, PropertyShape  # noqa: PLC0415

        type_info = TypeAnalyzer.resolve_type_info(field.annotation)
        field_metadata = ShaclGenerator._collect_field_metadata(field, type_info, strict, field_metadata_obj)

        # Get class constraints from nested models
        classes, nested_shapes = ShaclGenerator._get_nested_model_classes(type_info, covered, strict)

        # Create one PropertyShape per predicate
        property_shapes: list[PropertyShape] = []
        for predicate in field_metadata_obj.predicates:
            prop_shape_name = f"{model_class.Meta.get_shape_name()}-{field_name}"

            # Handle inverse properties
            if field_metadata_obj.inverse:
                path = PropertyPath(inverse_path=predicate)
            else:
                path = predicate

            property_shape = PropertyShape(
                shape_name=prop_shape_name,
                path=path,
                class_constraint=classes if strict else None,
                name=prop_shape_name,
                description=field.description,
                defaultValue=field.default,
                **field_metadata,
            )
            property_shape.node_kind = field_metadata["node_kind"]
            property_shapes.append(property_shape)

        return property_shapes, nested_shapes

    @staticmethod
    def _generate_model_shape(
        model_class: type[RdfanticBaseModel],
        target_classes: set[URIRef],
        property_shapes: list[PropertyShape],
        strict: bool,
    ) -> Shape:
        """Generate the main Shape for a model class.

        Parameters
        ----------
        model_class : type[RdfanticBaseModel]
            The model class to generate a shape for.
        target_classes : set[URIRef]
            Set of target class URIs.
        property_shapes : list[PropertyShape]
            List of PropertyShape instances for the model's fields.
        strict : bool
            Whether to enforce strict type constraints.

        Returns
        -------
        Shape
            The SHACL Shape instance for the model.
        """
        shape_name = model_class.Meta.get_shape_name()
        return NodeShape(
            shape_name=shape_name,
            name=shape_name,
            closed=strict,
            ignored_properties=[RDF.type] if strict else None,
            target_class=target_classes,
            property=property_shapes,
        )

    @staticmethod
    def _get_nested_model_classes(
        type_info: TypeInfo,
        covered: set[type],
        strict: bool,
    ) -> tuple[list[URIRef], list[Shape]]:
        """Extract class URIs from nested RDFantic models.

        Parameters
        ----------
        type_info : TypeInfo
            Type information for the field.
        covered : set[type]
            Set of model types already processed.
        strict : bool
            Whether to enforce strict type constraints.

        Returns
        -------
        tuple[list[URIRef], list[Shape]]
            A tuple of (class_uris, nested_shapes).
        """
        from rdfantic.models.base import RdfanticBaseModel  # noqa: PLC0415

        classes: list[URIRef] = []
        nested_shapes: list[Shape] = []

        if (
            isinstance(type_info.item_type, type)
            and issubclass(type_info.item_type, RdfanticBaseModel)
            and type_info.item_type not in covered
        ):
            covered.add(type_info.item_type)
            nested_shapes = ShaclGenerator._export_shacl(type_info.item_type, covered, strict)
            if type_info.item_type.Meta.class_uris is not None:
                classes = list(type_info.item_type.Meta.class_uris)

        return classes, nested_shapes

    @staticmethod
    def _is_node_kind_iri_or_blank(type_info: TypeInfo, field_metadata_obj: RdfanticFieldInfoMetaModel) -> bool:
        """Determine if a field should be serialized as IRI/BlankNode vs Literal.

        Fields are considered IRI or BlankNode if they are:
        - RdfanticBaseModel instances (but not RdfanticConstantValueModel)
        - Values with a term_builder (strings converted to URIs)
        - RdfanticResolvableEnum instances (but not RdfanticLiteralEnum)
        - RDF lists (rdf:List structures)

        Otherwise, they are Literals.

        Parameters
        ----------
        type_info : TypeInfo
            Type information for the field.
        rdfantic_meta : RdfanticFieldInfoMetaModel
            RDF metadata for the field.

        Returns
        -------
        bool
            True if the field should be IRI/BlankNode, False if Literal.
        """
        from rdfantic.models.base import RdfanticBaseModel  # noqa: PLC0415
        from rdfantic.models.constant_value import RdfanticConstantValueModel  # noqa: PLC0415
        from rdfantic.models.enums import RdfanticLiteralEnum, RdfanticResolvableEnum  # noqa: PLC0415

        # Check if it's a RdfanticBaseModel (but not a constant value model)
        is_model = (
            isinstance(type_info.item_type, type)
            and issubclass(type_info.item_type, RdfanticBaseModel)
            and not issubclass(type_info.item_type, RdfanticConstantValueModel)
        )

        # Check if it has a term builder (string → URI conversion)
        has_term_builder = field_metadata_obj.str_term_builder is not None

        # Check if it's a resolvable enum (but not a literal enum)
        is_resolvable_enum = (
            isinstance(type_info.item_type, type)
            and issubclass(type_info.item_type, RdfanticResolvableEnum)
            and not issubclass(type_info.item_type, RdfanticLiteralEnum)
        )

        # Check if it's an RDF list
        is_rdf_list = field_metadata_obj.rdf_list

        return is_model or has_term_builder or is_resolvable_enum or is_rdf_list

    @staticmethod
    def _collect_field_metadata(
        field_info: FieldInfo,
        type_info: TypeInfo,
        strict: bool,
        field_metadata_obj: RdfanticFieldInfoMetaModel,
    ) -> dict[str, object]:
        """Collect SHACL metadata for a field based on its type and constraints.

        Parameters
        ----------
        field_info : FieldInfo
            Field information containing Pydantic constraints and RDF metadata.
        type_info : TypeInfo
            Resolved type information for the field.
        strict : bool
            Whether to enforce strict type constraints in SHACL.
        rdfantic_meta : RdfanticFieldInfoMetaModel | None, optional
            Specific RDF metadata to use. If None, uses the first metadata found on the field.

        Returns
        -------
        dict[str, object]
            Dictionary containing SHACL property shape metadata including:
            - Cardinality constraints (min_count, max_count)
            - Value constraints (min/max inclusive/exclusive)
            - Node kind (IRI, Literal, BlankNode)
            - Datatype if applicable.
        """
        # Local import to avoid circular dependency
        from rdfantic.shacl.models import NodeKindEnum  # noqa: PLC0415

        result: dict[str, object] = {}
        rev_metadata_lookup = {value: key for key, value in field_info.metadata_lookup.items()}

        for descriptor_instance in field_info.metadata:
            descriptor = rev_metadata_lookup.get(type(descriptor_instance), None)

            if descriptor:
                value = getattr(descriptor_instance, descriptor)
                descriptor_key = DESCRIPTOR_MAP.get(descriptor, descriptor) if type_info.is_list else descriptor
                result[descriptor_key] = value

        if not type_info.is_list:
            # There should be a single value only
            result["max_count"] = 1
            if not type_info.contains_none:
                result["min_count"] = 1

        # Determine node kind based on field type and metadata
        if ShaclGenerator._is_node_kind_iri_or_blank(type_info, field_metadata_obj):
            result["node_kind"] = NodeKindEnum.BLANK_NODE_OR_IRI
        else:
            result["node_kind"] = NodeKindEnum.LITERAL

            if field_metadata_obj.datatype:
                result["datatype"] = URIRef(field_metadata_obj.datatype)
            elif strict:
                if datatype := DT_MAP.get(type_info.item_type, None):
                    result["datatype"] = datatype

        return result
