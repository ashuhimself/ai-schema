.PHONY: build up down logs clean dev prod help

# Default target
help:
	@echo "Available commands:"
	@echo "  build     - Build all Docker images"
	@echo "  up        - Start all services"
	@echo "  down      - Stop all services"
	@echo "  logs      - View logs from all services"
	@echo "  clean     - Remove all containers, networks, and volumes"
	@echo "  dev       - Start development environment"
	@echo "  prod      - Start production environment"
	@echo "  test      - Run tests"
	@echo "  migrate   - Run database migrations"
	@echo "  seed      - Seed database with sample data"

# Production environment
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Development environment
dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

dev-logs:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

dev-down:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

# Production environment
prod:
	docker-compose up -d --build
	@echo "Production environment started!"
	@echo "Application: http://localhost:3000"

# Database operations
migrate:
	docker-compose exec backend alembic upgrade head

seed:
	docker-compose exec backend python -m scripts.seed_data

# Testing
test:
	docker-compose exec backend pytest
	docker-compose exec frontend npm test

# Health check
health:
	@curl -f http://localhost:8000/health || echo "Backend is not responding"
	@curl -f http://localhost:3000 || echo "Frontend is not responding"

# Setup for first time users
setup: build
	@echo "Setting up Warehouse Copilot for the first time..."
	@cp .env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Then run 'make dev' to start the development environment"