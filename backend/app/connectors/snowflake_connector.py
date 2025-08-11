import pandas as pd
import snowflake.connector
from typing import Dict, List, Any, Optional, Tuple
from .base import BaseConnector
import logging
import re

logger = logging.getLogger(__name__)


class SnowflakeConnector(BaseConnector):
    """Snowflake database connector"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Establish connection to Snowflake"""
        try:
            self.connection = snowflake.connector.connect(
                account=self.config['account'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config.get('database'),
                schema=self.config.get('schema'),
                warehouse=self.config.get('warehouse'),
                role=self.config.get('role', 'PUBLIC')
            )
            
            self.cursor = self.connection.cursor()
            
            # Test connection
            self.cursor.execute("SELECT CURRENT_VERSION()")
            
            logger.info("Snowflake connection established")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            return False
    
    def disconnect(self):
        """Close Snowflake connection"""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        
        if self.connection:
            self.connection.close()
            self.connection = None
            
        logger.info("Snowflake connection closed")
    
    def execute_query(self, query: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        try:
            # Apply limit if specified
            if limit and not re.search(r'\bLIMIT\b', query, re.IGNORECASE):
                query = f"{query} LIMIT {limit}"
            
            # Execute query
            self.cursor.execute(query)
            
            # Fetch results
            columns = [desc[0] for desc in self.cursor.description]
            rows = self.cursor.fetchall()
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=columns)
            
            return df
            
        except Exception as e:
            logger.error(f"Snowflake query execution failed: {e}")
            raise e
    
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        if not self.cursor:
            return {}
        
        schema_info = {}
        
        try:
            # Get databases
            self.cursor.execute("SHOW DATABASES")
            databases = self.cursor.fetchall()
            
            for db in databases:
                db_name = db[1]  # Database name is in second column
                schema_info[db_name] = {}
                
                # Switch to database
                self.cursor.execute(f"USE DATABASE {db_name}")
                
                # Get schemas in database
                self.cursor.execute("SHOW SCHEMAS")
                schemas = self.cursor.fetchall()
                
                for schema in schemas:
                    schema_name = schema[1]
                    if schema_name.startswith('INFORMATION_SCHEMA'):
                        continue
                    
                    schema_info[db_name][schema_name] = {}
                    
                    # Get tables in schema
                    self.cursor.execute(f"SHOW TABLES IN SCHEMA {db_name}.{schema_name}")
                    tables = self.cursor.fetchall()
                    
                    for table in tables:
                        table_name = table[1]
                        
                        # Get columns for table
                        self.cursor.execute(f"DESCRIBE TABLE {db_name}.{schema_name}.{table_name}")
                        columns = self.cursor.fetchall()
                        
                        column_info = []
                        for col in columns:
                            column_info.append({
                                "name": col[0],
                                "type": col[1],
                                "nullable": col[2] == 'Y',
                                "default": col[3],
                                "primary_key": col[4] == 'Y',
                                "unique_key": col[5] == 'Y'
                            })
                        
                        schema_info[db_name][schema_name][table_name] = {
                            "columns": column_info
                        }
        
        except Exception as e:
            logger.error(f"Error getting Snowflake schema: {e}")
        
        return schema_info
    
    def get_tables(self) -> List[str]:
        """Get list of available tables"""
        if not self.cursor:
            return []
        
        tables = []
        
        try:
            self.cursor.execute("SHOW TABLES")
            result = self.cursor.fetchall()
            
            for row in result:
                # Format: database.schema.table
                db_name = row[2] if len(row) > 2 else self.config.get('database', '')
                schema_name = row[3] if len(row) > 3 else self.config.get('schema', '')
                table_name = row[1]
                
                full_name = f"{db_name}.{schema_name}.{table_name}"
                tables.append(full_name)
        
        except Exception as e:
            logger.error(f"Error getting Snowflake tables: {e}")
        
        return tables
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific table"""
        if not self.cursor:
            return {}
        
        try:
            # Parse table name (database.schema.table)
            parts = table_name.split('.')
            if len(parts) == 3:
                db_name, schema_name, table_name = parts
            elif len(parts) == 2:
                schema_name, table_name = parts
                db_name = self.config.get('database')
            else:
                db_name = self.config.get('database')
                schema_name = self.config.get('schema')
            
            full_table_name = f"{db_name}.{schema_name}.{table_name}"
            
            # Get column information
            self.cursor.execute(f"DESCRIBE TABLE {full_table_name}")
            columns = self.cursor.fetchall()
            
            column_info = []
            for col in columns:
                column_info.append({
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[2] == 'Y',
                    "default": col[3],
                    "primary_key": col[4] == 'Y'
                })
            
            # Get row count
            try:
                self.cursor.execute(f"SELECT COUNT(*) FROM {full_table_name}")
                row_count = self.cursor.fetchone()[0]
            except:
                row_count = None
            
            # Get table details
            self.cursor.execute(f"SHOW TABLES LIKE '{table_name}' IN SCHEMA {db_name}.{schema_name}")
            table_details = self.cursor.fetchone()
            
            return {
                "name": full_table_name,
                "columns": column_info,
                "row_count": row_count,
                "table_type": table_details[4] if table_details and len(table_details) > 4 else "TABLE",
                "created": table_details[0] if table_details else None,
                "size_bytes": table_details[7] if table_details and len(table_details) > 7 else None
            }
        
        except Exception as e:
            logger.error(f"Error getting Snowflake table info: {e}")
            return {"error": str(e)}
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate if query is safe to execute"""
        try:
            # Check for destructive operations
            query_upper = query.upper()
            dangerous_operations = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
            
            for op in dangerous_operations:
                if re.search(rf'\b{op}\b', query_upper):
                    return False, f"Query contains potentially destructive operation: {op}"
            
            # Ensure it's a SELECT or WITH statement
            query_stripped = query.strip().upper()
            if not query_stripped.startswith('SELECT') and not query_stripped.startswith('WITH'):
                return False, "Only SELECT queries are allowed"
            
            return True, None
            
        except Exception as e:
            return False, f"Query validation failed: {str(e)}"
    
    def get_query_plan(self, query: str) -> str:
        """Get execution plan for a query"""
        try:
            explain_query = f"EXPLAIN {query}"
            self.cursor.execute(explain_query)
            
            plan_rows = self.cursor.fetchall()
            plan = "\n".join([row[0] for row in plan_rows])
            
            return plan
            
        except Exception as e:
            return f"Error getting query plan: {str(e)}"
    
    def estimate_query_cost(self, query: str) -> Dict[str, Any]:
        """Estimate the cost/resources needed for query execution"""
        try:
            # Snowflake doesn't provide direct cost estimation
            # We can use EXPLAIN to get some insights
            explain_query = f"EXPLAIN {query}"
            self.cursor.execute(explain_query)
            
            plan_rows = self.cursor.fetchall()
            
            # Look for partition pruning and other optimization hints
            plan_text = "\n".join([row[0] for row in plan_rows])
            
            # Basic analysis
            has_partition_pruning = "partitions" in plan_text.lower()
            has_clustering = "clustering" in plan_text.lower()
            
            return {
                "plan_available": True,
                "partition_pruning": has_partition_pruning,
                "clustering_used": has_clustering,
                "optimization_hints": "Check query plan for detailed performance insights",
                "cost_units": "Snowflake credits (actual cost depends on warehouse size and query complexity)"
            }
            
        except Exception as e:
            return {"error": f"Cost estimation failed: {str(e)}"}
    
    def get_relationships(self) -> List[Dict[str, str]]:
        """Get table relationships based on foreign keys"""
        if not self.cursor:
            return []
        
        relationships = []
        
        try:
            # Query information schema for foreign key relationships
            query = """
            SELECT 
                fk.table_schema,
                fk.table_name,
                fk.column_name,
                fk.referenced_table_schema,
                fk.referenced_table_name,
                fk.referenced_column_name
            FROM information_schema.referential_constraints rc
            JOIN information_schema.key_column_usage fk ON rc.constraint_name = fk.constraint_name
            WHERE fk.table_schema = rc.constraint_schema
            """
            
            self.cursor.execute(query)
            foreign_keys = self.cursor.fetchall()
            
            for fk in foreign_keys:
                relationships.append({
                    "from_table": f"{fk[0]}.{fk[1]}",
                    "from_column": fk[2],
                    "to_table": f"{fk[3]}.{fk[4]}",
                    "to_column": fk[5]
                })
        
        except Exception as e:
            logger.error(f"Error getting Snowflake relationships: {e}")
        
        return relationships