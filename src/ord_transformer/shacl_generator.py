"""SHACL shape generator for the ORD vocabulary.

Public API
----------
:func:`generate_combined_shapes`
    The single entry point for callers.  Merges model-derived shapes with
    vocabulary-derived shapes into one graph.  Pass *vocab_path* to include
    shapes from ``ord_open_vocab.ttl``; omit it to get model shapes only.

Internal helpers (not part of the public API)
---------------------------------------------
:func:`_generate_model_shapes`
    Calls ``model_dump_shacl()`` on every RDFantic ORD model class.
    Shapes are derived from Pydantic field annotations (types, optionality,
    cardinality) and ``RdfanticFieldInfoMetaModel`` metadata.

:func:`_generate_vocab_shapes`
    Parses ``ord_open_vocab.ttl`` and converts ``rdfs:Class`` definitions
    together with their ``rdfs:domain`` / ``rdfs:range`` property constraints
    directly into SHACL NodeShape + PropertyShape triples.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, SH, URIRef, XSD
from rdflib.collection import Collection
from rdflib.namespace import SKOS

from .exceptions import SHACLGenerationError, VocabularyNotFoundError
from .models import ALL_MODELS
from .models.supporting import ChangelogEntry, ConsumptionBundleReference, Link, ResourceDefinition
from .namespaces import ORD, bind_standard_namespaces

_EMBEDDED_MODELS = [ResourceDefinition, Link, ChangelogEntry, ConsumptionBundleReference]

# XSD range URIs that should become sh:datatype (not sh:class)
_XSD_STR = str(XSD)
_SKOS_STR = str(SKOS)

# Ranges that map to sh:nodeKind sh:IRI instead of a datatype.
# Intentionally empty: both RDFS.Resource and XSD.anyURI cause false positives.
# • RDFS.Resource fires for properties that point to blank nodes (e.g. extensible,
#   resourceDefinition, describedSystemType) — blank nodes fail sh:nodeKind sh:IRI.
# • XSD.anyURI fires for relative-URL strings stored as xsd:string literals.
# Vocab shapes are structural only (sh:name, sh:description, sh:path, SKOS sh:or);
# the model-based shapes handle nodeKind / datatype constraints where needed.
_URI_RANGES: set = set()

# Properties whose xsd:string range is relaxed to also accept IRI node kind.
# Reason: these props are stored as URI references in reference-wrapper blank
# nodes (e.g. ConsumptionBundleReference) even though the vocabulary declares
# rdfs:range xsd:string.
_STRING_OR_IRI_PROPS = {ORD.ordId}


# ── Model-based SHACL generation (internal) ──────────────────────────────────

def _generate_model_shapes() -> Graph:
    """Generate SHACL shapes from all RDFantic ORD model classes.

    Internal helper — use :func:`generate_combined_shapes` instead.

    Iterates over :data:`~ord_transformer.models.ALL_MODELS` (plus the
    embedded supporting types) and merges their ``model_dump_shacl()``
    outputs into a single graph.

    Returns
    -------
    rdflib.Graph
        A graph containing one ``sh:NodeShape`` per model class.
    """
    g = Graph()
    bind_standard_namespaces(g)
    g.bind("sh", SH)

    for model_cls in ALL_MODELS + _EMBEDDED_MODELS:
        try:
            shape_graph = model_cls.model_dump_shacl()
            g += shape_graph
        except Exception as exc:
            raise SHACLGenerationError(
                f"Failed to generate SHACL for model {model_cls.__name__}: {exc}"
            ) from exc

    return g


# ── Shared helpers ────────────────────────────────────────────────────────────

def _emit_str_or_iri(g: Graph, prop_shape: BNode) -> None:
    """Add ``sh:or ( [ sh:datatype xsd:string ] [ sh:nodeKind sh:IRI ] )`` to *prop_shape*.

    Used for properties where the vocabulary declares ``rdfs:range xsd:string``
    but the transformer may also store URI references (e.g. ``ord:ordId`` on
    reference-wrapper blank nodes), and for SKOS concept ranges where ORD JSON
    uses plain strings while full RDF would use IRIs.
    """
    or_list = BNode()
    str_shape = BNode()
    iri_shape = BNode()
    Collection(g, or_list, [str_shape, iri_shape])
    g.add((prop_shape, SH["or"], or_list))
    g.add((str_shape, SH.datatype, XSD.string))
    g.add((iri_shape, SH.nodeKind, SH.IRI))


# ── Vocabulary-based SHACL generation (internal) ─────────────────────────────

def _generate_vocab_shapes(vocab_path: Path) -> Graph:
    """Generate SHACL shapes directly from the ORD vocabulary TTL file.

    Internal helper — use :func:`generate_combined_shapes` instead.

    Reads ``ord_open_vocab.ttl``, iterates over every ``rdfs:Class`` in the
    ``ord:`` namespace, and creates:

    - One ``sh:NodeShape`` per class (``sh:targetClass``)
    - One ``sh:PropertyShape`` per ``rdf:Property`` whose ``rdfs:domain``
      matches that class, with ``sh:path``, ``sh:name``, and — where
      determinable — ``sh:datatype``, ``sh:class``, or ``sh:nodeKind``
      derived from ``rdfs:range``.

    Parameters
    ----------
    vocab_path:
        Filesystem path to ``ord_open_vocab.ttl``.

    Returns
    -------
    rdflib.Graph

    Raises
    ------
    VocabularyNotFoundError
        If *vocab_path* does not exist.
    SHACLGenerationError
        If the vocabulary cannot be parsed.
    """
    vocab_path = Path(vocab_path)
    if not vocab_path.exists():
        raise VocabularyNotFoundError(f"Vocabulary file not found: {vocab_path}")

    vocab: Graph = Graph()
    try:
        vocab.parse(vocab_path.as_uri(), format="turtle")
    except Exception as exc:
        raise SHACLGenerationError(f"Failed to parse vocabulary {vocab_path}: {exc}") from exc

    g = Graph()
    bind_standard_namespaces(g)
    g.bind("sh", SH)

    ord_ns_str = str(ORD)

    # ── Build a map: class_uri → list of property URIs with that domain ───────
    domain_map: dict[URIRef, list[URIRef]] = {}
    for prop_uri in vocab.subjects(RDF.type, RDF.Property):
        for domain_uri in vocab.objects(prop_uri, RDFS.domain):
            if isinstance(domain_uri, URIRef):
                domain_map.setdefault(domain_uri, []).append(prop_uri)

    # Some properties carry a superclass (e.g. ord:ORDEntity) as domain — we
    # want to inherit those shapes onto subclasses too.
    subclass_map: dict[URIRef, list[URIRef]] = {}
    for child, _, parent in vocab.triples((None, RDFS.subClassOf, None)):
        if isinstance(child, URIRef) and isinstance(parent, URIRef):
            subclass_map.setdefault(child, []).append(parent)

    def _inherited_props(cls_uri: URIRef) -> list[URIRef]:
        """Return all property URIs whose domain is cls_uri or an ancestor."""
        result = list(domain_map.get(cls_uri, []))
        for parent in subclass_map.get(cls_uri, []):
            result += _inherited_props(parent)
        return result

    # ── Emit one NodeShape per ord: class ─────────────────────────────────────
    for class_uri in vocab.subjects(RDF.type, RDFS.Class):
        if not isinstance(class_uri, URIRef):
            continue
        if not str(class_uri).startswith(ord_ns_str):
            continue

        shape_uri = URIRef(str(class_uri) + "Shape")
        g.add((shape_uri, RDF.type, SH.NodeShape))
        g.add((shape_uri, SH.targetClass, class_uri))

        # sh:name from rdfs:label
        for label in vocab.objects(class_uri, RDFS.label):
            g.add((shape_uri, SH.name, Literal(str(label))))
            break

        # description from rdfs:comment
        for comment in vocab.objects(class_uri, RDFS.comment):
            g.add((shape_uri, SH.description, Literal(str(comment))))
            break

        # ── One PropertyShape per inherited property ──────────────────────────
        seen_props: set[URIRef] = set()
        for prop_uri in _inherited_props(class_uri):
            if prop_uri in seen_props:
                continue
            seen_props.add(prop_uri)

            prop_shape = BNode()
            g.add((shape_uri, SH.property, prop_shape))
            g.add((prop_shape, SH.path, prop_uri))

            # sh:name from property rdfs:label
            for label in vocab.objects(prop_uri, RDFS.label):
                g.add((prop_shape, SH.name, Literal(str(label))))
                break

            # sh:description from property rdfs:comment
            for comment in vocab.objects(prop_uri, RDFS.comment):
                g.add((prop_shape, SH.description, Literal(str(comment)[:500])))
                break

            # Constraint from rdfs:range
            for range_uri in vocab.objects(prop_uri, RDFS.range):
                if not isinstance(range_uri, URIRef):
                    continue
                range_str = str(range_uri)

                if range_uri in _URI_RANGES:
                    # Generic resource / anyURI — constrain to IRI node kind
                    g.add((prop_shape, SH.nodeKind, SH.IRI))

                elif range_str.startswith(_XSD_STR):
                    if prop_uri in _STRING_OR_IRI_PROPS:
                        # Property stores either a string literal (normal) or
                        # a URI (reference-wrapper pattern). Accept both.
                        _emit_str_or_iri(g, prop_shape)
                    elif range_uri == XSD.anyURI:
                        # anyURI can arrive as a typed xsd:anyURI literal OR as
                        # a plain xsd:string (relative URL). Skip the datatype
                        # constraint to avoid false positives.
                        pass
                    else:
                        # Standard XSD datatype literal
                        g.add((prop_shape, SH.datatype, range_uri))

                elif range_str.startswith(_SKOS_STR):
                    # SKOS:Concept — ORD JSON serialises these as plain strings;
                    # full RDF representation uses IRIs. Accept both.
                    _emit_str_or_iri(g, prop_shape)

                elif range_str.startswith(ord_ns_str):
                    # Another ORD class — skip ALL type/nodeKind constraints.
                    # • sh:class causes false violations when cross-document refs
                    #   lack an rdf:type assertion in the current graph.
                    # • sh:nodeKind sh:IRI causes false violations for embedded
                    #   blank-node objects (Extensible, ResourceDefinition, etc.).
                    # The blank-node shapes are validated by their own NodeShapes.
                    pass  # no range constraint

                # else: skip unknown range (e.g. foaf:Agent)
                break  # only process first range declaration

    return g


# ── Combined generation ───────────────────────────────────────────────────────

def generate_combined_shapes(vocab_path: Optional[Path] = None) -> Graph:
    """Generate a unified SHACL graph from both models and vocabulary.

    Model shapes are always generated.  Vocabulary shapes are merged in only
    when *vocab_path* is supplied and the file exists.

    Parameters
    ----------
    vocab_path:
        Optional path to ``ord_open_vocab.ttl``.  Pass ``None`` to skip
        vocabulary-based shape generation.

    Returns
    -------
    rdflib.Graph
    """
    g = _generate_model_shapes()

    if vocab_path is not None:
        vocab_path = Path(vocab_path)
        if vocab_path.exists():
            vocab_g = _generate_vocab_shapes(vocab_path)
            g += vocab_g

    return g
