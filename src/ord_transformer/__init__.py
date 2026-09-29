"""ORD RDF Transformer — convert ORD JSON documents to RDF and validate with SHACL.

Quick usage::

    from ord_transformer.transformer import ORDTransformer
    from ord_transformer.shacl_generator import generate_combined_shapes
    from ord_transformer.validator import SHACLValidator

    transformer = ORDTransformer()
    rdf_graph = transformer.transform_file("data/samples/sample_ord.json")
    rdf_graph.serialize("output/ord_data.ttl", format="turtle")

    shapes = generate_combined_shapes(vocab_path=Path("data/vocab/ord_open_vocab.ttl"))
    shapes.serialize("data/shapes/ord_shapes.ttl", format="turtle")

    validator = SHACLValidator()
    result = validator.validate(rdf_graph, shapes)
    print("Conforms:", result.conforms)
"""

__version__ = "0.1.0"
