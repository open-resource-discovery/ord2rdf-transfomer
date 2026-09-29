"""Shared pytest fixtures for the ORD RDF Transformer test suite."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make src/ importable without installation
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


# ── Paths ──────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def vocab_path(project_root: Path) -> Path:
    """Path to the ORD vocabulary TTL file."""
    p = project_root / "ord_open_vocab.ttl"
    if not p.exists():
        pytest.skip(f"Vocabulary file not found: {p}")
    return p


@pytest.fixture(scope="session")
def sample_ord_path(project_root: Path) -> Path:
    """Path to the sample ORD JSON document."""
    return project_root / "data" / "samples" / "sample_ord.json"


# ── Data ───────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def sample_ord_doc(sample_ord_path: Path) -> dict:
    """The sample ORD JSON document loaded as a Python dict."""
    with sample_ord_path.open(encoding="utf-8") as fh:
        return json.load(fh)


# ── RDFantic context ───────────────────────────────────────────────────────────

@pytest.fixture
def context():
    """A ShaclMaterializationContext using the standard ORD instance base URI."""
    from rdfantic import ShaclMaterializationContext

    return ShaclMaterializationContext("https://open-resource-discovery.org/instance/")


# ── Transformer ────────────────────────────────────────────────────────────────

@pytest.fixture
def transformer():
    """A default ORDTransformer instance."""
    from ord_transformer.transformer import ORDTransformer

    return ORDTransformer()


# ── Pre-built graphs ───────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def transformed_graph(sample_ord_doc):
    """The sample ORD document transformed to an rdflib.Graph (session-scoped)."""
    from ord_transformer.transformer import ORDTransformer

    return ORDTransformer().transform(sample_ord_doc)


@pytest.fixture(scope="session")
def model_shapes_graph():
    """SHACL shapes generated from ORD models (session-scoped)."""
    from ord_transformer.shacl_generator import _generate_model_shapes

    return _generate_model_shapes()


@pytest.fixture(scope="session")
def vocab_shapes_graph(vocab_path):
    """SHACL shapes generated from the vocabulary TTL (session-scoped)."""
    from ord_transformer.shacl_generator import _generate_vocab_shapes

    return _generate_vocab_shapes(vocab_path)
