"""URI builder utilities for SHACL shapes."""

from rdflib import URIRef

from rdfantic.utils import join_uri


class ShaclUriBuilder:
    """URI Builder class for SHACL URIS."""

    @staticmethod
    def create_shape_uri(base_uri: str, path: list[str], name: str) -> URIRef:
        """
        Build a URI by concatenating the base URI with the provided arguments.

        Parameters
        ----------
        base_uri : str
            The base URI to which the arguments will be appended.
        path : list[str]
            The path to be appended.
        name : str
            A name to which the arguments will be appended.

        Returns
        -------
        URIRef
            A complete URI formed by concatenating the base URI and the arguments.
        """
        path_ = path.copy()
        path_.append(name)
        return join_uri(base_uri, path_)
