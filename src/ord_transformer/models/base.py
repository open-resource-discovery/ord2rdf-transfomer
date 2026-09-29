"""Shared helpers and base mixin for all ORD entity models."""

from __future__ import annotations

from pydantic import ConfigDict

from rdfantic import RdfanticBaseModel
from ..namespaces import ord_id_to_uri


class ORDBaseModel(RdfanticBaseModel):
    """Pydantic model base for all ORD entities.

    Enables:
    - ``populate_by_name=True`` — allows both the Python snake_case name and
      the JSON camelCase alias when constructing from a dict.
    - ``extra="ignore"`` — silently drops unknown JSON keys (forward-compat).
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )


# Re-export the URI factory so models only need to import from this module
__all__ = ["ORDBaseModel", "ord_id_to_uri"]
