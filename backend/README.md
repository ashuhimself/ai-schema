# Warehouse Copilot Backend

FastAPI backend service for the Warehouse Copilot application.

## Features

- **Multi-Database Support**: Connects to PostgreSQL, BigQuery, Snowflake, and Redshift
- **AI Integration**: Uses Google Gemini with LangChain for natural language to SQL conversion
- **RAG Pipeline**: Retrieval Augmented Generation with pgvector for contextual responses
- **Query Safety**: Validates and sanitizes SQL queries before execution
- **Real-time Chat**: WebSocket support for conversational interfaces
- **Query Logging**: Comprehensive logging and analytics

## Architecture

```
app/
├── api/              # API routes and endpoints
├── connectors/       # Database connector implementations
├── models/           # Pydantic models and database schemas
├── services/         # Business logic services
└── main.py          # FastAPI application entry point
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database Configuration
DATABASE_TYPE=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=warehouse
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# AI Configuration
GOOGLE_API_KEY=your-gemini-api-key

# Security
SECRET_KEY=your-secret-key-here
```

## API Endpoints

### Query Execution
- `POST /api/query/execute` - Execute natural language or SQL queries
- `POST /api/query/validate` - Validate query syntax
- `POST /api/query/plan` - Get query execution plan
- `GET /api/query/history` - Get query history

### Schema Exploration
- `POST /api/schema/` - Get database schema
- `GET /api/schema/tables` - List all tables
- `GET /api/schema/tables/{table_name}` - Get table details
- `GET /api/schema/graph` - Get schema as graph for visualization

### Chat Interface
- `POST /api/chat/sessions` - Create chat session
- `POST /api/chat/sessions/{id}/messages` - Send message
- `WS /api/chat/sessions/{id}/ws` - WebSocket for real-time chat

## Database Connectors

### PostgreSQL
```python
from app.connectors.factory import ConnectorFactory

connector = ConnectorFactory.create_connector('postgres', {
    'host': 'localhost',
    'port': 5432,
    'database': 'mydb',
    'user': 'user',
    'password': 'password'
})
```

### BigQuery
```python
connector = ConnectorFactory.create_connector('bigquery', {
    'project_id': 'my-project',
    'credentials_path': '/path/to/credentials.json'
})
```

### Snowflake
```python
connector = ConnectorFactory.create_connector('snowflake', {
    'account': 'your-account',
    'user': 'username',
    'password': 'password',
    'database': 'database',
    'warehouse': 'warehouse'
})
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest

# Format code
black app/
isort app/
```

## Security Features

- **Query Validation**: Only SELECT statements allowed by default
- **SQL Injection Protection**: Parameterized queries and validation
- **Rate Limiting**: Configurable request limits
- **CORS**: Configurable cross-origin resource sharing
- **Authentication**: JWT-based authentication (optional)

## Performance Optimizations

- **Connection Pooling**: Efficient database connection management
- **Query Caching**: Cache frequently executed queries
- **Result Pagination**: Large result sets are paginated
- **Query Timeouts**: Configurable execution timeouts

## Monitoring

- Health check endpoint: `GET /health`
- Structured logging with configurable levels
- Query execution metrics
- Error tracking and reporting