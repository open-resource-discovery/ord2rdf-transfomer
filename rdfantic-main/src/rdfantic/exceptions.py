"""Exceptions for RDFantic serialization errors."""


class RdfanticSerializationError(Exception):
    """Raised when RDF serialization encounters an invalid state or configuration."""

    pass


class RdfanticModelError(Exception):
    """Raised when there are modeling errors encounters an invalid state or configuration."""

    pass
