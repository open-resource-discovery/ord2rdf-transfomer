"""Utility functions for URI manipulation and validation."""

import urllib

from rdflib import URIRef


def _validate_input(value: str) -> str:
    """
    Validate input value.

    Parameters
    ----------
    value : str
        The value to validate.

    Returns
    -------
    str
        The URL-encoded value.

    Raises
    ------
    ValueError
        If the value is empty or contains path traversal sequences.
    """
    if not value:
        raise ValueError("Path segment cannot be empty.")
    if "../" in value or "./" in value:
        raise ValueError("Path traversal sequences are not allowed.")
    return urllib.parse.quote(value, safe="~")


def join_uri(base_url, path, fragment=None) -> URIRef:
    """
    Join base URL, path, and fragment into a URI.

    Parameters
    ----------
    base_url : str
        The base URL.
    path : list[str]
        List of path segments to join.
    fragment : str, optional
        Optional fragment identifier.

    Returns
    -------
    URIRef
        The constructed URI.
    """
    uri = urllib.parse.urljoin(base_url, "/".join(path))
    if fragment:  # noqa: F821
        uri += f"#{_validate_input(fragment)}"
    return URIRef(uri)
