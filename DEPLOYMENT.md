# Deployment Guide

This guide covers deploying Warehouse Copilot in various environments.

## Quick Start (Local Development)

```bash
# 1. Clone the repository
git clone <repository-url>
cd ai-schema

# 2. Set up environment
cp .env.example .env
# Edit .env with your configuration

# 3. Start with Docker Compose
make dev

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

## Production Deployment

### Prerequisites

- Docker and Docker Compose
- Domain name (optional)
- SSL certificates (for HTTPS)
- Database credentials
- Google Gemini API key

### Environment Configuration

Create and configure your `.env` file:

```bash
# Database - Choose one
DATABASE_TYPE=postgres  # postgres, bigquery, snowflake, redshift

# PostgreSQL
POSTGRES_HOST=your-postgres-host
POSTGRES_PORT=5432
POSTGRES_DB=warehouse
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-secure-password

# BigQuery
BIGQUERY_PROJECT_ID=your-project-id
BIGQUERY_CREDENTIALS_PATH=/app/credentials/bigquery.json

# Snowflake
SNOWFLAKE_ACCOUNT=your-account
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_DATABASE=your-database
SNOWFLAKE_WAREHOUSE=your-warehouse

# Redshift
REDSHIFT_HOST=your-cluster.redshift.amazonaws.com
REDSHIFT_PORT=5439
REDSHIFT_DB=dev
REDSHIFT_USER=your-username
REDSHIFT_PASSWORD=your-password

# AI Configuration (Required)
GOOGLE_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-pro

# Security (Important!)
SECRET_KEY=generate-a-strong-random-key-here
ALLOWED_ORIGINS=https://your-domain.com,http://localhost:3000

# Production Settings
LOG_LEVEL=INFO
MAX_QUERY_ROWS=10000
QUERY_TIMEOUT_SECONDS=300
```

### Docker Deployment

1. **Build and start services:**
```bash
make prod
```

2. **Check service health:**
```bash
make health
```

3. **View logs:**
```bash
make logs
```

### Reverse Proxy Setup (Nginx)

For production deployment with custom domain:

```nginx
# /etc/nginx/sites-available/warehouse-copilot
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support for chat
    location /api/chat/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Cloud Deployment

### AWS Deployment

1. **Using EC2 with Docker:**
```bash
# Launch EC2 instance (Ubuntu 22.04)
# Install Docker and Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu

# Deploy application
git clone <repository-url>
cd ai-schema
cp .env.example .env
# Configure .env
make prod
```

2. **Using ECS (Elastic Container Service):**
- Build and push images to ECR
- Create ECS cluster and task definitions
- Configure load balancer and security groups

3. **Using EKS (Kubernetes):**
- Create Kubernetes manifests
- Deploy with kubectl or Helm

### Google Cloud Platform

1. **Using Compute Engine:**
- Similar to AWS EC2 deployment
- Use Cloud SQL for PostgreSQL
- Store credentials in Secret Manager

2. **Using Cloud Run:**
- Build container images
- Deploy frontend and backend separately
- Configure environment variables

### Azure Deployment

1. **Using Container Instances:**
- Deploy with Azure Container Instances
- Use Azure Database for PostgreSQL
- Store secrets in Key Vault

## Database Setup

### PostgreSQL (Recommended for development)
```bash
# Create database and user
createdb warehouse
createuser warehouse_user
```

### BigQuery Setup
1. Create GCP project
2. Enable BigQuery API
3. Create service account with BigQuery permissions
4. Download credentials JSON file

### Snowflake Setup
1. Create Snowflake account
2. Set up warehouse and database
3. Configure user permissions

### Redshift Setup
1. Create Redshift cluster
2. Configure VPC and security groups
3. Create database and user

## Monitoring and Logging

### Application Logs
```bash
# View logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Health Monitoring
- Health endpoint: `GET /health`
- Monitor database connections
- Track query execution times
- Alert on failures

### Metrics Collection
Consider integrating:
- Prometheus for metrics
- Grafana for dashboards
- ELK stack for log analysis

## Backup and Recovery

### Database Backups
```bash
# PostgreSQL backup
pg_dump warehouse > backup.sql

# Restore
psql warehouse < backup.sql
```

### Application Data
- Query history and logs are stored in PostgreSQL
- Vector embeddings for RAG are in pgvector
- Regular backups recommended

## Security Considerations

### Network Security
- Use HTTPS in production
- Configure firewall rules
- Limit database access to application only

### Application Security
- Keep SECRET_KEY secure and unique
- Use environment variables for sensitive data
- Regular security updates
- Monitor for vulnerabilities

### Database Security
- Use strong passwords
- Enable SSL connections
- Regular security patches
- Audit database access

## Performance Optimization

### Database Performance
- Create appropriate indexes
- Monitor query performance
- Use connection pooling
- Regular VACUUM/ANALYZE (PostgreSQL)

### Application Performance
- Enable caching where appropriate
- Monitor memory usage
- Optimize Docker images
- Use CDN for static assets

### Scaling
- Horizontal scaling with load balancer
- Database read replicas
- Redis for session management
- Container orchestration (Kubernetes)

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check credentials in .env
   - Verify database is running
   - Check network connectivity

2. **AI Service Unavailable**
   - Verify GOOGLE_API_KEY is set
   - Check API quotas and limits
   - Review network restrictions

3. **WebSocket Connection Issues**
   - Check proxy configuration
   - Verify WebSocket support
   - Review CORS settings

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Start with debug output
make dev-logs
```

### Health Checks
```bash
# Check service health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000
```

## Maintenance

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
make clean
make prod
```

### Database Migrations
```bash
# Run migrations
make migrate

# Seed sample data (optional)
make seed
```

### Monitoring
- Regular health checks
- Monitor disk space
- Check log files for errors
- Review query performance