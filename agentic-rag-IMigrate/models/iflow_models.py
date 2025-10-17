"""
SAP iFlow data models for the RAG + Knowledge Graph system.
"""

from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ComponentType(str, Enum):
    """SAP iFlow component types."""
    SFTP = "SFTP"
    ODATA = "OData"
    GROOVY = "GroovyScript"
    CONTENT_MODIFIER = "ContentModifier"
    REQUEST_REPLY = "RequestReply"
    SPLITTER = "Splitter"
    AGGREGATOR = "Aggregator"
    ROUTER = "Router"
    CONTENT_ENRICHER = "ContentEnricher"
    MESSAGE_MAPPING = "MessageMapping"
    LOCAL_INTEGRATION_PROCESS = "LocalIntegrationProcess"
    EXTERNAL_CALL = "ExternalCall"
    MAIL = "Mail"
    HTTP = "HTTP"
    REST = "REST"
    SOAP = "SOAP"
    JMS = "JMS"
    IDOC = "IDoc"
    EDI = "EDI"
    CACHE = "Cache"
    SECURITY = "Security"
    UNKNOWN = "Unknown"


class PatternType(str, Enum):
    """Integration pattern types."""
    REQUEST_REPLY = "Request-Reply"
    FIRE_AND_FORGET = "Fire-and-Forget"
    EVENT_DRIVEN = "Event-Driven"
    BATCH_PROCESSING = "Batch Processing"
    REAL_TIME_SYNC = "Real-time Sync"
    ASYNC_PROCESSING = "Async Processing"
    ERROR_HANDLING = "Error Handling"
    DATA_TRANSFORMATION = "Data Transformation"
    ROUTING = "Routing"
    AGGREGATION = "Aggregation"


class ConnectionType(str, Enum):
    """Connection types between components."""
    SEQUENCE = "sequence"
    MESSAGE = "message"
    ERROR = "error"
    TIMEOUT = "timeout"
    CONDITIONAL = "conditional"


class SAPComponent(BaseModel):
    """SAP iFlow component model."""
    id: Optional[str] = None
    component_type: ComponentType
    component_name: str
    configuration: Dict[str, Any] = Field(default_factory=dict)
    position_x: Optional[int] = None
    position_y: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(use_enum_values=True)


class Connection(BaseModel):
    """Connection between iFlow components."""
    id: Optional[str] = None
    from_component: str
    to_component: str
    connection_type: ConnectionType
    condition: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(use_enum_values=True)


class IntegrationPattern(BaseModel):
    """Integration pattern model."""
    id: Optional[str] = None
    pattern_name: str
    pattern_type: PatternType
    description: str
    components: List[SAPComponent] = Field(default_factory=list)
    connections: List[Connection] = Field(default_factory=list)
    complexity_score: float = Field(ge=0.0, le=10.0)
    success_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    usage_count: int = Field(ge=0, default=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(use_enum_values=True)


class SAPiFlowDocument(BaseModel):
    """SAP iFlow document model."""
    id: Optional[str] = None
    name: str
    package_name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    xml_content: str
    components: List[SAPComponent] = Field(default_factory=list)
    connections: List[Connection] = Field(default_factory=list)
    patterns: List[IntegrationPattern] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PatternChunk(BaseModel):
    """Pattern chunk for vector search."""
    id: Optional[str] = None
    pattern_id: str
    content: str
    embedding: Optional[List[float]] = None
    chunk_type: Literal["description", "components", "connections", "configuration"] = "description"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class ComponentRecommendation(BaseModel):
    """Component recommendation model."""
    component_type: ComponentType
    component_name: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    
    model_config = ConfigDict(use_enum_values=True)


class iFlowGenerationRequest(BaseModel):
    """Request model for iFlow generation."""
    requirements: str
    source_system: Optional[str] = None
    target_system: Optional[str] = None
    data_format: Optional[str] = None
    pattern_type: Optional[PatternType] = None
    complexity: Literal["low", "medium", "high"] = "medium"
    include_error_handling: bool = True
    include_monitoring: bool = True
    
    model_config = ConfigDict(use_enum_values=True)


class iFlowValidationResult(BaseModel):
    """iFlow validation result model."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)
    complexity_score: float = Field(ge=0.0, le=10.0)
    performance_score: float = Field(ge=0.0, le=10.0)
    security_score: float = Field(ge=0.0, le=10.0)


class PatternSearchResult(BaseModel):
    """Pattern search result model."""
    pattern: IntegrationPattern
    similarity_score: float = Field(ge=0.0, le=1.0)
    match_reason: str
    usage_examples: List[str] = Field(default_factory=list)


class iFlowAnalysisResult(BaseModel):
    """iFlow analysis result model."""
    iflow: SAPiFlowDocument
    patterns_found: List[IntegrationPattern] = Field(default_factory=list)
    complexity_analysis: Dict[str, Any] = Field(default_factory=dict)
    optimization_suggestions: List[str] = Field(default_factory=list)
    best_practices_compliance: Dict[str, bool] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
