#!/usr/bin/env python
"""Zero-install CLI launcher.

Run this script directly when you have NOT yet done ``pip install -e .``::

    python ord_transform.py --help
    python ord_transform.py transform data/samples/sample_ord.json output/ord_data.ttl
    python ord_transform.py generate-shapes --vocab ord_vocab.ttl --output output/shapes.ttl
    python ord_transform.py validate output/ord_data.ttl output/shapes.ttl

After ``pip install -e .`` the registered console-script ``ord-transform`` will
also be available.
"""
from __future__ import annotations

import sys
from pathlib import Path


_src = Path(__file__).resolve().parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from ord_transformer.cli import cli

if __name__ == "__main__":
    cli(prog_name="ord-transform")
