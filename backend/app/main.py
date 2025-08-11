from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from sqlalchemy import text

from app.config import settings
from app.api import query, schema, chat
from app.models.schemas import HealthCheck
from app.connectors.factory import ConnectorFactory

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Warehouse Copilot API",
    description="AI-powered database querying and analysis platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.log_level == "DEBUG" else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    
    # Test database connection
    database_connection = False
    try:
        connector = ConnectorFactory.create_connector()
        database_connection = connector.connect()
        if database_connection:
            connector.disconnect()
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
    
    # Test vector store connection
    vector_store_connection = False
    try:
        from app.models.database import vector_engine
        with vector_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        vector_store_connection = True
    except Exception as e:
        logger.warning(f"Vector store health check failed: {e}")
    
    # Test AI service
    ai_service = False
    try:
        if settings.google_api_key:
            ai_service = True
    except Exception as e:
        logger.warning(f"AI service health check failed: {e}")
    
    return HealthCheck(
        status="healthy" if all([database_connection, vector_store_connection, ai_service]) else "degraded",
        timestamp=datetime.now(),
        database_connection=database_connection,
        vector_store_connection=vector_store_connection,
        ai_service=ai_service
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Warehouse Copilot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
app.include_router(query.router)
app.include_router(schema.router)
app.include_router(chat.router)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("Starting Warehouse Copilot API...")
    
    # Initialize services
    try:
        # Test database connection
        connector = ConnectorFactory.create_connector()
        if connector.connect():
            logger.info(f"Successfully connected to {settings.database_type} database")
            connector.disconnect()
        else:
            logger.warning("Failed to connect to database")
        
        # Test vector store
        from app.models.database import vector_engine
        with vector_engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Successfully connected to vector store")
        
        logger.info("Warehouse Copilot API started successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Shutting down Warehouse Copilot API...")
    
    try:
        # Clean up resources
        from app.models.database import vector_engine
        vector_engine.dispose()
        
        logger.info("Warehouse Copilot API shut down successfully")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )