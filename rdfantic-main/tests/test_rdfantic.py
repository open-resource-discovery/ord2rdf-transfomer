import json

import pytest
from pyshacl import validate
from rdflib import RDF, RDFS, XSD, Graph, URIRef

from rdfantic import MaterializationContext, PathElement, RdfanticSerializationError, ShaclMaterializationContext
from rdfantic.utils import join_uri
from tests.conftest import RESOURCES_DIR, SHACL_SHACL_PATH
from tests.resources.rdfantic_test_model import Company, Person


class SimpleTestContext(MaterializationContext):
    """Simple test context for RDF materialization."""

    def resolve_term(self, term: str) -> URIRef | str:
        """Pass through string terms as-is."""
        return term

    def create_uri(self, path: list[PathElement], identifier: str, element_type: str | None = None) -> URIRef:
        """Create a simple URI from the identifier."""
        _path = []
        for element in path:
            _path.extend([element.element_type, element.identifier])
        _path.extend([element_type, identifier])
        return join_uri("http://example.org/", _path)


class TestRDFantic:
    @pytest.fixture(scope="class")
    def test_context(self) -> SimpleTestContext:
        """Create a test context for RDF materialization."""
        return SimpleTestContext()

    @pytest.fixture(scope="class")
    def persons(self) -> list[Person]:
        # Load test data
        test_data_path = RESOURCES_DIR / "test_persons.json"
        with open(test_data_path) as f:
            persons_data = json.load(f)

        # Parse into Pydantic models
        return [Person(**person_data) for person_data in persons_data]

    @pytest.fixture(scope="class")
    def companies(self) -> list[Company]:
        # Load test data
        test_data_path = RESOURCES_DIR / "test_companies.json"
        with open(test_data_path) as f:
            companies_data = json.load(f)

        # Parse into Pydantic models
        return [Company(**company_data) for company_data in companies_data]

    @pytest.fixture(scope="class")
    def shacl_context(self) -> ShaclMaterializationContext:
        return ShaclMaterializationContext("http://example.org/shacl/")

    @pytest.fixture(scope="class")
    def shacl_graph(self, shacl_context: ShaclMaterializationContext) -> Graph:
        return Person.model_dump_shacl(shacl_context)

    def test_person_from_json_to_rdf(self, persons: list[Person], test_context: SimpleTestContext) -> None:
        """Test that Person models can be loaded from JSON and dumped as RDF."""
        # Verify we got the expected number of persons
        assert len(persons) == 3
        assert persons[0].name == "Alice"
        assert persons[1].name == "Bob"
        assert persons[2].name == "Charlie"

        # Dump each person to RDF
        full_graph = Graph()
        for person in persons:
            graph = person.model_dump_rdf(context=test_context, parent=None, predicates=set())

            # Verify the graph contains expected triples
            person_uri = URIRef(f"http://example.org/Person/{person.name}")

            # Check class assertion
            assert (person_uri, RDF.type, URIRef("http://example.org/Person")) in graph

            # Check name (rdfs:label) and name
            assert (person_uri, RDFS.label, None) in graph
            assert (person_uri, URIRef("http://example.org/Person/name"), None) in graph

            for _, _, other_person in graph.triples((person_uri, URIRef("http://example.org/Person/knows"), None)):
                assert isinstance(other_person, URIRef)

            # Check age
            assert (person_uri, URIRef("http://example.org/Person/age"), None) in graph

            # Check father
            assert (None, URIRef("http://example.org/Person/isFatherOf"), person_uri) in graph

            # Check jobs
            assert (person_uri, URIRef("http://example.org/Person/job"), None) in graph

            # Check optional baptized value
            assert (person.baptized is not None) == (
                (person_uri, URIRef("http://example.org/Person/baptized"), None) in graph
            )

            full_graph += graph

        # Test specific person (Alice) in detail
        alice = persons[0]
        alice_graph = alice.model_dump_rdf(context=test_context, parent=None, predicates=set())

        alice_uri = URIRef("http://example.org/Person/Alice")

        # Check Alice's age
        age_triples = list(alice_graph.triples((alice_uri, URIRef("http://example.org/Person/age"), None)))
        assert len(age_triples) == 1
        assert age_triples[0][2].value == 30
        assert age_triples[0][2].datatype == XSD.integer

        # Check Alice's gender
        gender_triples = list(alice_graph.triples((alice_uri, URIRef("http://example.org/Person/gender"), None)))
        assert len(gender_triples) == 1
        assert gender_triples[0][2] == URIRef("http://example.org/Gender/Female")

        # Check Alice's knows
        knows_triples = list(alice_graph.triples((alice_uri, URIRef("http://example.org/Person/knows"), None)))
        assert len(knows_triples) == 2

        knows_persons = set(knows_triple[2] for knows_triple in knows_triples)

        assert knows_persons == set([URIRef("http://example.org/Person/Bob"), URIRef("http://example.org/Person/Dave")])

        # Check Alice is baptized
        baptized_triples = list(alice_graph.triples((alice_uri, URIRef("http://example.org/Person/baptized"), None)))
        assert len(baptized_triples) == 1
        assert baptized_triples[0][2].value
        assert baptized_triples[0][2].datatype == XSD.boolean

        # Check Alice is left-handed
        rh_triples = list(alice_graph.triples((alice_uri, URIRef("http://example.org/Person/right_handed"), None)))
        assert len(rh_triples) == 1
        assert not rh_triples[0][2].value
        assert rh_triples[0][2].datatype == XSD.boolean

        # Check Alice knows someone (should have knows relationships)
        knows_triples = list(alice_graph.triples((alice_uri, URIRef("http://example.org/Person/knows"), None)))
        assert len(knows_triples) == 2  # Alice knows Bob and Dave

        # Check Alice's jobs
        job_triples = list(alice_graph.triples((alice_uri, URIRef("http://example.org/Person/job"), None)))
        assert len(job_triples) == 2  # SE and KE

        father_triples = list(alice_graph.triples((None, URIRef("http://example.org/Person/isFatherOf"), alice_uri)))
        assert len(father_triples) == 1
        father = father_triples[0][0]
        assert father == URIRef(f"http://example.org/Person/{alice.father}")

        # Check Alice's address
        address_triples = list(alice_graph.triples((alice_uri, URIRef("http://example.org/Person/address"), None)))
        assert len(address_triples) == 1
        address_node = address_triples[0][2]

        # Verify address is a blank node
        assert f"http://example.org/Person/{alice.name}Test/Address/" in str(address_node)

        # Check address properties
        street_triples = list(alice_graph.triples((address_node, URIRef("http://example.org/Address/street"), None)))
        assert len(street_triples) == 1
        assert street_triples[0][2].value == "Main Street"

        number_triples = list(alice_graph.triples((address_node, URIRef("http://example.org/Address/number"), None)))
        assert len(number_triples) == 1
        assert number_triples[0][2].value == 42

        zip_triples = list(alice_graph.triples((address_node, URIRef("http://example.org/Address/zip_code"), None)))
        assert len(zip_triples) == 1
        assert zip_triples[0][2].value == 12345

        city_triples = list(alice_graph.triples((address_node, URIRef("http://example.org/Address/city"), None)))
        assert len(city_triples) == 1
        assert city_triples[0][2].value == "Springfield"

        # Check Bob has no address
        bob = persons[1]
        bob_graph = bob.model_dump_rdf(context=test_context, parent=None, predicates=set())
        bob_uri = URIRef("http://example.org/Person/Bob")
        bob_address_triples = list(bob_graph.triples((bob_uri, URIRef("http://example.org/Person/address"), None)))
        assert len(bob_address_triples) == 0  # Bob has no address

        # Check Charlie's address
        charlie = persons[2]
        charlie_graph = charlie.model_dump_rdf(context=test_context, parent=None, predicates=set())
        charlie_uri = URIRef("http://example.org/Person/Charlie")
        charlie_address_triples = list(
            charlie_graph.triples((charlie_uri, URIRef("http://example.org/Person/address"), None))
        )
        assert len(charlie_address_triples) == 1
        charlie_address_node = charlie_address_triples[0][2]

        charlie_city_triples = list(
            charlie_graph.triples((charlie_address_node, URIRef("http://example.org/Address/city"), None))
        )
        assert len(charlie_city_triples) == 1
        assert charlie_city_triples[0][2].value == "Shelbyville"

    def test_person_model_to_shacl(self, shacl_context: ShaclMaterializationContext, shacl_graph: Graph) -> None:
        """Test that the Person model is converted to a valid SHACL Graph."""
        conforms, report, _ = validate(shacl_graph, shacl_graph=Graph().parse(SHACL_SHACL_PATH))

        assert conforms, "Does not conform to SHACL:\n" + report.serialize()

        # Test shape_name override
        assert URIRef(shacl_context.base_uri + "AddrShape") in shacl_graph.subjects(None)

    def test_person_data_valid(
        self, persons: list[Person], test_context: SimpleTestContext, shacl_graph: Graph
    ) -> None:

        person_graph = Graph()
        for person in persons:
            person_graph += person.model_dump_rdf(context=test_context, parent=None, predicates=set())

        conforms, report, _ = validate(person_graph, shacl_graph=shacl_graph)

        assert conforms, "Does not conform to SHACL:\n" + report.serialize()

    def test_error_invalid_inverse_property(self, test_context: SimpleTestContext, companies: list[Company]) -> None:

        with pytest.raises(RdfanticSerializationError):
            for company in companies:
                company.model_dump_rdf(context=test_context, parent=None, predicates=set())
