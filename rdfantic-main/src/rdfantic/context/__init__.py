"""Materialization contexts for RDFantic serialization."""

from rdfantic.context.base import MaterializationContext
from rdfantic.context.shacl import ShaclMaterializationContext

__all__ = (
    "MaterializationContext",
    "ShaclMaterializationContext",
)
