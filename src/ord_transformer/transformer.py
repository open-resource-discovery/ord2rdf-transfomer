"""ORDTransformer — load an ORD JSON document and produce an rdflib Graph."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rdflib import Graph

from rdfantic import ShaclMaterializationContext

from .exceptions import ORDParseError
from .models import (
    ALL_MODELS,
    Agent,
    ApiResource,
    Capability,
    ConsumptionBundle,
    DataProduct,
    EntityType,
    EventResource,
    Group,
    GroupType,
    IntegrationDependency,
    OrdDocument,
    Overlay,
    Package,
    Product,
    Tombstone,
    Vendor,
)
from .namespaces import bind_standard_namespaces

# Mapping: ORD JSON top-level array key → RDFantic model class
# All keys follow the ORD spec document structure.
_ARRAY_KEY_TO_MODEL: dict[str, type] = {
    # Taxonomy
    "packages": Package,
    "consumptionBundles": ConsumptionBundle,
    "vendors": Vendor,
    "products": Product,
    "groups": Group,
    "groupTypes": GroupType,
    # Resources
    "apiResources": ApiResource,
    "eventResources": EventResource,
    "entityTypes": EntityType,
    "dataProducts": DataProduct,
    "capabilities": Capability,
    "integrationDependencies": IntegrationDependency,
    "agents": Agent,
    "overlays": Overlay,
    # Lifecycle
    "tombstones": Tombstone,
}


class ORDTransformer:
    """Transform an ORD JSON document into an ``rdflib.Graph``.

    Parameters
    ----------
    base_instance_uri:
        Root URI used as the ``base_uri`` for the
        :class:`~rdfantic.ShaclMaterializationContext`.
        Defaults to ``"https://open-resource-discovery.org/instance/"``.

    Examples
    --------
    .. code-block:: python

        transformer = ORDTransformer()
        graph = transformer.transform_file("data/samples/sample_ord.json")
        graph.serialize("output/ord_data.ttl", format="turtle")
    """

    def __init__(
        self,
        base_instance_uri: str = "https://open-resource-discovery.org/instance/",
    ) -> None:
        self.context = ShaclMaterializationContext(base_instance_uri)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def transform_file(self, path: str | Path) -> Graph:
        """Load an ORD JSON file from *path* and return the transformed graph.

        Parameters
        ----------
        path:
            Filesystem path to the ORD JSON document.

        Returns
        -------
        rdflib.Graph
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"ORD JSON file not found: {path}")
        with path.open(encoding="utf-8") as fh:
            doc = json.load(fh)
        return self.transform(doc)

    def transform(self, ord_doc: dict[str, Any]) -> Graph:
        """Transform an already-parsed ORD JSON dict into an ``rdflib.Graph``.

        Parameters
        ----------
        ord_doc:
            A Python dict representing the ORD document (as returned by
            ``json.load``).

        Returns
        -------
        rdflib.Graph
            A graph with all RDF triples for the document and its resources.
        """
        g = Graph()
        bind_standard_namespaces(g)

        # ── Serialize the top-level Document ──────────────────────────────────
        try:
            doc_model = OrdDocument.model_validate(ord_doc)
        except Exception as exc:
            raise ORDParseError(f"Failed to parse ORD document header: {exc}") from exc

        g += doc_model.model_dump_rdf(
            context=self.context,
            parent=None,
            predicates=set(),
        )

        # ── Serialize each top-level entity array ─────────────────────────────
        for json_key, model_cls in _ARRAY_KEY_TO_MODEL.items():
            items = ord_doc.get(json_key, []) or []
            for item_dict in items:
                try:
                    instance = model_cls.model_validate(item_dict)
                except Exception as exc:
                    raise ORDParseError(
                        f"Failed to parse {json_key} item {item_dict.get('ordId', '?')}: {exc}"
                    ) from exc

                g += instance.model_dump_rdf(
                    context=self.context,
                    parent=None,
                    predicates=set(),
                )

        return g

    # ------------------------------------------------------------------
    # Convenience: serialize directly to a file
    # ------------------------------------------------------------------

    def transform_to_file(
        self,
        ord_path: str | Path,
        output_path: str | Path,
        fmt: str = "turtle",
    ) -> Path:
        """Transform *ord_path* and write the RDF graph to *output_path*.

        Parameters
        ----------
        ord_path:
            Input ORD JSON file.
        output_path:
            Destination RDF file.
        fmt:
            rdflib serialization format: ``"turtle"``, ``"n3"``,
            ``"nt"``, ``"json-ld"``, ``"xml"``.

        Returns
        -------
        pathlib.Path
            The resolved output path.
        """
        graph = self.transform_file(ord_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        graph.serialize(str(output_path), format=fmt)
        return output_path
