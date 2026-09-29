"""Pytest configuration for rdfantic tests."""

from pathlib import Path

RESOURCES_DIR = Path(__file__).parent / "resources"

SHACL_SHACL_PATH = RESOURCES_DIR / "shacl-shacl.ttl"
