"""Container for RDFantic framework-specific state."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from rdfantic.context.base import MaterializationContext
    from rdfantic.internal.path_element import PathElement
    from rdfantic.models.base import RdfanticBaseModel


@dataclass
class RdfanticState:
    """Container for RDFantic framework-specific state.

    This class encapsulates all internal state managed by the RDFantic framework,
    keeping it separate from user-defined model fields to avoid naming conflicts.

    Attributes
    ----------
    id : UUID
        Unique identifier for this model instance.
    parent : RdfanticBaseModel | None
        Parent model in the serialization hierarchy.
    ctx : MaterializationContext | None
        Materialization context (set during model_dump_rdf).
    path : list[PathElement]
        Path from root to this model in the hierarchy.
    """

    _id: UUID = field(default_factory=uuid.uuid4)
    _parent: RdfanticBaseModel | None = None
    _ctx: MaterializationContext | None = None
    _path: list[PathElement] = field(default_factory=list)

    @property
    def id(self) -> UUID:
        """Get the unique identifier for this model instance."""
        return self._id

    @property
    def parent(self) -> RdfanticBaseModel | None:
        """Get the parent model in the serialization hierarchy."""
        return self._parent

    @parent.setter
    def parent(self, value: RdfanticBaseModel | None) -> None:
        """Set the parent model in the serialization hierarchy."""
        self._parent = value

    @property
    def ctx(self) -> MaterializationContext:
        """Get the materialization context for this instance.

        Returns
        -------
        MaterializationContext
            The context set during model_dump_rdf.

        Raises
        ------
        RuntimeError
            If no context has been set on this instance.
        """
        if self._ctx is None:
            raise RuntimeError(
                "No context set for this model instance. "
                "Context is automatically set when calling model_dump_rdf(context=...)."
            )
        return self._ctx

    @ctx.setter
    def ctx(self, value: MaterializationContext) -> None:
        """Set the materialization context for this instance."""
        self._ctx = value

    @property
    def path(self) -> list[PathElement]:
        """Get the path from root to this model in the hierarchy."""
        return self._path

    @path.setter
    def path(self, value: list[PathElement]) -> None:
        """Set the path from root to this model in the hierarchy."""
        self._path = value
