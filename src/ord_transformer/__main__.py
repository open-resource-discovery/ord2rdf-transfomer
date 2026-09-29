"""Allow the CLI to be invoked as ``python -m ord_transformer``.

Requires either a formal ``pip install -e .`` OR that ``src/`` is on
PYTHONPATH.

Zero-install alternatives
--------------------------
- **CLI launcher** (mirrors the installed ``ord-transform`` command)::

      python ord_transform.py --help

- **End-to-end pipeline script** (transform → validate in one step)::

      python scripts/run_pipeline.py
      python scripts/run_pipeline.py --force-shapes   # also regenerate SHACL shapes

With installation (or PYTHONPATH set)::

    # PowerShell / CMD — set PYTHONPATH once per session if not installed:
    $env:PYTHONPATH = "src"          # PowerShell
    set PYTHONPATH=src               # CMD

    python -m ord_transformer --help
    python -m ord_transformer transform data/samples/sample_ord.json output/ord_data.ttl
    python -m ord_transformer generate-shapes --vocab data/vocab/ord_vocabulary.ttl --output output/shapes.ttl
    python -m ord_transformer validate output/ord_data.ttl output/shapes.ttl
"""

from ord_transformer.cli import cli

if __name__ == "__main__":
    cli()
