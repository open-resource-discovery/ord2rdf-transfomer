# Contributing to ORD RDF Transformer

Thank you for your interest in contributing to **ord-to-rdf-transformer** — a tool that converts [Open Resource Discovery (ORD)](https://open-resource-discovery.org/) JSON documents into RDF knowledge graphs and validates them with SHACL shapes.

This document covers everything you need to get from a fresh clone to a merged pull request.

---

## Table of Contents

1. [General Remarks](#general-remarks)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Running Tests](#running-tests)
5. [Code Style](#code-style)
6. [Project Structure](#project-structure)
7. [How to Contribute](#how-to-contribute)
   - [Reporting Bugs](#reporting-bugs)
   - [Suggesting Features](#suggesting-features)
   - [Submitting a Pull Request](#submitting-a-pull-request)
8. [Adding a New ORD Model](#adding-a-new-ord-model)
9. [Commit Message Guidelines](#commit-message-guidelines)
10. [Developer Certificate of Origin (DCO)](#developer-certificate-of-origin-dco)

---

## General Remarks

You are welcome to contribute content (code, documentation, etc.) to this open source project.

There are some important things to know:

1. You must **comply with the license of this project** and **accept the Developer Certificate of Origin** (see [below](#developer-certificate-of-origin-dco)) before being able to contribute. The acknowledgement to the DCO will usually be requested from you as part of your first pull request to this project.

2. Please **adhere to our [Code of Conduct](CODE_OF_CONDUCT.md)**.

3. If you plan to use **generative AI tools** to create contributions, please read the [Guideline for AI-generated code contributions](CONTRIBUTING_USING_GENAI.md) first.

4. Not all proposed contributions can be accepted. Some features may, for example, not fit the overall project direction or technical constraints. It is therefore recommended that you first align with the maintainers — open an issue to discuss your idea before investing significant effort.

---

## Getting Started

**Prerequisites**

- Python 3.11 or 3.12
- `git`
- A virtual environment manager of your choice (`venv`, `conda`, etc.)

**Clone the repository**

```bash
git clone https://github.com/open-resource-discovery/ord2rdf-transfomer.git
cd ord2rdf-transfomer
```

---

## Development Setup

Create and activate a virtual environment, then install the package together with all development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

This installs:
- **Runtime:** `rdflib`, `pyshacl`, `pydantic`, `click`
- **Dev tools:** `pytest`, `pytest-cov`, `ruff`, `mypy`
- The `ord-transform` CLI entry point in editable mode

Verify the installation:

```bash
ord-transform --help
pytest --tb=short
```

---

## Running Tests

The full test suite runs with:

```bash
pytest
```

To include coverage reporting:

```bash
pytest --cov=src --cov-report=term-missing
```

Tests are organised by module under `tests/`:

| File | What it tests |
|---|---|
| `test_rdfantic.py` | RDFantic framework (context, RDF serialisation, SHACL shape generation) |
| `test_models.py` | ORD Pydantic models (instantiation, alias handling, RDF output) |
| `test_transformer.py` | `ORDTransformer` (JSON → RDF graph, error handling) |
| `test_shacl_generator.py` | SHACL shape generation (model-based and vocabulary-based) |
| `test_validator.py` | `SHACLValidator` (conformant/non-conformant data, file-based validation) |

All tests must pass before a pull request can be merged. The CI pipeline enforces this on Python 3.11 and 3.12.

---

## Code Style

This project uses **Ruff** for linting and formatting, and **Mypy** for type checking.

**Lint and format:**

```bash
ruff check src/ tests/          # lint
ruff format src/ tests/         # auto-format
```

**Type check:**

```bash
mypy src/
```

Key style rules (from `pyproject.toml`):

- Line length: **100 characters**
- Target Python version: **3.11**
- Active rule sets: `E`, `F`, `I` (isort), `UP` (pyupgrade), `B` (flake8-bugbear)

The CI pipeline runs both `ruff check` and `ruff format --check` on every pull request. Format failures will block merging.

---

## Project Structure

```
ord2rdf-transfomer/
├── src/
│   ├── rdfantic/               # Standalone RDFantic framework
│   │   ├── base_model.py       # RdfanticBaseModel — model_dump_rdf / model_dump_shacl
│   │   ├── context.py          # ShaclMaterializationContext
│   │   ├── field_info.py       # RdfanticFieldInfoMetaModel
│   │   └── metadata.py         # RdfanticModelMetadata (inner Meta config)
│   └── ord_transformer/        # ORD-specific application
│       ├── models/             # One file per ORD entity type
│       ├── namespaces.py       # ORD RDF namespace + URI helpers
│       ├── transformer.py      # JSON → rdflib.Graph pipeline
│       ├── shacl_generator.py  # Model-based + vocab-based SHACL generation
│       ├── validator.py        # pyshacl wrapper
│       ├── exceptions.py       # Custom exception hierarchy
│       └── cli.py              # click CLI (transform / generate-shapes / validate)
├── tests/                      # pytest test suite
├── data/
│   ├── vocab/                  # Authoritative ORD RDF vocabulary
│   ├── shapes/                 # SHACL shape files
│   └── samples/                # Example ORD JSON documents
├── scripts/
│   └── run_pipeline.py         # End-to-end demo: transform → validate
├── output/                     # Generated RDF + reports (git-ignored)
├── .github/workflows/ci.yml    # CI pipeline (lint → test → build)
├── pyproject.toml
├── LICENSE
├── CONTRIBUTING.md             # This file
└── CODE_OF_CONDUCT.md
```

---

## How to Contribute

### Reporting Bugs

Before opening a bug report, please search existing issues to avoid duplicates.

When filing a bug, include:
- A clear, descriptive title
- Steps to reproduce the problem
- The ORD JSON input (or a minimal excerpt) that triggers the issue
- The actual output or error message
- The expected output
- Your Python version and OS

### Suggesting Features

Open an issue with the label `enhancement` and describe:
- The problem you are trying to solve
- Your proposed solution or API
- Any ORD spec references that are relevant (link to the ORD specification section if applicable)

### Submitting a Pull Request

1. Make sure the change is welcome (see [General Remarks](#general-remarks)).

2. **Fork** the repository and create a feature branch from `main`:

   ```bash
   git checkout -b feat/your-feature-name
   ```

3. **Make your changes.** Keep commits focused — one logical change per commit.

4. **Add or update tests** to cover your changes. The test suite must remain green on both Python 3.11 and 3.12.

5. **Run the full check locally** before pushing:

   ```bash
   ruff check src/ tests/
   ruff format src/ tests/
   mypy src/
   pytest
   ```

6. **Push your branch** and open a pull request against `main`.

7. **Fill in the PR description** — what changed, why, and how to test it.

8. Follow the link posted by the DCO assistant to your pull request and accept it, as described in the [Developer Certificate of Origin](#developer-certificate-of-origin-dco) section.

9. Wait for our code review and approval — we may ask you to make additional changes based on feedback.

10. Once the change has been approved and merged, we will inform you in a comment. 🎉

---

## Adding a New ORD Model

When the ORD specification adds a new entity type, follow these steps:

1. **Create the model file** in `src/ord_transformer/models/`:

   ```python
   # src/ord_transformer/models/my_entity.py
   from rdfantic import RdfanticBaseModel, RdfanticModelMetadata, RdfanticFieldInfoMetaModel
   from pydantic import Field
   from ..namespaces import ORD

   class MyEntity(RdfanticBaseModel):
       class Meta(RdfanticModelMetadata):
           name = "MyEntity"
           class_uris = [ORD.MyEntity]

       ord_id: str = Field(..., alias="ordId",
           json_schema_extra={"rdf": RdfanticFieldInfoMetaModel(predicate=ORD.ordId)})
       # … additional fields
   ```

2. **Register the model** in `src/ord_transformer/models/__init__.py` by adding it to `ALL_MODELS` and mapping the JSON key in `transformer.py`.

3. **Add sample data** under `data/samples/` that exercises the new entity type.

4. **Write tests** in `tests/test_models.py` and `tests/test_transformer.py` covering at minimum:
   - Model instantiation with a valid payload
   - `model_dump_rdf()` returns the expected RDF type triple
   - The transformer produces the correct number of type triples for the new entity

5. **Update the README** model table.

---

## Commit Message Guidelines

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short summary>
```

Common types:

| Type | When to use |
|---|---|
| `feat` | A new feature or model |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `test` | Adding or updating tests |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `chore` | Build process, dependency updates, CI changes |

Examples:

```
feat(models): add Agent model for ORD spec v1.14 beta
fix(validator): handle empty graphs without raising AttributeError
docs(readme): correct CLI usage example for generate-shapes
chore(ci): pin actions/setup-python to v5
```

---

## Developer Certificate of Origin (DCO)

Due to legal reasons, contributors will be asked to accept a DCO before they submit the first pull request to this project. This project uses the [standard DCO text of the Linux Foundation](https://developercertificate.org/):

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.

Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off)
    is maintained indefinitely and may be redistributed consistent
    with this project or the open source license(s) involved.
```
