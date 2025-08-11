from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query or SQL")
    query_type: str = Field(default="natural", description="Type of query: 'natural' or 'sql'")
    limit: Optional[int] = Field(default=None, description="Maximum number of rows to return")
    database_type: Optional[str] = Field(default=None, description="Override default database type")


class QueryResponse(BaseModel):
    success: bool
    query_id: Optional[str] = None
    generated_sql: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    insights: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    row_count: Optional[int] = None


class SchemaRequest(BaseModel):
    table_name: Optional[str] = Field(default=None, description="Specific table to get schema for")
    include_relationships: bool = Field(default=True, description="Include foreign key relationships")


class SchemaResponse(BaseModel):
    success: bool
    schema: Optional[Dict[str, Any]] = None
    relationships: Optional[List[Dict[str, str]]] = None
    error: Optional[str] = None


class TableInfo(BaseModel):
    name: str
    columns: List[Dict[str, Any]]
    row_count: Optional[int] = None
    table_type: Optional[str] = None
    size_bytes: Optional[int] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None


class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_keys: List[str] = []
    description: Optional[str] = None


class DatabaseConnection(BaseModel):
    type: str = Field(..., description="Database type: postgres, bigquery, snowflake, redshift")
    config: Dict[str, Any] = Field(..., description="Database connection configuration")
    name: Optional[str] = Field(default=None, description="Connection name")


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    query_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatSession(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class RAGDocument(BaseModel):
    id: str
    title: str
    content: str
    document_type: str = Field(..., description="Type: 'schema', 'metric', 'governance'")
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None


class QueryPlan(BaseModel):
    query: str
    plan: str
    estimated_cost: Optional[Dict[str, Any]] = None
    optimizations: Optional[List[str]] = None


class QueryValidation(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    safety_issues: Optional[List[str]] = None
    suggested_fixes: Optional[List[str]] = None


class ExportRequest(BaseModel):
    query_id: str
    format: str = Field(..., description="Export format: 'csv', 'excel', 'json'")
    filename: Optional[str] = None


class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    database_connection: bool
    vector_store_connection: bool
    ai_service: bool


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Enum for supported database types
class DatabaseType(str, Enum):
    POSTGRES = "postgres"
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    REDSHIFT = "redshift"


# Enum for query types
class QueryType(str, Enum):
    NATURAL = "natural"
    SQL = "sql"


# Enum for document types for RAG
class DocumentType(str, Enum):
    SCHEMA = "schema"
    METRIC = "metric"
    GOVERNANCE = "governance"
    DOCUMENTATION = "documentation"