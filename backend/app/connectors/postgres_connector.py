import pandas as pd
import psycopg2
import sqlparse
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import create_engine, text, MetaData
from .base import BaseConnector
import logging

logger = logging.getLogger(__name__)


class PostgresConnector(BaseConnector):
    """PostgreSQL database connector"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.engine = None
        self.metadata = None
    
    def connect(self) -> bool:
        """Establish connection to PostgreSQL"""
        try:
            connection_string = (
                f"postgresql://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
            
            self.engine = create_engine(connection_string)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine)
            
            logger.info("PostgreSQL connection established")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        """Close PostgreSQL connection"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            logger.info("PostgreSQL connection closed")
    
    def execute_query(self, query: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        try:
            # Apply limit if specified
            if limit:
                query = f"SELECT * FROM ({query}) AS subquery LIMIT {limit}"
            
            # Execute query
            with self.engine.connect() as conn:
                result = pd.read_sql(query, conn)
            
            return result
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise e
    
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        if not self.metadata:
            return {}
        
        schema_info = {}
        for table_name, table in self.metadata.tables.items():
            columns = []
            for column in table.columns:
                columns.append({
                    "name": column.name,
                    "type": str(column.type),
                    "nullable": column.nullable,
                    "primary_key": column.primary_key,
                    "foreign_keys": [str(fk) for fk in column.foreign_keys] if column.foreign_keys else []
                })
            
            schema_info[table_name] = {
                "columns": columns,
                "indexes": [idx.name for idx in table.indexes] if table.indexes else []
            }
        
        return schema_info
    
    def get_tables(self) -> List[str]:
        """Get list of available tables"""
        if not self.metadata:
            return []
        return list(self.metadata.tables.keys())
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific table"""
        if not self.metadata or table_name not in self.metadata.tables:
            return {}
        
        table = self.metadata.tables[table_name]
        
        # Get row count
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()
        except:
            row_count = None
        
        return {
            "name": table_name,
            "columns": [
                {
                    "name": col.name,
                    "type": str(col.type),
                    "nullable": col.nullable,
                    "primary_key": col.primary_key
                }
                for col in table.columns
            ],
            "row_count": row_count,
            "indexes": [idx.name for idx in table.indexes] if table.indexes else [],
            "foreign_keys": [
                {
                    "column": fk.parent.name,
                    "references": f"{fk.column.table.name}.{fk.column.name}"
                }
                for fk in table.foreign_keys
            ] if table.foreign_keys else []
        }
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate if query is safe to execute"""
        try:
            # Parse the SQL to check for dangerous operations
            parsed = sqlparse.parse(query)
            
            for statement in parsed:
                # Check for destructive operations
                tokens = [token.value.upper() for token in statement.flatten() if token.ttype is None]
                
                dangerous_operations = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE'}
                if any(op in tokens for op in dangerous_operations):
                    return False, f"Query contains potentially destructive operation: {tokens}"
            
            # Additional validation: ensure it's a SELECT statement
            query_upper = query.strip().upper()
            if not query_upper.startswith('SELECT') and not query_upper.startswith('WITH'):
                return False, "Only SELECT queries are allowed"
            
            return True, None
            
        except Exception as e:
            return False, f"Query parsing error: {str(e)}"
    
    def get_query_plan(self, query: str) -> str:
        """Get execution plan for a query"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"EXPLAIN ANALYZE {query}"))
                plan = "\n".join([row[0] for row in result])
            return plan
        except Exception as e:
            return f"Error getting query plan: {str(e)}"
    
    def estimate_query_cost(self, query: str) -> Dict[str, Any]:
        """Estimate the cost/resources needed for query execution"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"EXPLAIN (FORMAT JSON, ANALYZE false) {query}"))
                plan_json = result.fetchone()[0]
                
                if isinstance(plan_json, list) and len(plan_json) > 0:
                    plan = plan_json[0]
                    total_cost = plan.get('Plan', {}).get('Total Cost', 0)
                    startup_cost = plan.get('Plan', {}).get('Startup Cost', 0)
                    
                    return {
                        "estimated_cost": total_cost,
                        "startup_cost": startup_cost,
                        "cost_units": "arbitrary units",
                        "estimated_rows": plan.get('Plan', {}).get('Plan Rows', 0)
                    }
            
            return {"error": "Unable to estimate cost"}
            
        except Exception as e:
            return {"error": f"Cost estimation failed: {str(e)}"}
    
    def get_relationships(self) -> List[Dict[str, str]]:
        """Get table relationships based on foreign keys"""
        if not self.metadata:
            return []
        
        relationships = []
        for table_name, table in self.metadata.tables.items():
            for fk in table.foreign_keys:
                relationships.append({
                    "from_table": table_name,
                    "from_column": fk.parent.name,
                    "to_table": fk.column.table.name,
                    "to_column": fk.column.name
                })
        
        return relationships