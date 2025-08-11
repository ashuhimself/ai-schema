# Warehouse Copilot

An AI-powered application that connects to relational databases and data warehouses, providing conversational querying, data analysis, and schema exploration through a web-based interface.

## Features

- **Multi-Database Support**: BigQuery, Snowflake, Redshift, PostgreSQL
- **AI-Powered Querying**: Natural language to SQL using Google Gemini
- **RAG Integration**: Grounded answers using schema and documentation
- **Interactive Schema Explorer**: Visual relationship graphs
- **Real-time Chat Interface**: Conversational data analysis
- **SQL Editor**: Direct query execution with syntax highlighting
- **Security & Governance**: Row/column-level security, query logging

## Quick Start

```bash
# Clone and start with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:3000
```

## Architecture

- **Frontend**: React + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + Python
- **AI Layer**: Google Gemini + LangChain + RAG
- **Vector Store**: pgvector for RAG embeddings
- **Databases**: Configurable connectors for major data warehouses

## Environment Configuration

Copy `.env.example` to `.env` and configure your database connections and API keys.

## Development

See individual service README files:
- [Backend Documentation](./backend/README.md)
- [Frontend Documentation](./frontend/README.md)