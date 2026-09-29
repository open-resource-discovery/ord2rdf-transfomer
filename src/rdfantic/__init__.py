"""RDFantic — Pydantic v2-based declarative RDF serialisation and SHACL shape generation.

This package is vendored as part of ``ord2rdf-transformer`` and provides the
declarative RDF/SHACL layer built on top of Pydantic v2.  Import it as::

    from rdfantic import RdfanticBaseModel, RdfanticModelMetadata, ...

Public API
----------
- :class:`RdfanticBaseModel` — Pydantic v2 base model with ``model_dump_rdf`` and
  ``model_dump_shacl``
- :class:`RdfanticModelMetadata` — inner ``Meta`` configuration class
- :class:`RdfanticFieldInfoMetaModel` — per-field RDF annotation metadata
- :class:`ShaclMaterializationContext` — shared context for a serialisation run
"""

from .base_model import RdfanticBaseModel
from .context import ShaclMaterializationContext
from .field_info import RdfanticFieldInfoMetaModel
from .metadata import RdfanticModelMetadata

__all__ = [
    "RdfanticBaseModel",
    "ShaclMaterializationContext",
    "RdfanticFieldInfoMetaModel",
    "RdfanticModelMetadata",
]

__version__ = "0.1.0"
