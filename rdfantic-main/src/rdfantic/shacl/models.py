"""Pydantic models for SHACL (Shapes Constraint Language) vocabulary.

Generated from: https://www.w3.org/ns/shacl.ttl

SHACL is used to validate RDF graphs against a set of conditions/constraints.

This module uses the Pydantic v2 Annotated pattern with RdfanticFieldInfoMetaModel
to attach RDF metadata to model fields.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from rdflib import RDFS, SH, XSD, BNode, Literal, URIRef

from rdfantic.models.base import RdfanticBaseModel
from rdfantic.models.enums import RdfanticResolvableEnum
from rdfantic.models.field_info import RdfanticFieldInfoMetaModel
from rdfantic.models.metadata import RdfanticModelMetadata

# ============================================================================
# Enumerations
# ============================================================================


class NodeKindEnum(RdfanticResolvableEnum):
    """RDF node types in SHACL."""

    BLANK_NODE = "BlankNode"
    IRI = "IRI"
    LITERAL = "Literal"
    BLANK_NODE_OR_IRI = "BlankNodeOrIRI"
    BLANK_NODE_OR_LITERAL = "BlankNodeOrLiteral"
    IRI_OR_LITERAL = "IRIOrLiteral"

    @property
    def rdf_term(self) -> URIRef | Literal:
        """Get the SHACL URI representation of this node kind."""
        return {
            NodeKindEnum.BLANK_NODE_OR_IRI: SH.BlankNodeOrIRI,
            NodeKindEnum.IRI: SH.IRI,
            NodeKindEnum.LITERAL: SH.Literal,
            NodeKindEnum.BLANK_NODE_OR_LITERAL: SH.BlankNodeOrLiteral,
            NodeKindEnum.IRI_OR_LITERAL: SH.IRIOrLiteral,
            NodeKindEnum.BLANK_NODE: SH.BlankNode,
        }[self]


class SeverityEnum(RdfanticResolvableEnum):
    """Validation severity levels."""

    INFO = "Info"
    WARNING = "Warning"
    VIOLATION = "Violation"

    @property
    def rdf_term(self) -> URIRef | Literal:
        """Get the SHACL URI representation of this severity."""
        return {SeverityEnum.WARNING: SH.Warning, SeverityEnum.INFO: SH.Info, SeverityEnum.VIOLATION: SH.Violation}[
            self
        ]


# ============================================================================
# SPARQL Components
# ============================================================================


class PrefixDeclaration(RdfanticBaseModel):
    """Namespace prefix declaration."""

    class Meta(RdfanticModelMetadata):
        """Metadata for PrefixDeclaration."""

        name = "PrefixDeclaration"
        class_uris = {SH.PrefixDeclaration}
        term_builder = lambda self: BNode(self.rdfantic.id)  # noqa: E731

    prefix: Annotated[
        str, RdfanticFieldInfoMetaModel(predicates={SH.prefix}), Field(description="Short prefix (e.g., 'ex')")
    ]
    namespace: Annotated[
        HttpUrl, RdfanticFieldInfoMetaModel(predicates={SH.namespace}), Field(description="Full namespace URI")
    ]


class SPARQLExecutable(BaseModel):
    """Base for SPARQL-based executables."""

    prefixes: PrefixDeclaration | None = Field(None, description="Namespace prefixes")


class SPARQLConstraint(SPARQLExecutable):
    """SPARQL-based constraint."""

    select: str | None = Field(None, description="SPARQL SELECT query")
    ask: str | None = Field(None, description="SPARQL ASK query")
    message: str | list[str] | None = Field(None, description="Violation message")
    deactivated: bool | None = Field(None, description="Whether constraint is disabled")


class SPARQLAskExecutable(SPARQLExecutable):
    """SPARQL ASK query."""

    ask: str = Field(..., description="SPARQL ASK query string")


class SPARQLSelectExecutable(SPARQLExecutable):
    """SPARQL SELECT query."""

    select: str = Field(..., description="SPARQL SELECT query string")


class SPARQLConstructExecutable(SPARQLExecutable):
    """SPARQL CONSTRUCT query."""

    construct_: str = Field(..., description="SPARQL CONSTRUCT query string", alias="construct")


class SPARQLUpdateExecutable(SPARQLExecutable):
    """SPARQL UPDATE operation."""

    update: str = Field(..., description="SPARQL UPDATE string")


class SPARQLAskValidator(SPARQLAskExecutable):
    """Validator using SPARQL ASK - returns true for conforming nodes."""


class ResultAnnotation(BaseModel):
    """Derives extra fields for validation results from SPARQL bindings."""

    model_config = ConfigDict(populate_by_name=True)

    annotation_property: str = Field(..., alias="annotationProperty", description="Property to set on result")
    annotation_var_name: str | None = Field(None, alias="annotationVarName", description="SPARQL variable name")
    annotation_value: Any | None = Field(None, alias="annotationValue", description="Default value")


class SPARQLSelectValidator(SPARQLSelectExecutable):
    """Validator using SPARQL SELECT - produces bindings for violations."""

    model_config = ConfigDict(populate_by_name=True)

    result_annotation: list[ResultAnnotation] | None = Field(None, alias="resultAnnotation")


# ============================================================================
# Targets
# ============================================================================


class Target(RdfanticBaseModel):
    """Extension mechanism for target selection."""

    class Meta(RdfanticModelMetadata):
        """Metadata for Target."""

        name = "Target"
        class_uris = {SH.Target}
        term_builder = lambda self: BNode(self.rdfantic.id)  # noqa: E731


class SPARQLTarget(Target):
    """SPARQL-based node selection."""

    model_config = ConfigDict(populate_by_name=True)

    select: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={SH.select}),
        Field(description="SPARQL SELECT query that returns ?this bindings"),
    ]
    prefixes: Annotated[
        PrefixDeclaration | None,
        RdfanticFieldInfoMetaModel(predicates={SH.prefixes}),
        Field(default=None, description="Namespace prefixes"),
    ]


# ============================================================================
# UI/Organization
# ============================================================================


class PropertyGroup(BaseModel):
    """Groups related properties for UI purposes."""

    label: str | list[str] | None = Field(None, description="Group label")
    order: int | Decimal | None = Field(None, description="Display order")


# ============================================================================
# Core Shape Classes
# ============================================================================


class Shape(RdfanticBaseModel):
    """Base class for SHACL shapes.

    A collection of constraints that may be targeted for certain nodes.
    """

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    class Meta(RdfanticModelMetadata):
        """Metadata for Shape."""

        name = "Shape"
        class_uris = {SH.Shape}
        term_builder = lambda self: self.rdfantic.ctx.create_uri([], self.shape_name)  # noqa: E731

    shape_name: str = Field(..., description="Shape name")

    # Targeting
    target_class: Annotated[
        list[URIRef] | None,
        RdfanticFieldInfoMetaModel(predicates={SH.targetClass}),
        Field(default=None, alias="targetClass", description="All instances of the class must conform"),
    ]
    target_node: Annotated[
        list[URIRef] | None,
        RdfanticFieldInfoMetaModel(predicates={SH.targetNode}),
        Field(default=None, alias="targetNode", description="Specific nodes that must conform"),
    ]
    target_objects_of: Annotated[
        list[URIRef] | None,
        RdfanticFieldInfoMetaModel(predicates={SH.targetObjectsOf}),
        Field(default=None, alias="targetObjectsOf", description="Objects of these properties must conform"),
    ]
    target_subjects_of: Annotated[
        list[URIRef] | None,
        RdfanticFieldInfoMetaModel(predicates={SH.targetSubjectsOf}),
        Field(default=None, alias="targetSubjectsOf", description="Subjects of these properties must conform"),
    ]
    target: Annotated[
        list[Target] | None,
        RdfanticFieldInfoMetaModel(predicates={SH.target}),
        Field(default=None, description="Extension-based targeting mechanism"),
    ]

    # Shape configuration
    deactivated: bool | None = Field(None, description="Whether this shape is disabled")
    severity: SeverityEnum | None = Field(None, description="Severity level for validation results")
    message: str | list[str] | None = Field(None, description="Human-readable message for violations")

    # Logical operators
    and_shapes: list[Shape] | None = Field(None, alias="and", description="All shapes must validate")
    or_shapes: list[Shape] | None = Field(None, alias="or", description="At least one shape must validate")
    xone_shapes: list[Shape] | None = Field(None, alias="xone", description="Exactly one shape must validate")
    not_shape: Shape | None = Field(None, alias="not", description="This shape must not validate")

    # Value constraints
    node: NodeShape | None = Field(None, description="Values must conform to this node shape")
    property: Annotated[
        list[PropertyShape] | None,
        RdfanticFieldInfoMetaModel(predicates={SH.property}),
        Field(default=None, description="Property constraints"),
    ]

    # Value type constraints
    class_constraint: Annotated[
        list[URIRef] | None,
        RdfanticFieldInfoMetaModel(predicates={URIRef(SH + "class")}),
        Field(default_factory=list, alias="class", description="Values must be instances of this class"),
    ]
    datatype: Annotated[
        URIRef | None,
        RdfanticFieldInfoMetaModel(predicates={SH.datatype}),
        Field(default=None, description="Values must have this datatype"),
    ]
    node_kind: Annotated[
        NodeKindEnum | None,
        RdfanticFieldInfoMetaModel(predicates={SH.nodeKind}),
        Field(default=None, alias="nodeKind", description="Type of RDF node"),
    ]

    # Cardinality constraints
    min_count: Annotated[
        int | None,
        RdfanticFieldInfoMetaModel(predicates={SH.minCount}, datatype=XSD.integer),
        Field(default=None, alias="minCount", ge=0, description="Minimum number of values"),
    ]
    max_count: Annotated[
        int | None,
        RdfanticFieldInfoMetaModel(predicates={SH.maxCount}, datatype=XSD.integer),
        Field(default=None, alias="maxCount", ge=0, description="Maximum number of values"),
    ]

    # String constraints
    pattern: Annotated[
        str | None,
        RdfanticFieldInfoMetaModel(predicates={SH.pattern}),
        Field(default=None, description="Regex pattern for string matching"),
    ]
    flags: str | None = Field(None, description="Regex flags (e.g., 'i' for case-insensitive)")

    min_length: Annotated[
        int | None,
        RdfanticFieldInfoMetaModel(predicates={SH.minLength}, datatype=XSD.integer),
        Field(default=None, alias="minLength", ge=0, description="Minimum string length"),
    ]
    max_length: Annotated[
        int | None,
        RdfanticFieldInfoMetaModel(predicates={SH.maxLength}, datatype=XSD.integer),
        Field(default=None, alias="maxLength", ge=0, description="Maximum string length"),
    ]
    language_in: list[str] | None = Field(None, alias="languageIn", description="Allowed language tags")
    unique_lang: bool | None = Field(None, alias="uniqueLang", description="Each language tag at most once")

    # Numeric range constraints
    min_exclusive: Annotated[
        int | float | Decimal | None,
        RdfanticFieldInfoMetaModel(predicates={SH.minExclusive}),
        Field(default=None, alias="minExclusive", description="Exclusive lower bound"),
    ]
    min_inclusive: Annotated[
        int | float | Decimal | None,
        RdfanticFieldInfoMetaModel(predicates={SH.minInclusive}),
        Field(default=None, alias="minInclusive", description="Inclusive lower bound"),
    ]
    max_exclusive: Annotated[
        int | float | Decimal | None,
        RdfanticFieldInfoMetaModel(predicates={SH.maxExclusive}),
        Field(default=None, alias="maxExclusive", description="Exclusive upper bound"),
    ]
    max_inclusive: Annotated[
        int | float | Decimal | None,
        RdfanticFieldInfoMetaModel(predicates={SH.maxInclusive}),
        Field(default=None, alias="maxInclusive", description="Inclusive upper bound"),
    ]

    # Set constraints
    in_values: list[Any] | None = Field(None, alias="in", description="Enumeration of allowed values")
    has_value: Any | None = Field(None, alias="hasValue", description="Must have this specific value")

    # Property relationship constraints
    equals: str | None = Field(None, description="Values must equal values of this property")
    disjoint: str | None = Field(None, description="Values must not overlap with this property")
    less_than: str | None = Field(None, alias="lessThan", description="Values must be less than this property's values")
    less_than_or_equals: str | None = Field(
        None, alias="lessThanOrEquals", description="Values must be ≤ this property's values"
    )

    # Closed shape constraint
    closed: Annotated[
        bool | None,
        RdfanticFieldInfoMetaModel(predicates={SH.closed}, datatype=XSD.boolean),
        Field(default=None, description="Only explicitly declared properties allowed"),
    ]
    ignored_properties: Annotated[
        list[URIRef] | None,
        RdfanticFieldInfoMetaModel(predicates={SH.ignoredProperties}, rdf_list=True),
        Field(default=None, alias="ignoredProperties", description="Properties to ignore when closed=true"),
    ]

    # Qualified cardinality
    qualified_min_count: int | None = Field(None, alias="qualifiedMinCount", ge=0)
    qualified_max_count: int | None = Field(None, alias="qualifiedMaxCount", ge=0)
    qualified_value_shape: Shape | None = Field(None, alias="qualifiedValueShape")
    qualified_value_shapes_disjoint: bool | None = Field(None, alias="qualifiedValueShapesDisjoint")

    # SPARQL constraints
    sparql: list[SPARQLConstraint] | None = Field(None, description="SPARQL-based constraints")

    # UI/Metadata
    name: Annotated[
        str | list[str] | None,
        RdfanticFieldInfoMetaModel(predicates={SH.name, RDFS.label}),
        Field(default=None, description="Human-readable label"),
    ]
    description: Annotated[
        str | list[str] | None,
        RdfanticFieldInfoMetaModel(predicates={SH.description, RDFS.comment}),
        Field(default=None, description="Explanation of the shape"),
    ]
    order: int | Decimal | None = Field(None, description="Relative ordering hint")
    group: PropertyGroup | None = Field(None, description="Property grouping")
    default_value: Any | None = Field(None, alias="defaultValue", description="Default value for properties")


class NodeShape(Shape):
    """Specifies constraints for focus nodes."""

    class Meta(RdfanticModelMetadata):
        """Metadata for Shape."""

        name = "NodeShape"
        class_uris = {SH.NodeShape}
        term_builder = lambda self: self.rdfantic.ctx.create_uri([], self.shape_name)  # noqa: E731


# ============================================================================
# Property Paths
# ============================================================================


class PropertyPath(RdfanticBaseModel):
    """Property path expressions for navigation in RDF graphs."""

    class Meta(RdfanticModelMetadata):
        """Metadata for PropertyShape."""

        name = "PropertyPath"
        class_uris = {}
        term_builder = lambda self: BNode(self.rdfantic.id)  # noqa: E731

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    inverse_path: Annotated[
        URIRef | None,
        RdfanticFieldInfoMetaModel(predicates={SH.inversePath}),
        Field(default=None, alias="inversePath", description="Reverse direction traversal"),
    ]

    alternative_path: list[str | PropertyPath] | None = Field(
        None, alias="alternativePath", description="Multiple path options"
    )
    zero_or_more_path: str | PropertyPath | None = Field(None, alias="zeroOrMorePath", description="Kleene star (*)")
    one_or_more_path: str | PropertyPath | None = Field(None, alias="oneOrMorePath", description="Kleene plus (+)")
    zero_or_one_path: str | PropertyPath | None = Field(None, alias="zeroOrOnePath", description="Optional (?)")


class PropertyShape(Shape):
    """Specifies constraints on property values for a given property path."""

    class Meta(RdfanticModelMetadata):
        """Metadata for PropertyShape."""

        name = "PropertyShape"
        class_uris = {SH.PropertyShape}
        term_builder = lambda self: BNode(self.rdfantic.id)  # noqa: E731

    path: Annotated[
        URIRef | PropertyPath | None,
        RdfanticFieldInfoMetaModel(predicates={SH.path}),
        Field(default=None, description="Property or property path to constrain"),
    ]


# ============================================================================
# Parameters and Components
# ============================================================================


class Parameter(BaseModel):
    """Declaration of function or constraint component parameters."""

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    path: str = Field(..., description="Parameter name/path")
    datatype: str | None = Field(None, description="Expected datatype")
    class_constraint: str | None = Field(None, alias="class", description="Expected class")
    node_kind: NodeKindEnum | None = Field(None, alias="nodeKind")
    optional: bool | None = Field(None, description="Whether parameter is optional")
    description: str | list[str] | None = Field(None, description="Parameter documentation")
    name: str | list[str] | None = Field(None, description="Human-readable name")


class Parameterizable(BaseModel):
    """Base for functions and constraint components."""

    model_config = ConfigDict(populate_by_name=True)

    parameter: list[Parameter] | None = Field(None, description="Parameter declarations")
    label_template: str | list[str] | None = Field(
        None, alias="labelTemplate", description="Template for instance labeling"
    )


class Validator(BaseModel):
    """Processes constraint definitions."""


class ConstraintComponent(Parameterizable):
    """Defines reusable validation rule implementations."""

    model_config = ConfigDict(populate_by_name=True)

    validator: list[Validator] | None = Field(None, description="General validators")
    node_validator: list[Validator] | None = Field(None, alias="nodeValidator", description="Node shape validators")
    property_validator: list[Validator] | None = Field(
        None, alias="propertyValidator", description="Property shape validators"
    )


# ============================================================================
# Functions
# ============================================================================


class Function(Parameterizable):
    """Reusable logic definition."""

    model_config = ConfigDict(populate_by_name=True)

    return_type: str | None = Field(None, alias="returnType", description="Expected output type")


class SPARQLFunction(Function, SPARQLExecutable):
    """SPARQL-based function."""

    ask: str | None = Field(None)
    select: str | None = Field(None)
    construct_: str | None = Field(None, alias="construct")


# ============================================================================
# Expressions (Advanced)
# ============================================================================


class Expression(BaseModel):
    """Node expression for evaluation."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: Any | None = Field(None, description="Input node expression")
    filter_shape: Shape | None = Field(None, alias="filterShape", description="Conformance requirement")
    intersection: list[Expression] | None = Field(None, description="Set intersection")
    union: list[Expression] | None = Field(None, description="Set union")
