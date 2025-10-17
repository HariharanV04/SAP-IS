"""
Knowledge Graph implementation for SAP iFlow analysis using Neo4j.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable

from models.iflow_models import SAPiFlowDocument, SAPComponent, Connection, IntegrationPattern, ComponentType, ConnectionType, PatternType

logger = logging.getLogger(__name__)

# Import schema mapper after other imports to avoid circular imports
try:
    from knowledge_graph.schema_mapping import schema_mapper
except ImportError:
    schema_mapper = None


class GraphStore:
    """Knowledge Graph store for SAP iFlow components and relationships using Neo4j."""
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialize graph store.
        
        Args:
            uri: Neo4j database URI
            username: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        self.verbose = 3  # 0=minimal, 1=concise, 2=show queries, 3=sample records + full details
        # Removed snapshot functionality as requested
    
    async def initialize(self):
        """Initialize the graph store and verify connection."""
        try:
            print(f"Attempting Neo4j connection to: {self.uri}")
            print(f"Username: {self.username}")
            print(f"Password length: {len(self.password) if self.password else 0}")
            
            # AuraDB-optimized driver configuration
            # Note: neo4j+s:// URI already implies encryption and trust settings
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                # AuraDB recommended settings (no encryption params needed for neo4j+s://)
                max_connection_lifetime=30 * 60,  # 30 minutes
                max_connection_pool_size=50,
                connection_acquisition_timeout=120  # 2 minutes
            )
            print("Neo4j driver created with AuraDB settings")
            
            # Verify connectivity with the built-in method
            await self.driver.verify_connectivity()
            print("Neo4j driver connectivity verified")
            
            # Test with AuraDB connection confirmation query and get detailed info
            async with self.driver.session() as session:
                print("Running AuraDB connection test...")
                result = await session.run("RETURN 'Connected to Aura!' AS msg, datetime() as timestamp")
                record = await result.single()
                print(f"AuraDB connection successful: {record['msg']} at {record['timestamp']}")
                
                # Get database details
                print("Fetching database information...")
                try:
                    # Get database name and edition
                    db_info = await session.run("""
                        CALL dbms.components() 
                        YIELD name, versions, edition 
                        RETURN name, versions[0] as version, edition
                        ORDER BY name
                    """)
                    
                    print("[NEO4J CLOUD] Database Information:")
                    async for record in db_info:
                        print(f"   • {record['name']}: {record['version']} ({record['edition']})")
                    
                    # Get node and relationship counts
                    node_count_result = await session.run("MATCH (n) RETURN count(n) as count")
                    node_count = await node_count_result.single()
                    
                    rel_count_result = await session.run("MATCH ()-[r]->() RETURN count(r) as count")
                    rel_count = await rel_count_result.single()
                    
                    print("[NEO4J CLOUD] Database Contents:")
                    print(f"   • Nodes: {node_count['count']:,}")
                    print(f"   • Relationships: {rel_count['count']:,}")
                    
                    # Get available node labels
                    labels_result = await session.run("CALL db.labels()")
                    labels = []
                    async for record in labels_result:
                        labels.append(record['label'])
                    
                    if labels:
                        print(f"[NEO4J CLOUD] Available Node Types: {', '.join(labels[:10])}")
                        if len(labels) > 10:
                            print(f"   ... and {len(labels) - 10} more")
                    
                    # Show schema mapping information
                    if schema_mapper:
                        print("\n[SCHEMA MAPPING] iFlow Database Structure:")
                        print("   Process nodes -> iFlow packages/processes")
                        print("   Component nodes -> BPMN elements (events, tasks, gateways)")
                        print("   Relationships -> Flow connections (FLOWS_TO, CONNECTS_TO)")
                        print("   SubProcess/Protocol -> Assets and configurations")
                        print("   Folder nodes -> Organizational containers")
                    
                except Exception as e:
                    print(f"Could not fetch detailed database info: {e}")
            
            print("Graph store initialized successfully with AuraDB")
            print(f"[NEO4J CLOUD] Connected to: {self.uri}")
            print(f"[NEO4J CLOUD] Authenticated as: {self.username}")
            print(f"[NEO4J CLOUD] Using secure connection (TLS)")
            print("[PURPOSE] SAP iFlow Integration Analysis & Component Relationships")
            print("=" * 60)
            
        except ServiceUnavailable as e:
            print(f"Neo4j service unavailable - check AuraDB instance status: {e}")
            raise
        except Exception as e:
            print(f"Neo4j connection error: {e}")
            print(f"Debug info - URI: {self.uri}, Username: {self.username}")
            print(f"For AuraDB, ensure:")
            print(f"   - URI starts with 'neo4j+s://' for secure connection")
            print(f"   - Username and password are correct")
            print(f"   - Database instance is active in Neo4j Aura Console")
            raise
    
    async def close(self):
        """Close the graph store connection."""
        if self.driver:
            await self.driver.close()
    
    async def _execute_cypher_with_logging(self, session, cypher_query: str, parameters: dict = None, description: str = ""):
        """Execute Cypher query with comprehensive logging."""
        # Clean up query for better display
        clean_query = ' '.join(cypher_query.strip().split())
        
        print(f"\n[CYPHER EXECUTION] {description}")
        print(f"[CYPHER QUERY] {clean_query}")
        if parameters:
            print(f"[PARAMETERS] {parameters}")
        
        try:
            result = await session.run(cypher_query, parameters or {})
            records = []
            async for record in result:
                records.append(dict(record))
            
            print(f"[RESULT] {len(records)} rows returned")
            
            if records:
                print(f"[DATA ANALYSIS] Sample records (first 3):")
                for i, record in enumerate(records[:3], 1):
                    print(f"   Record {i}: {record}")
                if len(records) > 3:
                    print(f"   ... and {len(records) - 3} more records")
                    
                # Show data structure
                sample = records[0]
                print(f"[DATA STRUCTURE] Fields: {list(sample.keys())}")
                for key, value in sample.items():
                    if isinstance(value, (dict, list)):
                        print(f"   • {key}: {type(value).__name__} with {len(value) if hasattr(value, '__len__') else 'N/A'} items")
                    else:
                        print(f"   • {key}: {type(value).__name__} = {str(value)[:50]}{'...' if len(str(value)) > 50 else ''}")
            else:
                print("[DATA ANALYSIS] No data returned")
            
            return records
            
        except Exception as e:
            print(f"[CYPHER] Failed: {str(e)}")
            if self.verbose >= 2:
                print(f"   Query: {clean_query}")
                if parameters:
                    print(f"   Params: {parameters}")
            raise

    async def get_schema_overview(self) -> Dict[str, Any]:
        """Return concise schema overview: labels with counts and relationship types with counts."""
        overview = {"labels": {}, "relationship_types": {}}
        try:
            async with self.driver.session() as session:
                # Labels and counts
                labels_records = await session.run("CALL db.labels()")
                labels = []
                async for rec in labels_records:
                    labels.append(rec[0])
                for label in labels:
                    q = f"MATCH (n:`{label}`) RETURN count(n) as cnt"
                    cnt_rec = await session.run(q)
                    one = await cnt_rec.single()
                    overview["labels"][label] = one[0] if one else 0
                # Relationship types and counts
                reltype_records = await session.run("CALL db.relationshipTypes()")
                reltypes = []
                async for rec in reltype_records:
                    reltypes.append(rec[0])
                for relt in reltypes:
                    q = f"MATCH ()-[r:`{relt}`]->() RETURN count(r) as cnt"
                    cnt_rec = await session.run(q)
                    one = await cnt_rec.single()
                    overview["relationship_types"][relt] = one[0] if one else 0
        except Exception as e:
            print(f"[SCHEMA] Failed to fetch schema overview: {e}")
        # Concise log
        labels_sorted = sorted(overview["labels"].items(), key=lambda kv: -kv[1])
        rels_sorted = sorted(overview["relationship_types"].items(), key=lambda kv: -kv[1])
        print("[SCHEMA] Labels:", ", ".join([f"{k}({v})" for k,v in labels_sorted[:6]]), ("..." if len(labels_sorted)>6 else ""))
        print("[SCHEMA] Relationships:", ", ".join([f"{k}({v})" for k,v in rels_sorted[:6]]), ("..." if len(rels_sorted)>6 else ""))
        return overview
    

    async def get_iflow_skeleton(self, iflow_name: str) -> Dict[str, Any]:
        """Get iFlow skeleton topology from Neo4j by name - as required by playbook.
        
        Returns {nodes: [{id, name, type}], edges: [{from, to, relation}]}
        """
        try:
            async with self.driver.session() as session:
                # First try to find the process/package by name with broader search
                query = """
                MATCH (p:Process)
                WHERE toLower(p.name) CONTAINS toLower($name) 
                   OR toLower(p.id) CONTAINS toLower($name)
                   OR toLower(p.folder_id) CONTAINS toLower($name)
                WITH p LIMIT 1
                MATCH (p)-[:CONTAINS]->(c:Component)
                OPTIONAL MATCH (c)-[r]->(d:Component)
                WHERE (p)-[:CONTAINS]->(d)
                RETURN collect(DISTINCT {id: c.id, name: c.name, type: c.type, folder_id: c.folder_id}) AS nodes,
                       collect(DISTINCT {from: c.id, to: d.id, relation: type(r)}) AS edges
                """
                
                records = await self._execute_cypher_with_logging(session, query, {"name": iflow_name}, f"Getting iFlow skeleton for '{iflow_name}'")
                
                if records and records[0]["nodes"]:
                    return {
                        "nodes": [n for n in records[0]["nodes"] if n["id"]],
                        "edges": [e for e in records[0]["edges"] if e["from"] and e["to"]]
                    }
                else:
                    # Fallback: try broader component search with fuzzy matching
                    query2 = """
                    MATCH (c:Component)
                    WHERE toLower(c.name) CONTAINS toLower($name) 
                       OR toLower(c.folder_id) CONTAINS toLower($name)
                       OR toLower(c.id) CONTAINS toLower($name)
                    WITH c LIMIT 50
                    OPTIONAL MATCH (c)-[r]->(d:Component)
                    RETURN collect(DISTINCT {id: c.id, name: c.name, type: c.type, folder_id: c.folder_id}) AS nodes,
                           collect(DISTINCT {from: c.id, to: d.id, relation: type(r)}) AS edges
                    """
                    
                    records2 = await self._execute_cypher_with_logging(session, query2, {"name": iflow_name}, f"Fallback component search for '{iflow_name}'")
                    
                    if records2 and records2[0]["nodes"]:
                        return {
                            "nodes": [n for n in records2[0]["nodes"] if n["id"]],
                            "edges": [e for e in records2[0]["edges"] if e["from"] and e["to"]]
                        }
                    
                    # Final fallback: try partial word matching
                    words = iflow_name.lower().split()
                    if len(words) > 1:
                        query3 = """
                        MATCH (c:Component)
                        WHERE ANY(word IN $words WHERE toLower(c.name) CONTAINS word 
                                                   OR toLower(c.folder_id) CONTAINS word
                                                   OR toLower(c.id) CONTAINS word)
                        WITH c LIMIT 30
                        OPTIONAL MATCH (c)-[r]->(d:Component)
                        RETURN collect(DISTINCT {id: c.id, name: c.name, type: c.type, folder_id: c.folder_id}) AS nodes,
                               collect(DISTINCT {from: c.id, to: d.id, relation: type(r)}) AS edges
                        """
                        
                        records3 = await self._execute_cypher_with_logging(session, query3, {"words": words}, f"Word-based search for '{iflow_name}'")
                        
                        if records3 and records3[0]["nodes"]:
                            return {
                                "nodes": [n for n in records3[0]["nodes"] if n["id"]],
                                "edges": [e for e in records3[0]["edges"] if e["from"] and e["to"]]
                            }
                
                return {"nodes": [], "edges": []}
                
        except Exception as e:
            logger.error(f"Error getting iFlow skeleton: {e}")
            return {"nodes": [], "edges": []}

    # Methods for iFlow Neo4j schema (Process, Component, etc.)
    async def query_iflow_packages(self, package_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query iFlow packages from Neo4j (using Process nodes)."""
        try:
            async with self.driver.session() as session:
                if package_name:
                    query = """
                        MATCH (p:Process) 
                        WHERE toLower(p.name) CONTAINS toLower($name) OR toLower(p.id) CONTAINS toLower($name)
                        RETURN p.id as package_id, p.name as package_name, p.type as type,
                               p.folder_id as folder_id
                    """
                    description = f"Searching for iFlow packages containing '{package_name}'"
                    records = await self._execute_cypher_with_logging(session, query, {"name": package_name}, description)
                else:
                    query = """
                        MATCH (p:Process)
                        RETURN p.id as package_id, p.name as package_name, p.type as type,
                               p.folder_id as folder_id
                        LIMIT 50
                    """
                    description = "Listing all iFlow packages (limit 10)"
                    records = await self._execute_cypher_with_logging(session, query, {}, description)
                
                # Convert to expected format
                packages = []
                for record in records:
                    packages.append({
                        'package_id': record['package_id'],
                        'package_name': record['package_name'],
                        'type': record['type'],
                        'folder_id': record['folder_id']
                    })
                
                return packages
                
        except Exception as e:
            logger.error(f"Error querying iFlow packages: {e}")
            return []
    
    async def query_iflow_components(self, component_type: Optional[str] = None, component_id: Optional[str] = None, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query iFlow components from Neo4j (using Component nodes)."""
        try:
            async with self.driver.session() as session:
                # Build dynamic query based on filters
                conditions = []
                params = {}
                
                if component_id:
                    conditions.append("c.id = $component_id")
                    params['component_id'] = component_id
                elif component_type:
                    conditions.append("toLower(c.type) CONTAINS toLower($component_type)")
                    params['component_type'] = component_type
                
                if folder_id:
                    conditions.append("toLower(c.folder_id) CONTAINS toLower($folder_id)")
                    params['folder_id'] = folder_id
                
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                
                query = f"""
                    MATCH (c:Component)
                    WHERE {where_clause}
                    RETURN c.id as component_id, c.type as component_type,
                           c.name as name, c.folder_id as folder_id
                    LIMIT 100
                """
                
                # Build description for logging
                filter_parts = []
                if component_id:
                    filter_parts.append(f"ID='{component_id}'")
                if component_type:
                    filter_parts.append(f"type='{component_type}'")
                if folder_id:
                    filter_parts.append(f"folder='{folder_id}'")
                
                if filter_parts:
                    description = f"Searching for iFlow components with filters: {', '.join(filter_parts)}"
                else:
                    description = "Listing all iFlow components (limit 20)"
                
                records = await self._execute_cypher_with_logging(session, query, params, description)
                
                components = []
                for record in records:
                    components.append({
                        'component_id': record['component_id'],
                        'component_type': record['component_type'],
                        'name': record['name'],
                        'folder_id': record['folder_id']
                    })
                
                return components
                
        except Exception as e:
            logger.error(f"Error querying iFlow components: {e}")
            return []

    async def query_components_by_sequence_flow(self, flow_identifier: str) -> List[Dict[str, Any]]:
        """
        List components connected by a specific sequence flow identifier.
        Matches any relationship where ANY property equals the given identifier.
        
        Args:
            flow_identifier: e.g., "SequenceFlow_81564015"
        Returns:
            List of connections with source/target component details and relationship type
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MATCH (source:Component)-[r]->(target:Component)
                    WHERE ANY(k IN keys(r) WHERE toString(r[k]) = $fid)
                    RETURN source.id as source_id, source.name as source_name, source.type as source_type,
                           target.id as target_id, target.name as target_name, target.type as target_type,
                           type(r) as rel_type, r as rel
                    ORDER BY source_id, target_id
                    """,
                    fid=flow_identifier
                )
                rows = []
                async for rec in result:
                    rows.append({
                        'source_id': rec['source_id'],
                        'source_name': rec['source_name'],
                        'source_type': rec['source_type'],
                        'target_id': rec['target_id'],
                        'target_name': rec['target_name'],
                        'target_type': rec['target_type'],
                        'relationship_type': rec['rel_type']
                    })
                return rows
        except Exception as e:
            logger.error(f"Error querying components by sequence flow: {e}")
            return []
    
    async def query_technologies(self, tech_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query technologies from existing Neo4j data."""
        try:
            async with self.driver.session() as session:
                if tech_name:
                    result = await session.run("""
                        MATCH (t:Technology)
                        WHERE toLower(t.name) CONTAINS toLower($name)
                        RETURN t.name as name, t.category as category, t.description as description,
                               t.year_introduced as year_introduced
                    """, name=tech_name)
                else:
                    result = await session.run("""
                        MATCH (t:Technology)
                        RETURN t.name as name, t.category as category, t.description as description,
                               t.year_introduced as year_introduced
                    """)
                
                technologies = []
                async for record in result:
                    technologies.append({
                        'name': record['name'],
                        'category': record['category'],
                        'description': record['description'],
                        'year_introduced': record['year_introduced']
                    })
                
                return technologies
                
        except Exception as e:
            logger.error(f"Error querying technologies: {e}")
            return []
    
    async def query_relationships(self, entity_name: str) -> Dict[str, Any]:
        """Query all relationships for a given entity."""
        try:
            async with self.driver.session() as session:
                result = await session.run("""
                    MATCH (n)
                    WHERE toLower(n.name) CONTAINS toLower($name)
                    OPTIONAL MATCH (n)-[r1]->(related1)
                    OPTIONAL MATCH (related2)-[r2]->(n)
                    RETURN labels(n) as node_labels, n.name as name, 
                           collect(DISTINCT {type: type(r1), target: related1.name, target_labels: labels(related1)}) as outgoing,
                           collect(DISTINCT {type: type(r2), source: related2.name, source_labels: labels(related2)}) as incoming
                """, name=entity_name)
                
                record = await result.single()
                if not record:
                    return {}
                
                return {
                    'entity': {
                        'name': record['name'],
                        'labels': record['node_labels']
                    },
                    'outgoing_relationships': [rel for rel in record['outgoing'] if rel['target']],
                    'incoming_relationships': [rel for rel in record['incoming'] if rel['source']]
                }
                
        except Exception as e:
            logger.error(f"Error querying relationships: {e}")
            return {}
    
    async def _create_constraints(self):
        """Create constraints and indexes for the graph."""
        async with self.driver.session() as session:
            # Create constraints
            await session.run("CREATE CONSTRAINT document_name IF NOT EXISTS FOR (d:Document) REQUIRE d.name IS UNIQUE")
            await session.run("CREATE CONSTRAINT component_id IF NOT EXISTS FOR (c:Component) REQUIRE c.id IS UNIQUE")
            await session.run("CREATE CONSTRAINT pattern_name IF NOT EXISTS FOR (p:Pattern) REQUIRE p.name IS UNIQUE")
            
            # Create indexes
            await session.run("CREATE INDEX component_type IF NOT EXISTS FOR (c:Component) ON (c.type)")
            await session.run("CREATE INDEX connection_type IF NOT EXISTS FOR (r:Connection) ON (r.type)")
            await session.run("CREATE INDEX pattern_type IF NOT EXISTS FOR (p:Pattern) ON (p.type)")
    
    async def store_document(self, document: SAPiFlowDocument) -> str:
        """
        Store a SAP iFlow document in the knowledge graph.
        
        Args:
            document: SAP iFlow document to store
            
        Returns:
            Document ID in the graph
        """
        try:
            async with self.driver.session() as session:
                # Create document node
                doc_result = await session.run("""
                    MERGE (d:Document {name: $name})
                    SET d.package_name = $package_name,
                        d.version = $version,
                        d.description = $description,
                        d.created_at = datetime($created_at),
                        d.updated_at = datetime($updated_at)
                    RETURN d.name as doc_id
                """, 
                name=getattr(document, 'name', None) or getattr(document.document_metadata, 'document_id', 'unknown'),
                package_name=getattr(document, 'package_name', 'unknown'),
                version=getattr(document, 'version', '1.0'),
                description=getattr(document, 'description', '') or getattr(document.document_metadata, 'description', ''),
                created_at=getattr(document, 'created_at', datetime.now()).isoformat(),
                updated_at=datetime.now().isoformat()
                )
                
                doc_id = await doc_result.single()
                doc_id = doc_id["doc_id"]
                
                # Store components
                for component in document.components:
                    await self._store_component(session, doc_id, component)
                
                # Store connections
                for connection in document.connections:
                    await self._store_connection(session, doc_id, connection)
                
                # Store patterns
                for pattern in document.patterns:
                    await self._store_pattern(session, doc_id, pattern)
                
                doc_name = getattr(document, 'name', None) or getattr(document.document_metadata, 'document_id', 'unknown')
                logger.info(f"Stored document '{doc_name}' in knowledge graph")
                return doc_id
                
        except Exception as e:
            logger.error(f"Error storing document in graph: {e}")
            raise
    
    async def _store_component(self, session, doc_id: str, component):
        """Store a component in the knowledge graph."""
        component_id = f"{doc_id}_{component.component_name}"
        
        await session.run("""
            MERGE (c:Component {id: $id})
            SET c.name = $name,
                c.type = $type,
                c.document = $document,
                c.position_x = $position_x,
                c.position_y = $position_y,
                c.created_at = datetime($created_at)
            WITH c
            MATCH (d:Document {name: $document})
            MERGE (d)-[:CONTAINS]->(c)
        """,
        id=component_id,
        name=component.component_name,
        type=str(component.component_type),
        document=doc_id,
        position_x=getattr(component, 'position_x', 0),
        position_y=getattr(component, 'position_y', 0),
        created_at=getattr(component, 'created_at', datetime.now()).isoformat()
        )
        
        # Store configuration as properties
        if hasattr(component, 'configuration') and component.configuration:
            config_dict = component.configuration.dict() if hasattr(component.configuration, 'dict') else component.configuration
            for key, value in config_dict.items():
                await session.run("""
                    MATCH (c:Component {id: $id})
                    SET c.config_$key = $value
                """,
                id=component_id,
                key=key,
                value=str(value)
                )
        
        # Store metadata
        if hasattr(component, 'metadata') and component.metadata:
            metadata_dict = component.metadata.dict() if hasattr(component.metadata, 'dict') else component.metadata
            for key, value in metadata_dict.items():
                await session.run("""
                    MATCH (c:Component {id: $id})
                    SET c.`meta_$key` = $value
                """,
                id=component_id,
                key=key,
                value=str(value)
                )
    
    async def _store_connection(self, session, doc_id: str, connection):
        """Store a connection in the knowledge graph."""
        from_id = f"{doc_id}_{connection.source_component}"
        to_id = f"{doc_id}_{connection.target_component}"
        
        await session.run("""
            MATCH (from:Component {id: $from_id})
            MATCH (to:Component {id: $to_id})
            MERGE (from)-[r:Connection {type: $type}]->(to)
            SET r.created_at = datetime($created_at)
        """,
        from_id=from_id,
        to_id=to_id,
        type=str(connection.connection_type),
        created_at=datetime.now().isoformat()
        )
        
        # Store connection metadata
        if hasattr(connection, 'metadata') and connection.metadata:
            metadata_dict = connection.metadata.dict() if hasattr(connection.metadata, 'dict') else connection.metadata
            for key, value in metadata_dict.items():
                await session.run("""
                    MATCH (from:Component {id: $from_id})-[r:Connection]->(to:Component {id: $to_id})
                    SET r.`meta_$key` = $value
                """,
                from_id=from_id,
                to_id=to_id,
                key=key,
                value=str(value)
                )
    
    async def _store_pattern(self, session, doc_id: str, pattern):
        """Store an integration pattern in the knowledge graph."""
        pattern_id = f"{doc_id}_{pattern.pattern_name}"
        
        await session.run("""
            MERGE (p:Pattern {name: $name})
            SET p.type = $type,
                p.description = $description,
                p.complexity_score = $complexity_score,
                p.document = $document,
                p.created_at = datetime($created_at)
            WITH p
            MATCH (d:Document {name: $document})
            MERGE (d)-[:HAS_PATTERN]->(p)
        """,
        name=pattern_id,
        type=str(pattern.pattern_type),
        description=pattern.description,
        complexity_score=pattern.complexity_rating,
        document=doc_id,
        created_at=datetime.now().isoformat()
        )
        
        # Connect pattern to components (if components exist)
        if hasattr(pattern, 'components') and pattern.components:
            for component in pattern.components:
                component_id = f"{doc_id}_{component.component_name}"
                await session.run("""
                    MATCH (p:Pattern {name: $pattern_name})
                    MATCH (c:Component {id: $component_id})
                    MERGE (p)-[:INCLUDES]->(c)
                """,
                pattern_name=pattern_id,
                component_id=component_id
                )
    
    async def find_similar_components(self, component_type: ComponentType, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find similar components by type.
        
        Args:
            component_type: Type of component to search for
            limit: Maximum number of results
            
        Returns:
            List of similar components
        """
        try:
            async with self.driver.session() as session:
                result = await session.run("""
                    MATCH (c:Component {type: $type})
                    MATCH (d:Document)-[:CONTAINS]->(c)
                    RETURN c.id as id, c.name as name, c.type as type, 
                           d.name as document, d.package_name as package_name,
                           c.position_x as position_x, c.position_y as position_y
                    LIMIT $limit
                """,
                type=str(component_type),
                limit=limit
                )
                
                components = []
                async for record in result:
                    components.append({
                        'id': record['id'],
                        'name': record['name'],
                        'type': record['type'],
                        'document': record['document'],
                        'package_name': record['package_name'],
                        'position_x': record['position_x'],
                        'position_y': record['position_y']
                    })
                
                return components
                
        except Exception as e:
            logger.error(f"Error finding similar components: {e}")
            raise
    
    async def find_component_relationships(self, component_name: str) -> Dict[str, Any]:
        """
        Find relationships for a specific Component.
        
        Args:
            component_name: Name or ID of the component
            
        Returns:
            Dictionary with component relationships
        """
        try:
            async with self.driver.session() as session:
                # Find component by id or name and get its relationships
                query = """
                    MATCH (c:Component) 
                    WHERE c.id = $name OR c.name = $name
                    OPTIONAL MATCH (c)-[r1:FLOWS_TO]->(target:Component)
                    OPTIONAL MATCH (source:Component)-[r2:FLOWS_TO]->(c)
                    OPTIONAL MATCH (c)-[r3:CONNECTS_TO]->(connected:Component)
                    RETURN c, 
                           collect(DISTINCT {target: target.id, target_name: target.name, target_type: target.type, rel_type: 'FLOWS_TO'}) as outgoing_flows,
                           collect(DISTINCT {source: source.id, source_name: source.name, source_type: source.type, rel_type: 'FLOWS_TO'}) as incoming_flows,
                           collect(DISTINCT {connected: connected.id, connected_name: connected.name, connected_type: connected.type, rel_type: 'CONNECTS_TO'}) as connections
                """
                description = f"Finding relationships for component '{component_name}'"
                records = await self._execute_cypher_with_logging(session, query, {"name": component_name}, description)
                
                if not records:
                    return {}
                
                record = records[0]  # Get the first (and only) record
                component = record['c']
                
                # Combine all outgoing connections
                outgoing = [conn for conn in record['outgoing_flows'] if conn['target']] + \
                          [conn for conn in record['connections'] if conn['connected']]
                
                return {
                    'component': {
                        'id': component['id'],
                        'name': component.get('name', component['id']),
                        'type': component['type'],
                        'folder_id': component.get('folder_id')
                    },
                    'outgoing_connections': outgoing,
                    'incoming_connections': [conn for conn in record['incoming_flows'] if conn['source']],
                    'patterns': [],
                    'documents': [component.get('folder_id')] if component.get('folder_id') else []
                }
                
        except Exception as e:
            logger.error(f"Error finding component relationships: {e}")
            raise
    
    async def comprehensive_neo4j_search(self, user_query: str) -> Dict[str, Any]:
        """
        Perform comprehensive search across ALL Neo4j data using multiple query strategies.
        This method ensures we extract maximum information from the knowledge graph.
        
        Args:
            user_query: The user's search query
            
        Returns:
            Dictionary with comprehensive results from all Neo4j queries
        """
        print(f"\n[COMPREHENSIVE NEO4J SEARCH] Executing ALL available Neo4j queries for: '{user_query}'")
        print("=" * 80)
        
        search_results = {
            "packages": [],
            "components": [],
            "component_relationships": [],
            "sequence_flows": [],
            "patterns": [],
            "technologies": [],
            "related_data": [],
            "total_queries": 0,
            "successful_queries": 0
        }
        

        # STRATEGY 1: Search for packages (Process nodes)
        try:
            print("\n[NEO4J QUERY 1] Searching iFlow packages...")
            packages = await self.query_iflow_packages()
            if packages:
                search_results["packages"] = packages
                search_results["successful_queries"] += 1
                print(f"Found {len(packages)} packages")
            search_results["total_queries"] += 1
        except Exception as e:
            print(f"Package search failed: {e}")
        
        # STRATEGY 2: Search for all components
        try:
            print("\n[NEO4J QUERY 2] Searching all iFlow components...")
            components = await self.query_iflow_components()
            if components:
                search_results["components"] = components
                search_results["successful_queries"] += 1
                print(f"Found {len(components)} components")
            search_results["total_queries"] += 1
        except Exception as e:
            print(f"Component search failed: {e}")
        
        # STRATEGY 3: Search for specific component types mentioned in query
        component_types_to_try = [
            "StartEvent", "EndEvent", "IntermediateEvent", 
            "ServiceTask", "UserTask", "ScriptTask",
            "ExclusiveGateway", "ParallelGateway",
            "SFTP", "HTTP", "OData", "SOAP", "JDBC"
        ]
        
        query_lower = user_query.lower()
        for comp_type in component_types_to_try:
            if comp_type.lower() in query_lower:
                try:
                    print(f"\n[NEO4J QUERY 3.{comp_type}] Searching {comp_type} components...")
                    type_components = await self.query_iflow_components(component_type=comp_type)
                    if type_components:
                        # Add to components if not already found
                        existing_ids = {c['component_id'] for c in search_results["components"]}
                        new_components = [c for c in type_components if c['component_id'] not in existing_ids]
                        search_results["components"].extend(new_components)
                        search_results["successful_queries"] += 1
                        print(f"Found {len(type_components)} {comp_type} components")
                    search_results["total_queries"] += 1
                except Exception as e:
                    print(f"{comp_type} search failed: {e}")
        
        # STRATEGY 4: Try to find component relationships for any mentioned components
        # Extract potential component names from query
        potential_component_names = []
        words = user_query.replace('_', ' ').replace('-', ' ').split()
        for word in words:
            if len(word) > 3:  # Skip short words
                potential_component_names.append(word)
        
        for comp_name in potential_component_names[:5]:  # Limit to 5 to avoid too many queries
            try:
                print(f"\n[NEO4J QUERY 4.{comp_name}] Finding relationships for '{comp_name}'...")
                relationships = await self.find_component_relationships(comp_name)
                if relationships:
                    search_results["component_relationships"].append(relationships)
                    search_results["successful_queries"] += 1
                    print(f"Found relationships for component '{comp_name}'")
                search_results["total_queries"] += 1
            except Exception as e:
                print(f"Relationship search for '{comp_name}' failed: {e}")
        
        # STRATEGY 5: Search for sequence flows if mentioned
        if 'sequence' in query_lower or 'flow' in query_lower:
            try:
                print("\n[NEO4J QUERY 5] Searching for sequence flows...")
                # Try to extract sequence flow identifiers
                import re
                seq_matches = re.findall(r'sequenceflow[_\s]*\w+', query_lower)
                for seq_match in seq_matches[:3]:  # Limit to 3
                    try:
                        flow_data = await self.query_components_by_sequence_flow(seq_match)
                        if flow_data:
                            search_results["sequence_flows"].extend(flow_data)
                            search_results["successful_queries"] += 1
                            print(f"Found sequence flow data for '{seq_match}'")
                        search_results["total_queries"] += 1
                    except Exception as e:
                        print(f"Sequence flow search for '{seq_match}' failed: {e}")
            except Exception as e:
                print(f"General sequence flow search failed: {e}")
        
        # STRATEGY 6: Search for integration patterns
        try:
            print("\n[NEO4J QUERY 6] Searching integration patterns...")
            patterns = await self.find_integration_patterns()
            if patterns:
                search_results["patterns"] = patterns
                search_results["successful_queries"] += 1
                print(f"Found {len(patterns)} integration patterns")
            search_results["total_queries"] += 1
        except Exception as e:
            print(f"Pattern search failed: {e}")
        
        # STRATEGY 7: Search for technologies
        try:
            print("\n[NEO4J QUERY 7] Searching technologies...")
            technologies = await self.query_technologies()
            if technologies:
                search_results["technologies"] = technologies
                search_results["successful_queries"] += 1
                print(f"Found {len(technologies)} technologies")
            search_results["total_queries"] += 1
        except Exception as e:
            print(f"Technology search failed: {e}")
        
        # STRATEGY 8: General relationship search
        for word in words[:3]:  # Try first few words
            if len(word) > 4:
                try:
                    print(f"\n[NEO4J QUERY 8.{word}] General relationship search for '{word}'...")
                    relationships = await self.query_relationships(word)
                    if relationships and relationships.get('entity'):
                        search_results["related_data"].append(relationships)
                        search_results["successful_queries"] += 1
                        print(f"Found relationships for '{word}'")
                    search_results["total_queries"] += 1
                except Exception as e:
                    print(f"General relationship search for '{word}' failed: {e}")
        
        # Summary
        print(f"\n[COMPREHENSIVE NEO4J SEARCH COMPLETE]")
        print(f"   • Total queries executed: {search_results['total_queries']}")
        print(f"   • Successful queries: {search_results['successful_queries']}")
        print(f"   • Packages found: {len(search_results['packages'])}")
        print(f"   • Components found: {len(search_results['components'])}")
        print(f"   • Component relationships found: {len(search_results['component_relationships'])}")
        print(f"   • Sequence flows found: {len(search_results['sequence_flows'])}")
        print(f"   • Patterns found: {len(search_results['patterns'])}")
        print(f"   • Technologies found: {len(search_results['technologies'])}")
        print(f"   • Related data found: {len(search_results['related_data'])}")
        print("=" * 80)
        
        return search_results
    
    async def find_integration_patterns(self, pattern_type: Optional[PatternType] = None) -> List[Dict[str, Any]]:
        """
        Find integration patterns from iFlow data.
        Since the new schema may not have explicit patterns, we analyze flow patterns.
        
        Args:
            pattern_type: Optional pattern type to filter by
            
        Returns:
            List of integration patterns found in the flows
        """
        try:
            async with self.driver.session() as session:
                # Analyze flow patterns from the iFlow data
                result = await session.run("""
                    MATCH (source:Component)-[r]->(target:Component)
                    RETURN source.type as source_type, 
                           target.type as target_type,
                           type(r) as flow_type,
                           count(*) as frequency
                    ORDER BY frequency DESC
                    LIMIT 10
                """)
                
                patterns = []
                async for record in result:
                    pattern_name = f"{record['source_type']}_to_{record['target_type']}_Pattern"
                    patterns.append({
                        'name': pattern_name,
                        'type': f"{record['flow_type']}_flow",
                        'description': f"Pattern: {record['source_type']} connected to {record['target_type']} via {record['flow_type']} flow",
                        'complexity_score': min(record['frequency'] / 2.0, 10.0),  # Simple complexity based on frequency
                        'document': 'Derived from relationship patterns',
                        'components': [record['source_type'], record['target_type']],
                        'frequency': record['frequency']
                    })
                
                return patterns
                
        except Exception as e:
            logger.error(f"Error finding integration patterns: {e}")
            # Return empty list instead of raising to avoid breaking the flow
            return []
    
    async def get_component_reusability_score(self, component_name: str) -> float:
        """
        Calculate reusability score for an iFlow component based on connection patterns.
        Updated to work with new iFlow schema.
        
        Args:
            component_name: Name or ID of the component
            
        Returns:
            Reusability score (0-1)
        """
        try:
            async with self.driver.session() as session:
                # Count how many different flows this component is involved in
                result = await session.run("""
                    MATCH (c:iflow_components) 
                    WHERE c.component_id = $name OR c.name = $name
                    OPTIONAL MATCH (f1:iflow_flows) WHERE f1.source_component_id = c.component_id
                    OPTIONAL MATCH (f2:iflow_flows) WHERE f2.target_component_id = c.component_id
                    WITH c, count(DISTINCT f1) + count(DISTINCT f2) as connection_count
                    OPTIONAL MATCH (same_type:iflow_components) 
                    WHERE same_type.component_type = c.component_type AND same_type.component_id <> c.component_id
                    RETURN connection_count, count(DISTINCT same_type) as similar_components
                """,
                name=component_name
                )
                
                record = await result.single()
                if not record:
                    return 0.0
                
                connection_count = record['connection_count'] or 0
                similar_components = record['similar_components'] or 0
                
                # Score based on connections (more connections = more reusable) and rarity
                connection_score = min(connection_count / 10.0, 1.0)  # Normalize connections
                rarity_score = max(0.1, 1.0 - (similar_components / 50.0))  # Less common = more valuable
                
                return (connection_score + rarity_score) / 2.0
                
        except Exception as e:
            logger.error(f"Error calculating reusability score: {e}")
            return 0.0
    
    async def find_related_components(self, component_name: str, depth: int = 2) -> List[Dict[str, Any]]:
        """
        Find iFlow components related to a given component through flow connections.
        Updated to work with new iFlow schema.
        
        Args:
            component_name: Name or ID of the component
            depth: Maximum relationship depth
            
        Returns:
            List of related components with their relationships
        """
        try:
            async with self.driver.session() as session:
                # Find components connected through flows (direct and indirect)
                result = await session.run("""
                    MATCH (start:iflow_components) 
                    WHERE start.component_id = $name OR start.name = $name
                    
                    // Find directly connected components (depth 1)
                    OPTIONAL MATCH (f1:iflow_flows) WHERE f1.source_component_id = start.component_id
                    OPTIONAL MATCH (direct1:iflow_components) WHERE direct1.component_id = f1.target_component_id
                    
                    OPTIONAL MATCH (f2:iflow_flows) WHERE f2.target_component_id = start.component_id
                    OPTIONAL MATCH (direct2:iflow_components) WHERE direct2.component_id = f2.source_component_id
                    
                    // Find components of the same type in the same package
                    OPTIONAL MATCH (similar:iflow_components) 
                    WHERE similar.component_type = start.component_type 
                    AND similar.package_name = start.package_name 
                    AND similar.component_id <> start.component_id
                    
                    WITH start, 
                         collect(DISTINCT {id: direct1.component_id, name: direct1.name, type: direct1.component_type, distance: 1, relation: 'outgoing'}) +
                         collect(DISTINCT {id: direct2.component_id, name: direct2.name, type: direct2.component_type, distance: 1, relation: 'incoming'}) +
                         collect(DISTINCT {id: similar.component_id, name: similar.name, type: similar.component_type, distance: 0, relation: 'similar_type'}) as related
                    
                    UNWIND related as rel
                    WHERE rel.id IS NOT NULL
                    RETURN DISTINCT rel.id as component_id, rel.name as name, rel.type as type, 
                           rel.distance as distance, rel.relation as relation_type
                    LIMIT 10
                """,
                name=component_name
                )
                
                related_components = []
                async for record in result:
                    related_components.append({
                        'component_id': record['component_id'],
                        'name': record['name'] or record['component_id'],
                        'type': record['type'],
                        'distance': record['distance'],
                        'relation_type': record['relation_type']
                    })
                
                return related_components
                
        except Exception as e:
            logger.error(f"Error finding related components: {e}")
            # Return empty list instead of raising to avoid breaking the flow
            return []

    # New methods for iFlow schema
    async def analyze_iflow_package(self, package_name: str) -> Dict[str, Any]:
        """Analyze a complete iFlow package with all its components and flows."""
        try:
            async with self.driver.session() as session:
                # Get process/folder info
                package_result = await session.run("""
                    MATCH (p:Process) 
                    WHERE p.name = $package_name OR p.id CONTAINS $package_name
                    RETURN p.id as id, p.name as name, p.type as type, p.folder_id as folder_id
                    LIMIT 1
                """, package_name=package_name)
                
                package_record = await package_result.single()
                if not package_record:
                    # Try with Folder nodes as well
                    package_result = await session.run("""
                        MATCH (f:Folder) 
                        WHERE f.name = $package_name OR f.id CONTAINS $package_name
                        RETURN f.id as id, f.name as name, f.type as type
                        LIMIT 1
                    """, package_name=package_name)
                    package_record = await package_result.single()
                    
                if not package_record:
                    return {"error": f"Package '{package_name}' not found"}
                
                folder_id = package_record['id']
                
                # Get components count by type
                components_result = await session.run("""
                    MATCH (c:Component) 
                    WHERE c.folder_id = $folder_id OR c.folder_id CONTAINS $package_name
                    RETURN c.type as type, count(c) as count
                    ORDER BY count DESC
                """, folder_id=folder_id, package_name=package_name)
                
                component_stats = {}
                total_components = 0
                async for record in components_result:
                    component_stats[record['type']] = record['count']
                    total_components += record['count']
                
                # Get flows count (relationships)
                flows_result = await session.run("""
                    MATCH (c:Component)-[r]->(target:Component)
                    WHERE c.folder_id = $folder_id OR c.folder_id CONTAINS $package_name
                    RETURN type(r) as rel_type, count(r) as count
                """, folder_id=folder_id, package_name=package_name)
                
                flow_stats = {}
                total_flows = 0
                async for record in flows_result:
                    flow_stats[record['rel_type']] = record['count']
                    total_flows += record['count']
                
                return {
                    "package": {
                        "id": package_record['id'],
                        "name": package_record['name'],
                        "type": package_record.get('type', 'Unknown')
                    },
                    "statistics": {
                        "total_components": total_components,
                        "total_flows": total_flows,
                        "component_types": component_stats,
                        "flow_types": flow_stats
                    }
                }
                
        except Exception as e:
            logger.error(f"Error analyzing iFlow package: {e}")
            return {"error": str(e)}
    
    async def get_flow_patterns(self, package_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Identify common flow patterns in iFlow packages."""
        try:
            async with self.driver.session() as session:
                # Find common component sequences
                where_clause = "WHERE f1.package_name = $package_name" if package_name else ""
                params = {"package_name": package_name} if package_name else {}
                
                result = await session.run(f"""
                    MATCH (f1:iflow_flows)-[:NEXT_FLOW*0..1]-(f2:iflow_flows)
                    {where_clause}
                    MATCH (c1:iflow_components {{component_id: f1.source_component_id}})
                    MATCH (c2:iflow_components {{component_id: f1.target_component_id}})
                    RETURN c1.component_type as source_type, c2.component_type as target_type,
                           f1.file_type as flow_type, count(*) as frequency
                    ORDER BY frequency DESC
                    LIMIT 10
                """, **params)
                
                patterns = []
                async for record in result:
                    patterns.append({
                        "pattern": f"{record['source_type']} -> {record['target_type']}",
                        "flow_type": record['flow_type'],
                        "frequency": record['frequency'],
                        "description": f"Common pattern: {record['source_type']} connected to {record['target_type']} via {record['flow_type']} flow"
                    })
                
                return patterns
                
        except Exception as e:
            logger.error(f"Error getting flow patterns: {e}")
            return []
