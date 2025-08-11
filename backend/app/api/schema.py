from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
import logging

from app.models.schemas import SchemaRequest, SchemaResponse, TableInfo
from app.connectors.factory import ConnectorFactory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/schema", tags=["schema"])


@router.post("/", response_model=SchemaResponse)
async def get_schema(request: SchemaRequest = SchemaRequest()):
    """Get database schema information"""
    
    try:
        connector = ConnectorFactory.create_connector()
        
        if not connector.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to database")
        
        try:
            schema_data = connector.get_schema()
            relationships = []
            
            if request.include_relationships:
                relationships = connector.get_relationships() if hasattr(connector, 'get_relationships') else []
            
            return SchemaResponse(
                success=True,
                schema=schema_data,
                relationships=relationships
            )
            
        finally:
            connector.disconnect()
    
    except Exception as e:
        logger.error(f"Failed to get schema: {e}")
        return SchemaResponse(
            success=False,
            error=str(e)
        )


@router.get("/tables")
async def get_tables():
    """Get list of all available tables"""
    
    try:
        connector = ConnectorFactory.create_connector()
        
        if not connector.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to database")
        
        try:
            tables = connector.get_tables()
            return {
                "success": True,
                "tables": tables
            }
            
        finally:
            connector.disconnect()
    
    except Exception as e:
        logger.error(f"Failed to get tables: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/tables/{table_name}", response_model=TableInfo)
async def get_table_info(table_name: str):
    """Get detailed information about a specific table"""
    
    try:
        connector = ConnectorFactory.create_connector()
        
        if not connector.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to database")
        
        try:
            table_info = connector.get_table_info(table_name)
            
            if not table_info:
                raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
            
            # Convert to TableInfo model
            return TableInfo(**table_info)
            
        finally:
            connector.disconnect()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get table info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/relationships")
async def get_relationships():
    """Get table relationships (foreign keys)"""
    
    try:
        connector = ConnectorFactory.create_connector()
        
        if not connector.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to database")
        
        try:
            relationships = connector.get_relationships() if hasattr(connector, 'get_relationships') else []
            
            return {
                "success": True,
                "relationships": relationships,
                "relationship_count": len(relationships)
            }
            
        finally:
            connector.disconnect()
    
    except Exception as e:
        logger.error(f"Failed to get relationships: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/graph")
async def get_schema_graph():
    """Get schema as a graph structure for visualization"""
    
    try:
        connector = ConnectorFactory.create_connector()
        
        if not connector.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to database")
        
        try:
            # Get tables and their information
            tables = connector.get_tables()
            schema_data = connector.get_schema()
            relationships = connector.get_relationships() if hasattr(connector, 'get_relationships') else []
            
            # Build graph structure
            nodes = []
            edges = []
            
            # Create nodes for tables
            for table_name in tables:
                # Get table info for metadata
                table_info = schema_data.get(table_name, {})
                columns = table_info.get('columns', [])
                
                node = {
                    "id": table_name,
                    "label": table_name,
                    "type": "table",
                    "columns": len(columns),
                    "metadata": {
                        "columns": columns[:5],  # First 5 columns for preview
                        "total_columns": len(columns)
                    }
                }
                nodes.append(node)
            
            # Create edges for relationships
            for rel in relationships:
                edge = {
                    "id": f"{rel['from_table']}-{rel['to_table']}-{rel['from_column']}",
                    "source": rel['from_table'],
                    "target": rel['to_table'],
                    "label": f"{rel['from_column']} → {rel['to_column']}",
                    "type": "foreign_key"
                }
                edges.append(edge)
            
            return {
                "success": True,
                "graph": {
                    "nodes": nodes,
                    "edges": edges
                },
                "stats": {
                    "table_count": len(nodes),
                    "relationship_count": len(edges)
                }
            }
            
        finally:
            connector.disconnect()
    
    except Exception as e:
        logger.error(f"Failed to generate schema graph: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/search")
async def search_schema(q: str, limit: int = 10):
    """Search for tables, columns, or other schema elements"""
    
    try:
        connector = ConnectorFactory.create_connector()
        
        if not connector.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to database")
        
        try:
            schema_data = connector.get_schema()
            search_results = []
            
            query_lower = q.lower()
            
            # Search through tables and columns
            for table_name, table_info in schema_data.items():
                # Search table names
                if query_lower in table_name.lower():
                    search_results.append({
                        "type": "table",
                        "table": table_name,
                        "match": table_name,
                        "score": 10  # Higher score for table name matches
                    })
                
                # Search column names and types
                columns = table_info.get('columns', [])
                for column in columns:
                    column_name = column.get('name', '')
                    column_type = column.get('type', '')
                    column_desc = column.get('description', '')
                    
                    if (query_lower in column_name.lower() or 
                        query_lower in column_type.lower() or 
                        (column_desc and query_lower in column_desc.lower())):
                        
                        search_results.append({
                            "type": "column",
                            "table": table_name,
                            "column": column_name,
                            "column_type": column_type,
                            "match": column_name,
                            "score": 5  # Lower score for column matches
                        })
            
            # Sort by score and limit results
            search_results.sort(key=lambda x: x['score'], reverse=True)
            search_results = search_results[:limit]
            
            return {
                "success": True,
                "results": search_results,
                "total_found": len(search_results),
                "query": q
            }
            
        finally:
            connector.disconnect()
    
    except Exception as e:
        logger.error(f"Schema search failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }