"""ShaclMaterializationContext — shared configuration for an RDF serialization run."""

from __future__ import annotations


class ShaclMaterializationContext:
    """Carries shared configuration passed to every :meth:`model_dump_rdf` call.

    Parameters
    ----------
    base_uri:
        Base URI used as a namespace root for resolving local identity.
        Example: ``"https://open-resource-discovery.org/instance/"``
    """

    def __init__(self, base_uri: str) -> None:
        if not base_uri:
            raise ValueError("base_uri must be a non-empty string")
        self.base_uri: str = base_uri

    def __repr__(self) -> str:  # pragma: no cover
        return f"ShaclMaterializationContext(base_uri={self.base_uri!r})"
