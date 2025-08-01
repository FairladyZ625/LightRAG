

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from neo4j import AsyncGraphDatabase, exceptions as neo4jExceptions

# --- Configuration ---
# Set up your Neo4j connection details here
# You can use environment variables or directly set the strings
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE", "neo4j")

# --- Logger Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Neo4jToLightRAGConverter:
    """
    Connects to an existing Neo4j database, fetches graph data,
    and converts it into a format compatible with LightRAG's `ainsert_custom_kg` method.
    """

    def __init__(self, uri: str, user: str, password: str, database: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self._driver = None

    async def __aenter__(self):
        """Initializes the async database driver."""
        try:
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            await self._driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {self.uri}")
        except neo4jExceptions.AuthError:
            logger.error(f"Authentication failed for Neo4j. Please check your credentials.")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the async database driver."""
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j connection closed.")

    async def _run_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Helper function to run a Cypher query and return results."""
        try:
            async with self._driver.session(database=self.database) as session:
                result = await session.run(query, params or {})
                return [record.data() for record in await result.list()]
        except neo4jExceptions.CypherSyntaxError as e:
            logger.error(f"Cypher query syntax error: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while running the query: {e}")
            raise

    async def convert_to_lightrag_format(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetches all nodes and relationships from Neo4j and converts them
        into the LightRAG custom knowledge graph format.

        ********************************************************************
        *** IMPORTANT: You MUST customize the Cypher queries in this method
        *** to match your specific Neo4j graph schema.
        ********************************************************************

        Returns:
            A dictionary with 'entities' and 'relations' keys, ready to be
            used with `lightrag.ainsert_custom_kg`.
        """
        logger.info("Starting conversion from Neo4j to LightRAG format...")

        # 1. Customize this query to fetch your nodes.
        #    - You MUST return an 'entity_name' which is a unique string identifier for the node.
        #    - 'entity_type' should be the node's label.
        #    - 'description' should be a text summary of the node.
        #    - 'source_id' can be the node's original ID or another unique identifier.
        #    - You can add any other properties you want to keep.
        node_query = """
        MATCH (n)
        RETURN
            // --- REQUIRED FIELDS ---
            elementId(n) AS source_id,       // Using internal elementId as a unique source_id
            coalesce(n.name, n.title, elementId(n)) AS entity_name, // Use a name, title, or fallback to ID
            labels(n)[0] AS entity_type,     // Use the first label as the entity type
            // Create a text description from node properties
            apoc.convert.toJson(properties(n)) AS description,

            // --- OPTIONAL: Keep original properties ---
            properties(n) as properties
        """

        # 2. Customize this query to fetch your relationships.
        #    - You MUST return 'src_id' and 'tgt_id' which correspond to the 'entity_name'
        #      of the source and target nodes from the query above.
        #    - 'description' should be a text summary of the relationship.
        #    - 'keywords' can be used to add search terms.
        #    - 'weight' is a numeric value indicating the relationship's importance.
        relationship_query = """
        MATCH (src)-[r]->(tgt)
        RETURN
            // --- REQUIRED FIELDS ---
            coalesce(src.name, src.title, elementId(src)) AS src_id, // Must match the 'entity_name' of the source
            coalesce(tgt.name, tgt.title, elementId(tgt)) AS tgt_id, // Must match the 'entity_name' of the target
            type(r) AS description, // Use the relationship type as the description

            // --- OPTIONAL FIELDS ---
            apoc.convert.toJson(properties(r)) as keywords,
            1.0 AS weight, // Default weight
            elementId(r) as source_id
        """

        logger.info("Fetching nodes from Neo4j...")
        nodes_data = await self._run_query(node_query)
        logger.info(f"Found {len(nodes_data)} nodes.")

        logger.info("Fetching relationships from Neo4j...")
        relationships_data = await self._run_query(relationship_query)
        logger.info(f"Found {len(relationships_data)} relationships.")

        # The 'chunks' part is optional but useful if you want to create
        # text blocks for vector search that are linked to your graph entities.
        # Here, we create one chunk per node.
        chunks = [
            {
                'chunk_id': f"chunk_{node['source_id']}",
                'content': node['description'],
                'source_id': node['source_id'],
                'tokens': len(node['description'].split()),
                'chunk_order_index': 0
            }
            for node in nodes_data
        ]

        custom_kg = {
            "entities": nodes_data,
            "relations": relationships_data,
            "chunks": chunks
        }

        logger.info("Successfully converted data to LightRAG format.")
        return custom_kg


async def main():
    """
    Main function to run the converter and print the output.
    """
    logger.info("--- Neo4j to LightRAG Converter ---")

    # The converter is used within an async context manager to handle connections
    async with Neo4jToLightRAGConverter(
        uri=NEO4J_URI,
        user=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        database=NEO4J_DATABASE
    ) as converter:
        # Fetch and convert the data
        lightrag_formatted_data = await converter.convert_to_lightrag_format()

        # Now, `lightrag_formatted_data` can be used with LightRAG
        # For example:
        #
        # from lightrag import LightRAG
        #
        # rag = LightRAG(...)
        # await rag.initialize_storages()
        # await rag.ainsert_custom_kg(
        #     custom_kg=lightrag_formatted_data,
        #     full_doc_id="my_neo4j_graph"
        # )

        # For demonstration, we'll just print the counts and a sample
        print("\n--- Conversion Summary ---")
        num_entities = len(lightrag_formatted_data.get("entities", []))
        num_relations = len(lightrag_formatted_data.get("relations", []))
        print(f"Total entities converted: {num_entities}")
        print(f"Total relationships converted: {num_relations}")

        if num_entities > 0:
            print("\nSample Entity:")
            print(lightrag_formatted_data["entities"][0])

        if num_relations > 0:
            print("\nSample Relation:")
            print(lightrag_formatted_data["relations"][0])

if __name__ == "__main__":
    # This allows running the script directly to test the conversion.
    # Make sure your Neo4j instance is running.
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Conversion process cancelled by user.")

