-- Initialize pgvector extension and create vector tables
\c vector_store;
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for storing document embeddings for RAG
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    document_type VARCHAR(50) NOT NULL, -- 'schema', 'metric', 'governance'
    title VARCHAR(500),
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- Adjust dimension based on embedding model
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on embeddings for fast similarity search
CREATE INDEX ON document_embeddings USING hnsw (embedding vector_cosine_ops);

-- Create table for query logging and metadata (in vector_store)
CREATE TABLE IF NOT EXISTS query_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    query_text TEXT NOT NULL,
    query_type VARCHAR(50),
    execution_time_ms INTEGER,
    row_count INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for schema metadata
CREATE TABLE IF NOT EXISTS schema_metadata (
    id SERIAL PRIMARY KEY,
    database_name VARCHAR(255),
    schema_name VARCHAR(255),
    table_name VARCHAR(255) NOT NULL,
    column_name VARCHAR(255),
    data_type VARCHAR(100),
    description TEXT,
    is_pii BOOLEAN DEFAULT FALSE,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(database_name, schema_name, table_name, column_name)
);