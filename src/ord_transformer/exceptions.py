"""Custom exceptions for the ORD RDF Transformer."""

from __future__ import annotations


class ORDTransformerError(Exception):
    """Base exception for all ORD transformer errors."""


class ORDParseError(ORDTransformerError):
    """Raised when the ORD JSON document cannot be parsed or validated."""


class SHACLGenerationError(ORDTransformerError):
    """Raised when SHACL shape generation fails."""


class SHACLValidationError(ORDTransformerError):
    """Raised when SHACL validation fails with a hard error (not a conforms=False result)."""


class VocabularyNotFoundError(ORDTransformerError):
    """Raised when the ORD vocabulary TTL file cannot be located."""
