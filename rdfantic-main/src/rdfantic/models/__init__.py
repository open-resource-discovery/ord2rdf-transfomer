"""User-facing model classes for RDFantic.

This subpackage contains metadata classes, enums, and field info that don't
depend on RdfanticBaseModel. Classes that inherit from RdfanticBaseModel
(like RdfanticConstantValueModel) are intentionally NOT exported here to
avoid circular imports - import them from the main rdfantic package instead.
"""

from rdfantic.models.enums import RdfanticLiteralEnum, RdfanticResolvableEnum
from rdfantic.models.field_info import RdfanticFieldInfoMetaModel, field
from rdfantic.models.metadata import RdfanticModelMetadata

__all__ = (
    "RdfanticLiteralEnum",
    "RdfanticResolvableEnum",
    "RdfanticFieldInfoMetaModel",
    "RdfanticModelMetadata",
    "field",
)
