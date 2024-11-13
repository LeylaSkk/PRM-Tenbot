import json
from neo4j import GraphDatabase
from typing import Dict, Any
import logging
from tqdm import tqdm
import time
from itertools import islice

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NLPGraphBuilder:
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
    def close(self):
        self.driver.close()
        
    def chunk_data(self, data, chunk_size=1000):
        """Split data into smaller chunks"""
        for i in range(0, len(data), chunk_size):
            yield list(islice(data, i, i + chunk_size))
    
    def test_connection(self):
        """Test the Neo4j connection"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS test")
                result.single()
                logger.info("Successfully connected to Neo4j database")
                return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            return False

    def create_graph(self, nlp_data: Dict[str, Any]):
        try:
            # First test the connection
            if not self.test_connection():
                return
            
            logger.info("Starting graph creation process...")
            
            # Log the data structure
            logger.info(f"Data structure: {', '.join(nlp_data.keys())}")
            
            with self.driver.session() as session:
                # Create constraints and indexes
                logger.info("Creating constraints and indexes...")
                self._create_constraints(session)
                
                # Clear existing data
                logger.info("Clearing existing data...")
                session.run("MATCH (n) DETACH DELETE n")
                
                # Process entities in chunks
                entities = nlp_data["ner_analysis"]["entities"]
                logger.info(f"Processing {len(entities)} entities...")
                
                for chunk_idx, entity_chunk in enumerate(self.chunk_data(entities)):
                    try:
                        session.execute_write(
                            self._create_entities,
                            entity_chunk
                        )
                        logger.info(f"Processed entity chunk {chunk_idx + 1}")
                    except Exception as e:
                        logger.error(f"Error processing entity chunk {chunk_idx + 1}: {str(e)}")
                        raise
                
                # Process tokens in chunks
                tokens = nlp_data["pos_analysis"]["tokens"]
                logger.info(f"Processing {len(tokens)} tokens...")
                
                for chunk_idx, token_chunk in enumerate(self.chunk_data(tokens)):
                    try:
                        session.execute_write(
                            self._create_tokens,
                            token_chunk
                        )
                        logger.info(f"Processed token chunk {chunk_idx + 1}")
                    except Exception as e:
                        logger.error(f"Error processing token chunk {chunk_idx + 1}: {str(e)}")
                        raise
                
                # Create relationships in chunks
                logger.info("Creating relationships...")
                try:
                    session.execute_write(self._create_relationships)
                except Exception as e:
                    logger.error(f"Error creating relationships: {str(e)}")
                    raise
                
                # Verify the import
                logger.info("Verifying data...")
                stats = session.execute_read(self._verify_data)
                self._print_statistics(stats)
                
        except Exception as e:
            logger.error(f"Error creating graph: {str(e)}")
            raise
    
    @staticmethod
    def _create_constraints(session):
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Node) REQUIRE n.text IS NOT NULL",
            "CREATE INDEX IF NOT EXISTS FOR (n:Node) ON (n.type)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Node) ON (n.label)"
        ]
        
        for constraint in constraints:
            session.run(constraint)
    
    @staticmethod
    def _create_entities(tx, entities):
        query = """
        UNWIND $entities AS entity
        CREATE (e:Node:Entity {
            type: 'entity',
            text: entity.text,
            label: entity.label,
            start_pos: entity.start,
            end_pos: entity.end,
            description: entity.description
        })
        """
        tx.run(query, {'entities': entities})
    
    @staticmethod
    def _create_tokens(tx, tokens):
        query = """
        UNWIND $tokens AS token
        CREATE (t:Node:Token {
            type: 'token',
            text: token.text,
            lemma: token.lemma,
            pos: token.pos,
            tag: token.tag,
            dep: token.dep,
            pos_description: token.pos_description,
            tag_description: token.tag_description,
            is_stop: token.is_stop
        })
        """
        tx.run(query, {'tokens': tokens})
    
    @staticmethod
    def _create_relationships(tx):
        # Create NEXT relationships in batches
        tx.run("""
        MATCH (t1:Token)
        WITH t1
        MATCH (t2:Token)
        WHERE t2.text CONTAINS t1.text AND t1.text <> t2.text
        WITH t1, t2
        LIMIT 10000
        CREATE (t1)-[:NEXT]->(t2)
        """)
        
        # Create PART_OF relationships in batches
        tx.run("""
        MATCH (t:Token)
        WITH t
        MATCH (e:Entity)
        WHERE e.text CONTAINS t.text
        WITH t, e
        LIMIT 10000
        CREATE (t)-[:PART_OF]->(e)
        """)
    
    @staticmethod
    def _verify_data(tx):
        return {
            'node_counts': tx.run("""
                MATCH (n)
                RETURN labels(n) as type, count(n) as count
            """).data(),
            'relationship_counts': tx.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
            """).data()
        }
    
    @staticmethod
    def _print_statistics(stats):
        logger.info("\nFinal Statistics:")
        logger.info("\nNodes:")
        for stat in stats['node_counts']:
            logger.info(f"- {stat['type']}: {stat['count']}")
        logger.info("\nRelationships:")
        for stat in stats['relationship_counts']:
            logger.info(f"- {stat['type']}: {stat['count']}")

def main():
    # Configuration
    URI = "neo4j+s://95a99cad.databases.neo4j.io"
    USERNAME = "neo4j"
    PASSWORD = "VVtKoO1Pp29RhbSWTTtxxPxwAX9P8i5k0IzQba5natg"
    DATA_PATH = r'C:\Users\MK 10\OneDrive\Bureau\AI project\analysis_results.json'
    
    start_time = time.time()
    
    try:
        # Load data with progress indication
        logger.info("Loading JSON data...")
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            nlp_data = json.load(f)
        logger.info(f"Data loaded successfully in {time.time() - start_time:.2f} seconds")
        
        # Create and use the graph builder
        builder = NLPGraphBuilder(URI, USERNAME, PASSWORD)
        try:
            builder.create_graph(nlp_data)
        finally:
            builder.close()
            
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON file: {str(e)}")
    except FileNotFoundError:
        logger.error(f"Could not find file: {DATA_PATH}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        logger.info(f"Total execution time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()