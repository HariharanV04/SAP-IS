"""
RAG Component Retrieval Logger
Logs all RAG retrieval operations with detailed component information
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class RAGLogger:
    """Logger for RAG component retrieval operations"""

    def __init__(self, service_name: str, log_dir: Optional[str] = None):
        """
        Initialize RAG logger

        Args:
            service_name: Name of the service (e.g., 'RAG_API', 'BoomiToIS', 'MuleToIS')
            log_dir: Optional custom log directory
        """
        self.service_name = service_name

        # Setup log directory
        if log_dir:
            self.log_dir = Path(log_dir)
        else:
            # Default: logs directory in project root
            self.log_dir = Path(__file__).parent.parent / "logs" / service_name.lower()

        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped log file for this session
        self.session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_file = self.log_dir / f"rag_retrieval_{self.session_timestamp}.log"
        self.json_log_file = self.log_dir / f"rag_retrieval_{self.session_timestamp}.json"

        # Initialize JSON log structure
        self.json_logs = {
            "session_id": self.session_timestamp,
            "service": service_name,
            "started_at": datetime.now().isoformat(),
            "retrievals": []
        }

        # Setup Python logging
        self.logger = logging.getLogger(f"RAGLogger.{service_name}")
        self.logger.setLevel(logging.DEBUG)

        # File handler
        fh = logging.FileHandler(self.log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.logger.info(f"="*80)
        self.logger.info(f"RAG Logger initialized for {service_name}")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info(f"JSON log: {self.json_log_file}")
        self.logger.info(f"="*80)

    def log_retrieval(self,
                      query: str,
                      results: List[Dict[str, Any]],
                      context: Optional[Dict[str, Any]] = None,
                      retrieval_type: str = "vector_search"):
        """
        Log a RAG retrieval operation

        Args:
            query: The search query used
            results: List of retrieved components/documents
            context: Optional additional context (component type, job_id, etc.)
            retrieval_type: Type of retrieval (vector_search, graph_query, hybrid)
        """
        timestamp = datetime.now().isoformat()

        # Extract key information from results
        components_info = []
        for idx, result in enumerate(results):
            component_info = {
                "rank": idx + 1,
                "id": result.get('id', 'unknown'),
                "document_name": result.get('document_name', 'unknown'),
                "chunk_type": result.get('chunk_type', 'unknown'),
                "component_type": result.get('component_type', 'unknown'),
                "similarity_score": result.get('similarity', result.get('score', 0)),
                "metadata": {
                    "iflow_id": result.get('iflow_id', 'N/A'),
                    "component_id": result.get('component_id', 'N/A'),
                    "artifact_name": result.get('artifact_name', 'N/A'),
                    "description": result.get('description', 'N/A')[:200]  # Limit description length
                },
                "content_preview": result.get('content', '')[:300]  # First 300 chars
            }
            components_info.append(component_info)

        # Log to text file
        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info(f"RAG RETRIEVAL - {retrieval_type}")
        self.logger.info(f"Timestamp: {timestamp}")
        if context:
            self.logger.info(f"Context: {json.dumps(context, indent=2)}")
        self.logger.info(f"Query: {query}")
        self.logger.info(f"Results: {len(results)} components retrieved")
        self.logger.info("-"*80)

        for comp in components_info:
            self.logger.info(f"  [{comp['rank']}] {comp['component_type']} - {comp['document_name']}")
            self.logger.info(f"      ID: {comp['id']}")
            self.logger.info(f"      Chunk Type: {comp['chunk_type']}")
            self.logger.info(f"      Similarity: {comp['similarity_score']:.4f}")
            self.logger.info(f"      iFlow ID: {comp['metadata']['iflow_id']}")
            self.logger.info(f"      Component ID: {comp['metadata']['component_id']}")
            if comp['metadata']['description'] != 'N/A':
                self.logger.info(f"      Description: {comp['metadata']['description']}")

        self.logger.info("="*80)

        # Add to JSON log
        retrieval_entry = {
            "timestamp": timestamp,
            "retrieval_type": retrieval_type,
            "query": query,
            "context": context or {},
            "num_results": len(results),
            "components": components_info
        }

        self.json_logs["retrievals"].append(retrieval_entry)

        # Save JSON log after each retrieval (for real-time debugging)
        self._save_json_log()

    def log_component_selection(self,
                                 selected_components: List[Dict[str, Any]],
                                 reason: str,
                                 context: Optional[Dict[str, Any]] = None):
        """
        Log when components are selected for iFlow generation

        Args:
            selected_components: List of components chosen for generation
            reason: Reason for selection
            context: Optional context
        """
        timestamp = datetime.now().isoformat()

        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info("COMPONENT SELECTION")
        self.logger.info(f"Timestamp: {timestamp}")
        self.logger.info(f"Reason: {reason}")
        if context:
            self.logger.info(f"Context: {json.dumps(context, indent=2)}")
        self.logger.info(f"Selected: {len(selected_components)} components")
        self.logger.info("-"*80)

        for idx, comp in enumerate(selected_components):
            self.logger.info(f"  [{idx+1}] {comp.get('type', 'unknown')}")
            self.logger.info(f"      Name: {comp.get('name', 'N/A')}")
            self.logger.info(f"      ID: {comp.get('id', 'N/A')}")
            self.logger.info(f"      Source: {comp.get('source', 'N/A')}")

        self.logger.info("="*80)

        # Add to JSON log
        selection_entry = {
            "timestamp": timestamp,
            "type": "component_selection",
            "reason": reason,
            "context": context or {},
            "selected_components": selected_components
        }

        self.json_logs["retrievals"].append(selection_entry)
        self._save_json_log()

    def log_generation_result(self,
                              iflow_name: str,
                              components_used: List[Dict[str, Any]],
                              success: bool,
                              error: Optional[str] = None):
        """
        Log the final iFlow generation result

        Args:
            iflow_name: Name of generated iFlow
            components_used: List of components used in generation
            success: Whether generation succeeded
            error: Error message if failed
        """
        timestamp = datetime.now().isoformat()

        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info("IFLOW GENERATION RESULT")
        self.logger.info(f"Timestamp: {timestamp}")
        self.logger.info(f"iFlow Name: {iflow_name}")
        self.logger.info(f"Status: {'SUCCESS' if success else 'FAILED'}")
        if error:
            self.logger.error(f"Error: {error}")
        self.logger.info(f"Components Used: {len(components_used)}")
        self.logger.info("-"*80)

        for idx, comp in enumerate(components_used):
            self.logger.info(f"  [{idx+1}] {comp.get('type', 'unknown')}")
            self.logger.info(f"      ID: {comp.get('id', 'N/A')}")

        self.logger.info("="*80)

        # Add to JSON log
        result_entry = {
            "timestamp": timestamp,
            "type": "generation_result",
            "iflow_name": iflow_name,
            "success": success,
            "error": error,
            "components_used": components_used
        }

        self.json_logs["retrievals"].append(result_entry)
        self.json_logs["completed_at"] = timestamp
        self._save_json_log()

    def _save_json_log(self):
        """Save JSON log to file"""
        try:
            with open(self.json_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.json_logs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save JSON log: {e}")

    def get_log_files(self) -> Dict[str, str]:
        """Get paths to log files"""
        return {
            "text_log": str(self.log_file),
            "json_log": str(self.json_log_file)
        }


# Global logger instances for each service
_loggers: Dict[str, RAGLogger] = {}


def get_rag_logger(service_name: str, log_dir: Optional[str] = None) -> RAGLogger:
    """
    Get or create a RAG logger for a service

    Args:
        service_name: Name of the service
        log_dir: Optional custom log directory

    Returns:
        RAGLogger instance
    """
    if service_name not in _loggers:
        _loggers[service_name] = RAGLogger(service_name, log_dir)
    return _loggers[service_name]
