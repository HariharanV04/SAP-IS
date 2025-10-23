"""
Neo4j-based similarity search for finding reference iFlows.

This module provides functionality to search the Neo4j knowledge graph for iFlows
that are similar to a given requirement, which can then be used as references
for building new iFlows.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
import asyncio

logger = logging.getLogger(__name__)


class IFlowSimilaritySearch:
    """
    Search for similar iFlows in Neo4j knowledge graph to use as references.

    This class analyzes user requirements and finds iFlows with similar:
    - Component types (HTTP, SFTP, OData, etc.)
    - Integration patterns (request-reply, publish-subscribe, etc.)
    - Data transformation steps
    - Protocol combinations
    """

    def __init__(self, graph_store):
        """
        Initialize similarity search.

        Args:
            graph_store: Neo4j GraphStore instance
        """
        self.graph_store = graph_store

        # Component type keywords mapping
        self.component_keywords = {
            'http': ['http', 'rest', 'api', 'endpoint', 'webhook'],
            'sftp': ['sftp', 'ftp', 'file', 'transfer'],
            'odata': ['odata', 'open data protocol'],
            'soap': ['soap', 'web service', 'wsdl'],
            'jdbc': ['jdbc', 'database', 'sql', 'db'],
            'mail': ['email', 'mail', 'smtp', 'imap'],
            'amqp': ['amqp', 'message queue', 'rabbitmq'],
            'jms': ['jms', 'java message', 'activemq'],
            'idoc': ['idoc', 'sap idoc'],
            'successfactors': ['successfactors', 'sf', 'sfsf'],
            'ariba': ['ariba', 'procurement'],
            's3': ['s3', 'amazon s3', 'aws storage'],
            'kafka': ['kafka', 'event streaming'],
            'json': ['json', 'javascript object'],
            'xml': ['xml', 'extensible markup'],
            'csv': ['csv', 'comma separated']
        }

        # Integration pattern keywords
        self.pattern_keywords = {
            'request_reply': ['request', 'reply', 'synchronous', 'sync'],
            'publish_subscribe': ['publish', 'subscribe', 'pub-sub', 'event'],
            'content_enrichment': ['enrich', 'enrichment', 'augment', 'enhance'],
            'content_filter': ['filter', 'filtering', 'condition', 'conditional'],
            'splitter': ['split', 'splitter', 'divide', 'separate'],
            'aggregator': ['aggregate', 'aggregator', 'combine', 'merge'],
            'router': ['route', 'router', 'routing', 'switch'],
            'transformer': ['transform', 'transformation', 'convert', 'map', 'mapping']
        }

    def extract_requirement_features(self, requirement: str) -> Dict[str, Any]:
        """
        Extract key features from user requirement text.

        Args:
            requirement: User requirement description

        Returns:
            Dictionary with extracted features
        """
        req_lower = requirement.lower()

        # Extract component types
        detected_components = []
        for comp_type, keywords in self.component_keywords.items():
            if any(keyword in req_lower for keyword in keywords):
                detected_components.append(comp_type)

        # Extract integration patterns
        detected_patterns = []
        for pattern, keywords in self.pattern_keywords.items():
            if any(keyword in req_lower for keyword in keywords):
                detected_patterns.append(pattern)

        # Extract data formats
        data_formats = []
        for format_type in ['json', 'xml', 'csv']:
            if format_type in req_lower:
                data_formats.append(format_type)

        # Extract operations (verbs)
        operations = []
        operation_verbs = ['create', 'read', 'update', 'delete', 'get', 'post',
                          'put', 'delete', 'send', 'receive', 'fetch', 'retrieve',
                          'process', 'transform', 'validate']
        for verb in operation_verbs:
            if verb in req_lower:
                operations.append(verb)

        logger.info(f"Extracted features from requirement:")
        logger.info(f"  Components: {detected_components}")
        logger.info(f"  Patterns: {detected_patterns}")
        logger.info(f"  Data formats: {data_formats}")
        logger.info(f"  Operations: {operations}")

        return {
            'components': detected_components,
            'patterns': detected_patterns,
            'data_formats': data_formats,
            'operations': operations,
            'raw_text': requirement
        }

    async def find_similar_iflows(
        self,
        requirement: str,
        limit: int = 5,
        min_similarity_score: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Find iFlows similar to the given requirement.

        Args:
            requirement: User requirement description
            limit: Maximum number of similar iFlows to return
            min_similarity_score: Minimum similarity score (0-1)

        Returns:
            List of similar iFlows with similarity scores and details
        """
        logger.info(f"Searching for iFlows similar to: {requirement[:100]}...")

        # Extract features from requirement
        features = self.extract_requirement_features(requirement)

        if not features['components'] and not features['patterns']:
            logger.warning("No components or patterns detected in requirement")
            return []

        # Search Neo4j for matching iFlows
        similar_iflows = await self._search_neo4j_by_features(features, limit * 3)

        # Calculate similarity scores
        scored_iflows = []
        for iflow in similar_iflows:
            score = self._calculate_similarity_score(features, iflow)
            if score >= min_similarity_score:
                iflow['similarity_score'] = score
                scored_iflows.append(iflow)

        # Sort by similarity score and return top results
        scored_iflows.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_results = scored_iflows[:limit]

        logger.info(f"Found {len(top_results)} similar iFlows with score >= {min_similarity_score}")
        for i, iflow in enumerate(top_results, 1):
            logger.info(f"  {i}. {iflow.get('name', 'Unknown')} (score: {iflow['similarity_score']:.3f})")

        return top_results

    async def _search_neo4j_by_features(
        self,
        features: Dict[str, Any],
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Search Neo4j for iFlows matching the extracted features.

        Args:
            features: Extracted features from requirement
            limit: Maximum number of results

        Returns:
            List of matching iFlows with their component details
        """
        try:
            async with self.graph_store.driver.session() as session:
                # Build dynamic Cypher query based on detected components
                component_conditions = []
                for comp in features['components']:
                    # Search for components containing these keywords
                    component_conditions.append(f"toLower(c.type) CONTAINS '{comp}'")
                    component_conditions.append(f"toLower(c.name) CONTAINS '{comp}'")

                # If no specific components, search broadly
                if not component_conditions:
                    component_conditions = ["1=1"]  # Match all

                # Create OR condition for components
                component_where = " OR ".join(component_conditions)

                query = f"""
                    MATCH (p:Process)-[:CONTAINS]->(c:Component)
                    WHERE {component_where}
                    WITH p, c
                    MATCH (p)-[:CONTAINS]->(all_c:Component)
                    OPTIONAL MATCH (all_c)-[r]->(target:Component)
                    WHERE (p)-[:CONTAINS]->(target)

                    WITH p,
                         collect(DISTINCT {{
                             id: all_c.id,
                             name: all_c.name,
                             type: all_c.type
                         }}) as components,
                         collect(DISTINCT {{
                             from: all_c.id,
                             to: target.id,
                             type: type(r)
                         }}) as connections

                    RETURN p.id as package_id,
                           p.name as package_name,
                           p.folder_id as folder_id,
                           components,
                           connections,
                           size(components) as component_count
                    ORDER BY component_count DESC
                    LIMIT $limit
                """

                result = await session.run(query, limit=limit)

                iflows = []
                async for record in result:
                    # Filter out null connections
                    connections = [c for c in record['connections'] if c['from'] and c['to']]
                    components = [c for c in record['components'] if c['id']]

                    iflows.append({
                        'package_id': record['package_id'],
                        'name': record['package_name'] or record['package_id'],
                        'folder_id': record['folder_id'],
                        'components': components,
                        'connections': connections,
                        'component_count': record['component_count']
                    })

                logger.info(f"Neo4j search returned {len(iflows)} candidate iFlows")
                return iflows

        except Exception as e:
            logger.error(f"Error searching Neo4j: {e}")
            return []

    def _calculate_similarity_score(
        self,
        features: Dict[str, Any],
        iflow: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity score between requirement features and an iFlow.

        Args:
            features: Extracted features from requirement
            iflow: iFlow data from Neo4j

        Returns:
            Similarity score (0-1)
        """
        score = 0.0
        weights = {
            'component_match': 0.4,
            'pattern_match': 0.3,
            'structure_similarity': 0.2,
            'complexity_match': 0.1
        }

        # Extract component types from iFlow
        iflow_components = set()
        for comp in iflow.get('components', []):
            comp_type = comp.get('type', '').lower()
            iflow_components.add(comp_type)

        # 1. Component matching (40% weight)
        required_components = set(features['components'])
        if required_components and iflow_components:
            # Calculate Jaccard similarity
            intersection = len(required_components & iflow_components)
            union = len(required_components | iflow_components)
            component_score = intersection / union if union > 0 else 0
            score += component_score * weights['component_match']

        # 2. Pattern matching (30% weight)
        # Check if iFlow structure suggests similar patterns
        pattern_score = self._check_pattern_match(features['patterns'], iflow)
        score += pattern_score * weights['pattern_match']

        # 3. Structure similarity (20% weight)
        # Compare complexity (number of components, connections)
        structure_score = self._calculate_structure_similarity(features, iflow)
        score += structure_score * weights['structure_similarity']

        # 4. Complexity match (10% weight)
        # Prefer iFlows of similar complexity
        complexity_score = self._calculate_complexity_match(features, iflow)
        score += complexity_score * weights['complexity_match']

        return min(score, 1.0)  # Cap at 1.0

    def _check_pattern_match(self, patterns: List[str], iflow: Dict[str, Any]) -> float:
        """
        Check if iFlow structure matches required patterns.

        Args:
            patterns: Required patterns
            iflow: iFlow data

        Returns:
            Pattern match score (0-1)
        """
        if not patterns:
            return 0.5  # Neutral score if no specific patterns required

        score = 0.0
        components = iflow.get('components', [])
        connections = iflow.get('connections', [])

        # Analyze iFlow structure for pattern indicators
        component_types = [c.get('type', '').lower() for c in components]

        for pattern in patterns:
            if pattern == 'request_reply':
                # Look for start/end events with processing in between
                has_start = any('start' in ct for ct in component_types)
                has_end = any('end' in ct for ct in component_types)
                if has_start and has_end and len(connections) > 0:
                    score += 1.0

            elif pattern == 'splitter':
                # Look for gateway components
                has_gateway = any('gateway' in ct for ct in component_types)
                if has_gateway:
                    score += 1.0

            elif pattern == 'transformer':
                # Look for mapping/transform components
                has_transform = any(any(kw in ct for kw in ['map', 'transform', 'convert'])
                                   for ct in component_types)
                if has_transform:
                    score += 1.0

            elif pattern == 'router':
                # Look for routing logic
                has_router = any('router' in ct or 'gateway' in ct for ct in component_types)
                if has_router:
                    score += 1.0

        return min(score / len(patterns), 1.0) if patterns else 0.5

    def _calculate_structure_similarity(
        self,
        features: Dict[str, Any],
        iflow: Dict[str, Any]
    ) -> float:
        """
        Calculate structural similarity based on complexity.

        Args:
            features: Requirement features
            iflow: iFlow data

        Returns:
            Structure similarity score (0-1)
        """
        # Estimate expected complexity from features
        expected_components = len(features['components']) * 3  # Rough estimate
        expected_components += len(features['patterns']) * 2
        expected_components = max(expected_components, 5)  # Minimum

        actual_components = iflow.get('component_count', len(iflow.get('components', [])))

        # Calculate similarity (closer = higher score)
        if actual_components == 0:
            return 0.0

        ratio = min(expected_components, actual_components) / max(expected_components, actual_components)
        return ratio

    def _calculate_complexity_match(
        self,
        features: Dict[str, Any],
        iflow: Dict[str, Any]
    ) -> float:
        """
        Calculate complexity matching score.

        Args:
            features: Requirement features
            iflow: iFlow data

        Returns:
            Complexity match score (0-1)
        """
        # Simple heuristic: prefer iFlows with moderate complexity
        component_count = iflow.get('component_count', 0)
        connection_count = len(iflow.get('connections', []))

        # Optimal range: 5-20 components, with good connectivity
        if 5 <= component_count <= 20 and connection_count > 0:
            return 1.0
        elif component_count < 5:
            return 0.5
        else:
            # Penalize overly complex iFlows
            return max(0.3, 1.0 - (component_count - 20) / 50)

    async def get_iflow_reference_details(
        self,
        package_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed reference information for a specific iFlow.

        Args:
            package_id: iFlow package ID

        Returns:
            Detailed iFlow information including full topology
        """
        try:
            # Use existing graph_store method to get skeleton
            skeleton = await self.graph_store.get_iflow_skeleton(package_id)

            if not skeleton or not skeleton.get('nodes'):
                logger.warning(f"No skeleton found for package: {package_id}")
                return None

            # Get package analysis
            analysis = await self.graph_store.analyze_iflow_package(package_id)

            return {
                'package_id': package_id,
                'topology': skeleton,
                'analysis': analysis,
                'nodes': skeleton.get('nodes', []),
                'edges': skeleton.get('edges', [])
            }

        except Exception as e:
            logger.error(f"Error getting iFlow reference details: {e}")
            return None

    async def get_reference_iflows_for_generation(
        self,
        requirement: str,
        max_references: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get reference iFlows for generation, with full details.

        This is the main method to call when generating new iFlows.

        Args:
            requirement: User requirement description
            max_references: Maximum number of reference iFlows to return

        Returns:
            List of reference iFlows with full topology and analysis
        """
        logger.info(f"Getting reference iFlows for requirement...")

        # Find similar iFlows
        similar_iflows = await self.find_similar_iflows(
            requirement=requirement,
            limit=max_references,
            min_similarity_score=0.3
        )

        if not similar_iflows:
            logger.warning("No similar iFlows found")
            return []

        # Get detailed information for each
        reference_iflows = []
        for iflow in similar_iflows:
            details = await self.get_iflow_reference_details(iflow['package_id'])
            if details:
                details['similarity_score'] = iflow['similarity_score']
                details['name'] = iflow['name']
                reference_iflows.append(details)

        logger.info(f"Retrieved {len(reference_iflows)} reference iFlows with full details")
        return reference_iflows


# Convenience function
async def find_reference_iflows(
    graph_store,
    requirement: str,
    max_references: int = 3
) -> List[Dict[str, Any]]:
    """
    Convenience function to find reference iFlows.

    Args:
        graph_store: Neo4j GraphStore instance
        requirement: User requirement description
        max_references: Maximum number of references to return

    Returns:
        List of reference iFlows with full details
    """
    search = IFlowSimilaritySearch(graph_store)
    return await search.get_reference_iflows_for_generation(requirement, max_references)
