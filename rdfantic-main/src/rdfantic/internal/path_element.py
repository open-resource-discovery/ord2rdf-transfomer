"""Path element representation for hierarchical RDF structures."""

from typing import NamedTuple


class PathElement(NamedTuple):
    """Represents a single element in a hierarchical path."""

    element_type: str
    identifier: str
