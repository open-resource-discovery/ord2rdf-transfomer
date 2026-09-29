"""RDFantic: A Pydantic-based framework for RDF graph serialization and SHACL generation.

This package provides tools for:
- Defining Pydantic models with RDF metadata
- Serializing models to RDF graphs
- Generating SHACL shapes from model definitions

Package Structure
-----------------
- models/: Metadata classes, enums, field info (no base_model dependency)
- serialization/: RDF and SHACL serialization logic
- context/: Materialization contexts for URI resolution
- internal/: Framework internals (state, type analysis, protocols)
- shacl/: SHACL vocabulary models (Shape, PropertyShape, etc.)
"""

from rdfantic.context.base import MaterializationContext
from rdfantic.context.shacl import ShaclMaterializationContext
from rdfantic.exceptions import RdfanticSerializationError
from rdfantic.internal.path_element import PathElement
from rdfantic.models.base import RdfanticBaseModel
from rdfantic.models.constant_value import RdfanticConstantValueModel
from rdfantic.models.enums import RdfanticLiteralEnum, RdfanticResolvableEnum
from rdfantic.models.field_info import RdfanticFieldInfoMetaModel, field
from rdfantic.models.metadata import RdfanticModelMetadata

__all__ = (
    # Core model
    "RdfanticBaseModel",
    # Model classes
    "RdfanticConstantValueModel",
    "RdfanticLiteralEnum",
    "RdfanticResolvableEnum",
    # Metadata
    "RdfanticFieldInfoMetaModel",
    "RdfanticModelMetadata",
    # Contexts
    "MaterializationContext",
    "ShaclMaterializationContext",
    "PathElement",
    # Exceptions
    "RdfanticSerializationError",
    # Deprecated (kept for backward compatibility)
    "field",
)
