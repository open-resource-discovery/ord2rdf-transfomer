"""RdfanticBaseModel — Pydantic v2 base with RDF serialization and SHACL generation."""

from __future__ import annotations

import typing
from datetime import date, datetime
from typing import Any, Optional, Set, get_args, get_origin

from pydantic import BaseModel
from rdflib import XSD, BNode, Graph, Literal, RDF, SH, URIRef

from .context import ShaclMaterializationContext
from .field_info import RdfanticFieldInfoMetaModel
from .metadata import RdfanticModelMetadata

# ---------------------------------------------------------------------------
# XSD datatype inference
# ---------------------------------------------------------------------------

_PYTHON_TO_XSD: dict[type, URIRef] = {
    str: XSD.string,
    int: XSD.integer,
    float: XSD.decimal,
    bool: XSD.boolean,
    datetime: XSD.dateTime,
    date: XSD.date,
}


def _xsd_for(python_type: type) -> Optional[URIRef]:
    """Return the XSD datatype URI for a Python scalar type, or None."""
    return _PYTHON_TO_XSD.get(python_type)


# ---------------------------------------------------------------------------
# Annotation introspection
# ---------------------------------------------------------------------------

def _unwrap(annotation: Any) -> tuple[Any, bool, bool]:
    """Recursively strip ``Optional`` / ``List`` wrappers.

    Returns
    -------
    (inner_type, is_optional, is_list)
        *inner_type* is the core Python type (e.g. ``str``, ``Package``).
        *is_optional* is True if the annotation included ``None``.
        *is_list* is True if the annotation was ``List[T]``.
    """
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Optional[T] == Union[T, None]
    if origin is typing.Union:
        is_optional = type(None) in args
        non_none = [a for a in args if a is not type(None)]
        inner = non_none[0] if len(non_none) == 1 else non_none[0] if non_none else str
        inner_type, _, is_list = _unwrap(inner)
        return inner_type, is_optional, is_list

    # List[T]
    if origin is list:
        inner = args[0] if args else str
        inner_type, _, _ = _unwrap(inner)
        return inner_type, False, True

    # Bare type
    return annotation, False, False


# ---------------------------------------------------------------------------
# RdfanticBaseModel
# ---------------------------------------------------------------------------

