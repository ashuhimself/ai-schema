from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any
import time
import uuid
import logging
from datetime import datetime

from app.models.schemas import QueryRequest, QueryResponse, QueryPlan, QueryValidation
from app.connectors.factory import ConnectorFactory
from app.services.ai_service import AIService
from app.services.query_logger import QueryLogger

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/query", tags=["query"])

# Dependency injection
def get_ai_service():
    return AIService()

def get_query_logger():
    return QueryLogger()


@router.post("/execute", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    ai_service: AIService = Depends(get_ai_service),
    query_logger: QueryLogger = Depends(get_query_logger)
):
    """Execute a natural language or SQL query"""
    
    start_time = time.time()
    query_id = str(uuid.uuid4())
    
    try:
        # Create database connector
        connector = ConnectorFactory.create_connector(request.database_type)
        
        if not connector.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to database")
        
        try:
            generated_sql = None
            
            # Handle natural language queries
            if request.query_type == "natural":
                logger.info(f"Processing natural language query: {request.query}")
                
                # Get schema context for AI
                schema_context = connector.get_schema()
                
                # Generate SQL using AI
                generated_sql = await ai_service.generate_sql(
                    query=request.query,
                    schema_context=schema_context,
                    database_type=connector.config.get('type', 'postgres')
                )
                
                if not generated_sql:
                    raise HTTPException(status_code=400, detail="Could not generate SQL from natural language query")
                
                sql_to_execute = generated_sql
                
            else:
                # Direct SQL execution
                sql_to_execute = request.query
                generated_sql = request.query
            
            # Validate query safety
            is_valid, validation_error = connector.validate_query(sql_to_execute)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Query validation failed: {validation_error}")
            
            # Execute query
            results_df = connector.execute_query(sql_to_execute, limit=request.limit)
            
            # Convert DataFrame to dictionary format
            results = {
                "columns": results_df.columns.tolist(),
                "data": results_df.to_dict('records'),
                "total_rows": len(results_df)
            }
            
            # Generate insights using AI
            insights = None
            if request.query_type == "natural":
                insights = await ai_service.generate_insights(
                    query=request.query,
                    results=results_df,
                    sql=generated_sql
                )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log query in background
            background_tasks.add_task(
                query_logger.log_query,
                query_id=query_id,
                original_query=request.query,
                generated_sql=generated_sql,
                success=True,
                execution_time_ms=execution_time,
                row_count=len(results_df)
            )
            
            response = QueryResponse(
                success=True,
                query_id=query_id,
                generated_sql=generated_sql,
                results=results,
                insights=insights,
                execution_time_ms=execution_time,
                row_count=len(results_df),
                metadata={
                    "query_type": request.query_type,
                    "database_type": connector.config.get('type'),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return response
            
        finally:
            connector.disconnect()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        
        execution_time = int((time.time() - start_time) * 1000)
        
        # Log failed query
        background_tasks.add_task(
            query_logger.log_query,
            query_id=query_id,
            original_query=request.query,
            generated_sql=generated_sql,
            success=False,
            execution_time_ms=execution_time,
            error_message=str(e)
        )
        
        return QueryResponse(
            success=False,
            query_id=query_id,
            error=str(e),
            execution_time_ms=execution_time
        )


@router.post("/validate", response_model=QueryValidation)
async def validate_query(request: QueryRequest):
    """Validate a SQL query without executing it"""
    
    try:
        connector = ConnectorFactory.create_connector(request.database_type)
        
        if not connector.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to database")
        
        try:
            sql_query = request.query
            
            # If natural language, first convert to SQL
            if request.query_type == "natural":
                ai_service = AIService()
                schema_context = connector.get_schema()
                sql_query = await ai_service.generate_sql(
                    query=request.query,
                    schema_context=schema_context,
                    database_type=connector.config.get('type', 'postgres')
                )
            
            # Validate the SQL
            is_valid, error_message = connector.validate_query(sql_query)
            
            return QueryValidation(
                is_valid=is_valid,
                error_message=error_message,
                safety_issues=[] if is_valid else [error_message],
                suggested_fixes=[] if is_valid else ["Ensure query only contains SELECT statements"]
            )
            
        finally:
            connector.disconnect()
    
    except Exception as e:
        logger.error(f"Query validation failed: {e}")
        return QueryValidation(
            is_valid=False,
            error_message=str(e)
        )


@router.post("/plan", response_model=QueryPlan)
async def get_query_plan(request: QueryRequest):
    """Get execution plan for a query"""
    
    try:
        connector = ConnectorFactory.create_connector(request.database_type)
        
        if not connector.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to database")
        
        try:
            sql_query = request.query
            
            # If natural language, first convert to SQL
            if request.query_type == "natural":
                ai_service = AIService()
                schema_context = connector.get_schema()
                sql_query = await ai_service.generate_sql(
                    query=request.query,
                    schema_context=schema_context,
                    database_type=connector.config.get('type', 'postgres')
                )
            
            # Get execution plan
            plan = connector.get_query_plan(sql_query)
            cost_estimate = connector.estimate_query_cost(sql_query)
            
            return QueryPlan(
                query=sql_query,
                plan=plan,
                estimated_cost=cost_estimate
            )
            
        finally:
            connector.disconnect()
    
    except Exception as e:
        logger.error(f"Getting query plan failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get query plan: {str(e)}")


@router.get("/history")
async def get_query_history(limit: int = 50, offset: int = 0):
    """Get query execution history"""
    
    try:
        query_logger = QueryLogger()
        history = await query_logger.get_query_history(limit=limit, offset=offset)
        return {"success": True, "history": history}
    
    except Exception as e:
        logger.error(f"Failed to get query history: {e}")
        raise HTTPException(status_code=500, detail=str(e))