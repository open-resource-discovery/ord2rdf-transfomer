# ORD RDF Transformer

[Open Resource Discovery (ORD)](https://open-resource-discovery.org/) is an open specification for describing the resources and capabilities that software systems expose — such as APIs, events, data products, capabilities, and integration dependencies — along with their business context (vendors, products, packages, industries, lines of business) and lifecycle metadata (versioning, release status, visibility). In short, ORD lets a system self-describe what it offers in a standardized, machine-readable way, making automated discovery and integration across a distributed landscape possible.

This repository provides the tooling and semantic assets to bring ORD JSON documents into the RDF / Knowledge Graph :

- ORD → RDF Transformation — converts ORD documents into normalized RDF graphs.
- ORD Vocabulary — the RDF vocabulary representing ORD concepts, resources, taxonomies, and relationships.
- SHACL Shapes — executable validation constraints that verify the generated RDF conforms to the ORD specification.
- Together, these components let you take raw ORD metadata, express it as a knowledge graph, and prove that the result is valid and specification-compliant.

```
  ┌──────────────────┐
  │  ORD JSON        │   your system's ORD document
  └────────┬─────────┘
           │
           │  Step 1 — Transform
           │  Pydantic models + RDFantic serialize every
           │  resource, package, vendor, … to RDF triples
           ▼
  ┌──────────────────┐
  │  RDF graph       │   Turtle (default), n-3, nt, json-ld, xml  
  │                  │   
  └────────┬─────────┘
           │
           │  Step 2 — Validate
           │  pyshacl checks the graph against
           │  SHACL shapes + the ORD vocabulary
           ▼
  ┌──────────────────┐
  │  Validation      │   violations flagged by severity;
  │  report          │   
  └──────────────────┘
```

## Requirements

- [Python](https://www.python.org/) 3.11+
- [rdflib](https://rdflib.readthedocs.io/) ≥ 7.6.0
- [pyshacl](https://github.com/RDFLib/pySHACL) ≥ 0.40.1
- [pydantic](https://docs.pydantic.dev/) ≥ 2.13.4
- [click](https://click.palletsprojects.com/) ≥ 8.0.0

### Installation

```bash
git clone https://github.com/open-resource-discovery/ord2rdf-transfomer.git
cd ord2rdf-transfomer
pip install .
```

After installation you can run it using following commands:

```bash
# Transform an ORD JSON document to Turtle RDF
ord-transform transform data/samples/sample_ord.json output/ord_data.ttl

# Generate SHACL shapes from models + vocabulary
ord-transform generate-shapes \
    --vocab data/vocab/ord_vocabulary.ttl \
    --output output/ord_shapes.ttl

# Validate an RDF file against a shapes file
ord-transform validate output/ord_data.ttl data/shapes/ord_shapes.ttl
```

### Run it without installation

`scripts/run_pipeline.py` is a convenience script that runs transform → validate
for a single input file and writes every output to `output/`. It is not part of
the installed package — it is a local script you run from the project root.

```bash
# Run on the bundled comprehensive example (default input)
python scripts/run_pipeline.py

# Run on your own ORD document
python scripts/run_pipeline.py path/to/my_ord_document.json

# Force shapes regeneration even if the shapes file is already up-to-date
python scripts/run_pipeline.py --force-shapes
```

Outputs written to `output/`:
| File | Contents |
|---|---|
| `<stem>.ttl` | The transformed RDF graph (Turtle) |
| `<stem>_validation_report.ttl` | SHACL validation report |
### example code

The fastest way to see what the tool produces:

```python
from ord_transformer.transformer import ORDTransformer
from ord_transformer.validator import SHACLValidator

# 1. Load and transform an ORD JSON document into an RDF graph
transformer = ORDTransformer()
graph = transformer.transform_file("data/samples/sample_ord.json")

# 2. Inspect: print the first 20 triples as Turtle
print(graph.serialize(format="turtle")[:800])

# 3. Validate against the hand-authored SHACL shapes
validator = SHACLValidator(
    ont_path="data/vocab/ord_vocabulary.ttl"  # vocab merged for concept resolution
)
result = validator.validate_files(
    "output/ord_data.ttl",
    "data/shapes/ord_shapes.ttl",
)
print(result)          # e.g. ValidationResult(CONFORMS)
print(result.violation_count)  # 0 if all constraints pass
```

**What you get back** — for each API resource in the JSON you get triples like:

```turtle
<https://open-resource-discovery.org/instance/sap.foo/apiResource/astronomy/v1>
    a ord:APIResource ;
    ord:ordId        "sap.foo:apiResource:astronomy:v1" ;
    ord:title        "Astronomy API" ;
    ord:releaseStatus ord:ReleaseStatus-active ;
    ord:visibility   ord:Visibility-public ;
    ord:partOfPackage <.../sap.foo/package/AstronomyPackage/v1> ;
    ord:resourceDefinition
        <https://my-system.example.com/ord/metadata/astronomy-v1.oas3.json> .
```


---

## Support, Feedback, Contributing

This project is open to feature requests/suggestions, bug reports etc. via [GitHub issues](https://github.com/open-resource-discovery/ord2rdf-transfomer/issues). Contribution and feedback are encouraged and always welcome. For more information about how to contribute, the project structure, as well as additional contribution information, see our [Contribution Guidelines](CONTRIBUTING.md).

## Security / Disclosure
If you find any bug that may be a security problem, please follow our instructions at [in our security policy](https://github.com/open-resource-discovery/ord2rdf-transfomer/security/policy) on how to report it. Please do not create GitHub issues for security-related doubts or problems.

## Code of Conduct

We as members, contributors, and leaders pledge to make participation in our community a harassment-free experience for everyone. By participating in this project, you agree to abide by its [Code of Conduct](CODE_OF_CONDUCT.md) at all times.

## Licensing

Copyright 2026 SAP SE or an SAP affiliate company and ord2rdf-transfomer contributors. Please see our [LICENSE](LICENSE) for copyright and license information. Detailed information including third-party components and their licensing/copyright information is available [via the REUSE tool](https://api.reuse.software/info/github.com/open-resource-discovery/ord2rdf-transfomer).


