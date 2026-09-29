# Developing and contributing along with RDFantic

This guide explains how to build and develop within the RDFantic library project, using [uv](https://docs.astral.sh/uv/).

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) installed
- Project dependencies installed: `uv sync` (it installs dev and test dependencies by default)

## Package Configuration

The package is configured in `pyproject.toml` with:

- **Package name**: `bkg-rdfantic`
- **Version**: `x.y.z` (update in `pyproject.toml` before publishing)
- **Source layout**: `src/rdfantic/` (using src layout for better isolation)
- **Build backend**: [`hatchling`](https://hatch.pypa.io/latest/)

## Building and Testing locally

### Building the package

```bash
uv build \
    [--wheel] \
    [--sdist] \
    [--out-dir <OUTDIR_PATH=dist>] \
    [--clear]
```

The options above are all optional, with defaults indicated if existing.
- `--wheel` will create the wheel distribution (e.g. `bkg_rdfantic-x.y.z-py3-none-any.whl`).
  It will be created even if not provided if `--sdist` not provided either.
- `--sdist` will create the source distribution (e.g. `bkg_rdfantic-x.y.z.tar.gz`).
  It will be created even if not provided if `--wheel` not provided either.
- `--out-dir` is the output directory for the distribution mentioned above. `dist` by default.
- `--clear` will remove stale artifacts and allow you to get a clean build.

#### Testing the package

Install the built package in a virtual environment:

```bash
# Using pip
pip install dist/bkg_rdfantic-x.y.z-py3-none-any.whl

# Or from the source distribution
pip install dist/bkg_rdfantic-x.y.z.tar.gz
```

### Test the installation:

```python
from rdfantic import RdfanticBaseModel, RdfanticModelMetadata
print("Import successful!")
```

## Anatomy of the built package



## Distribution Files

The built package includes:

- **All source files** from `src/rdfantic/`
- **LICENSE** file
- **README.md**
- **Metadata** (dependencies, version, etc.)

Tests, documentation source files, and development tools are excluded from the distribution.

## Package Structure in Distribution

When installed, the package structure is:

```
site-packages/
└── rdfantic/
    ├── __init__.py
    ├── context/
    ├── exceptions.py
    ├── internal/
    ├── models/
    ├── serialization/
    ├── shacl/
    └── utils.py
```

Users can import with:

```python
from rdfantic import RdfanticBaseModel, ShaclMaterializationContext
```

## Package development lifecycle

The package is developed under a series of CICD and security checks.

In order to put a fix or a feature change as candidate, open a PR against the `main` branch, get the checks green (see below) and get it reviewed by code owners.

The CICD pipeline will take care of building the package productively.

### CICD checks

The CICD pipeline(s) bring the following checks against development PRs :
- The Piper General Purpose Pipeline (GPP) takes care of building the package (at the very minimum) and this repository includes the unit tests within it through GPP extensibility mechanism.
- Some quicker code quality checks (i.e linter, formatter) are run before the Piper GPP to discard
unprepared PRs quicker.
- Static code scans (SAST Scans) and Code Quality Scans (Sonar) are also part of the CICD through dedicated workflows.

### Versioning and publication

TBD.

Temporary notes:
- This will be taken care of in the future when release mechanisms will be setup.
- No manual publication should be done by developers.
- versioning will be done through release processes.