class RdfanticBaseModel(BaseModel):
    """Pydantic v2 base model that can serialize to RDF and generate SHACL shapes.

    Subclasses must define an inner ``Meta`` class that inherits from
    :class:`~rdfantic.RdfanticModelMetadata` and sets at minimum ``class_uris``
    and ``term_builder``::

        class Package(RdfanticBaseModel):
            class Meta(RdfanticModelMetadata):
                name = "Package"
                class_uris = {ORD.Package}
                term_builder = lambda self: URIRef(f"https://example.org/{self.ord_id}")

            ord_id: Annotated[
                str,
                RdfanticFieldInfoMetaModel(predicates={ORD.ordId}),
                Field(alias="ordId"),
            ]
    """

    class Meta(RdfanticModelMetadata):
        pass

    # ------------------------------------------------------------------
    # Public instance API
    # ------------------------------------------------------------------

    def model_dump_rdf(
        self,
        context: ShaclMaterializationContext,
        parent: Optional[URIRef | BNode],
        predicates: Set[URIRef],
    ) -> Graph:
        """Serialize this instance to an ``rdflib.Graph``.

        Parameters
        ----------
        context:
            Shared materialization context (carries the ``base_uri``).
        parent:
            Subject node of the *parent* model, if this model is being
            embedded inside another.  Pass ``None`` for top-level entities.
        predicates:
            RDF predicates that should link *parent* → *this subject*.
            Ignored when *parent* is ``None``.

        Returns
        -------
        rdflib.Graph
            A fresh graph containing all triples for this instance (and any
            recursively embedded models).
        """
        g = Graph()
        meta = self.__class__.Meta

        # Build subject node
        subject: URIRef | BNode
        if meta.term_builder is not None:
            subject = meta.term_builder(self)
        else:
            subject = BNode()

        # rdf:type assertions
        for class_uri in meta.class_uris:
            g.add((subject, RDF.type, class_uri))

        # Link from parent
        if parent is not None and predicates:
            for pred in predicates:
                g.add((parent, pred, subject))

        # Field triples
        for field_name, field_info in self.__class__.model_fields.items():
            value = getattr(self, field_name)
            if value is None:
                continue

            rdf_metas: list[RdfanticFieldInfoMetaModel] = [
                m for m in field_info.metadata
                if isinstance(m, RdfanticFieldInfoMetaModel)
            ]
            for rdf_meta in rdf_metas:
                self._emit_triples(g, context, subject, value, field_info.annotation, rdf_meta)

        return g

    # ------------------------------------------------------------------
    # Public class API
    # ------------------------------------------------------------------

    @classmethod
    def model_dump_shacl(cls) -> Graph:
        """Generate a SHACL ``NodeShape`` graph from this model's class definition.

        Returns
        -------
        rdflib.Graph
            A graph containing one ``sh:NodeShape`` targeting each URI in
            ``Meta.class_uris``, with one ``sh:PropertyShape`` per annotated
            field.
        """
        g = Graph()
        g.bind("sh", SH)
        g.bind("xsd", XSD)

        meta = cls.Meta
        if not meta.class_uris:
            return g

        first_class_uri = next(iter(meta.class_uris))
        shape_uri = URIRef(str(first_class_uri) + "Shape")

        g.add((shape_uri, RDF.type, SH.NodeShape))
        if meta.name:
            g.add((shape_uri, SH.name, Literal(f"{meta.name}Shape")))
        for class_uri in meta.class_uris:
            g.add((shape_uri, SH.targetClass, class_uri))

        for field_name, field_info in cls.model_fields.items():
            rdf_metas: list[RdfanticFieldInfoMetaModel] = [
                m for m in field_info.metadata
                if isinstance(m, RdfanticFieldInfoMetaModel)
            ]
            if not rdf_metas:
                continue

            annotation = field_info.annotation
            inner_type, is_optional, is_list = _unwrap(annotation)
            is_required = field_info.is_required() and not is_optional

            for rdf_meta in rdf_metas:
                for pred in rdf_meta.predicates:
                    prop_node = BNode()
                    g.add((shape_uri, SH.property, prop_node))
                    g.add((prop_node, SH.path, pred))
                    g.add((prop_node, SH.name, Literal(field_name)))

                    # Cardinality
                    if is_required:
                        g.add((prop_node, SH.minCount, Literal(1, datatype=XSD.integer)))
                    if not is_list:
                        g.add((prop_node, SH.maxCount, Literal(1, datatype=XSD.integer)))

                    # Value type constraint
                    cls._add_shacl_value_constraint(g, prop_node, rdf_meta, inner_type)

        return g

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _emit_triples(
        self,
        g: Graph,
        context: ShaclMaterializationContext,
        subject: URIRef | BNode,
        value: Any,
        annotation: Any,
        rdf_meta: RdfanticFieldInfoMetaModel,
    ) -> None:
        """Emit all RDF triples for one field (scalar, list, or nested model)."""
        values = value if isinstance(value, list) else [value]

        for val in values:
            if val is None:
                continue

            if isinstance(val, RdfanticBaseModel):
                # Nested model → recursive serialisation
                nested_g = val.model_dump_rdf(
                    context=context,
                    parent=subject,
                    predicates=rdf_meta.predicates,
                )
                for triple in nested_g:
                    g.add(triple)

                # Inverse properties
                if rdf_meta.inverse_predicates:
                    nested_meta = val.__class__.Meta
                    nested_subj = nested_meta.term_builder(val) if nested_meta.term_builder else BNode()
                    for inv_pred in rdf_meta.inverse_predicates:
                        g.add((nested_subj, inv_pred, subject))

            elif rdf_meta.uri_factory is not None and isinstance(val, str):
                # String → URI via factory
                obj: URIRef | BNode = rdf_meta.uri_factory(val)
                for pred in rdf_meta.predicates:
                    g.add((subject, pred, obj))
                for cls_uri in rdf_meta.field_class_uris:
                    g.add((obj, RDF.type, cls_uri))

            elif isinstance(val, URIRef):
                # Already a URIRef
                for pred in rdf_meta.predicates:
                    g.add((subject, pred, val))
                for cls_uri in rdf_meta.field_class_uris:
                    g.add((val, RDF.type, cls_uri))

            else:
                # Literal
                if rdf_meta.datatype:
                    obj_lit = Literal(val, datatype=rdf_meta.datatype)
                else:
                    inferred = _xsd_for(type(val))
                    obj_lit = Literal(val, datatype=inferred) if inferred else Literal(str(val))
                for pred in rdf_meta.predicates:
                    g.add((subject, pred, obj_lit))

    @classmethod
    def _add_shacl_value_constraint(
        cls,
        g: Graph,
        prop_node: BNode,
        rdf_meta: RdfanticFieldInfoMetaModel,
        inner_type: Any,
    ) -> None:
        """Add the appropriate SHACL value-type constraint to a property shape node."""
        if rdf_meta.datatype:
            g.add((prop_node, SH.datatype, rdf_meta.datatype))
        elif rdf_meta.uri_factory is not None:
            g.add((prop_node, SH.nodeKind, SH.IRI))
            for cls_uri in rdf_meta.field_class_uris:
                g.add((prop_node, SH["class"], cls_uri))
        elif rdf_meta.field_class_uris:
            for cls_uri in rdf_meta.field_class_uris:
                g.add((prop_node, SH["class"], cls_uri))
        elif isinstance(inner_type, type) and issubclass(inner_type, RdfanticBaseModel):
            for cls_uri in inner_type.Meta.class_uris:
                g.add((prop_node, SH["class"], cls_uri))
        elif isinstance(inner_type, type):
            inferred = _xsd_for(inner_type)
            if inferred:
                g.add((prop_node, SH.datatype, inferred))
