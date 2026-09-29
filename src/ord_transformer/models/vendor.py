"""Vendor model — organisation that owns / creates ORD resources."""

from __future__ import annotations

from typing import Annotated, Optional

from pydantic import Field

from rdfantic import RdfanticFieldInfoMetaModel, RdfanticModelMetadata

from ..namespaces import ORD, ord_id_to_uri
from .base import ORDBaseModel


class Vendor(ORDBaseModel):
    """An organisation that creates or is responsible for ORD resources.

    Maps to ``ord:Vendor``.
    """

    class Meta(RdfanticModelMetadata):
        name = "Vendor"
        class_uris = {ORD.Vendor}
        term_builder = lambda self: ord_id_to_uri(self.ord_id)  # noqa: E731

    ord_id: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
        Field(alias="ordId", description="ORD ID of the vendor, e.g. 'acme.demo:vendor:AcmeCorp:'"),
    ]
    local_id: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.localId}),
        Field(alias="localId", default=None),
    ]
    title: Annotated[
        str,
        RdfanticFieldInfoMetaModel(predicates={ORD.title}),
        Field(description="Human-readable vendor name"),
    ]
    short_description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.shortDescription}),
        Field(alias="shortDescription", default=None),
    ]
    description: Annotated[
        Optional[str],
        RdfanticFieldInfoMetaModel(predicates={ORD.description}),
        Field(default=None),
    ]
