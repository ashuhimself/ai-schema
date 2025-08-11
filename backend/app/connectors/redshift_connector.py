import pandas as pd
import redshift_connector
from typing import Dict, List, Any, Optional, Tuple
from .base import BaseConnector
import logging
import re

logger = logging.getLogger(__name__)


class RedshiftConnector(BaseConnector):
    """Amazon Redshift connector"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Establish connection to Redshift"""
        try:
            self.connection = redshift_connector.connect(
                host=self.config['host'],
                database=self.config['database'],
                port=self.config.get('port', 5439),
                user=self.config['user'],
                password=self.config['password'],
                ssl=True,
                sslmode='require'
            )
            
            self.cursor = self.connection.cursor()
            
            # Test connection
            self.cursor.execute("SELECT version()")
            
            logger.info("Redshift connection established")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redshift: {e}")
            return False
    
    def disconnect(self):
        """Close Redshift connection"""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        
        if self.connection:
            self.connection.close()
            self.connection = None
            
        logger.info("Redshift connection closed")
    
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
            logger.error(f"Redshift query execution failed: {e}")
            raise e
    
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        if not self.cursor:
            return {}
        
        schema_info = {}
        
        try:
            # Get schemas
            self.cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_internal')
            """)
            
            schemas = self.cursor.fetchall()
            
            for schema in schemas:
                schema_name = schema[0]
                schema_info[schema_name] = {}
                
                # Get tables in schema
                self.cursor.execute("""
                    SELECT table_name, table_type
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                """, (schema_name,))
                
                tables = self.cursor.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    table_type = table[1]
                    
                    # Get columns for table
                    self.cursor.execute("""
                        SELECT 
                            column_name,
                            data_type,
                            is_nullable,
                            column_default,
                            character_maximum_length,
                            numeric_precision
                        FROM information_schema.columns 
                        WHERE table_schema = %s AND table_name = %s
                        ORDER BY ordinal_position
                    """, (schema_name, table_name))
                    
                    columns = self.cursor.fetchall()
                    
                    column_info = []
                    for col in columns:
                        column_info.append({
                            "name": col[0],
                            "type": col[1],
                            "nullable": col[2] == 'YES',
                            "default": col[3],
                            "max_length": col[4],
                            "precision": col[5]
                        })
                    
                    schema_info[schema_name][table_name] = {
                        "columns": column_info,
                        "table_type": table_type
                    }
        
        except Exception as e:
            logger.error(f"Error getting Redshift schema: {e}")
        
        return schema_info
    
    def get_tables(self) -> List[str]:
        """Get list of available tables"""
        if not self.cursor:
            return []
        
        tables = []
        
        try:
            self.cursor.execute("""
                SELECT table_schema, table_name
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_internal')
                ORDER BY table_schema, table_name
            """)
            
            result = self.cursor.fetchall()
            
            for row in result:
                schema_name, table_name = row
                tables.append(f"{schema_name}.{table_name}")
        
        except Exception as e:
            logger.error(f"Error getting Redshift tables: {e}")
        
        return tables
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific table"""
        if not self.cursor:
            return {}
        
        try:
            # Parse schema and table name
            if '.' in table_name:
                schema_name, table_name = table_name.split('.', 1)
            else:
                schema_name = 'public'  # Default schema
            
            # Get column information
            self.cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """, (schema_name, table_name))
            
            columns = self.cursor.fetchall()
            
            column_info = []
            for col in columns:
                column_info.append({
                    "name": col[0],
                    "type": col[1],
                    "nullable": col[2] == 'YES',
                    "default": col[3],
                    "max_length": col[4],
                    "precision": col[5],
                    "scale": col[6]
                })
            
            # Get table statistics
            try:
                self.cursor.execute(f"""
                    SELECT 
                        COUNT(*) as row_count,
                        COUNT(DISTINCT 1) as approximate_row_count
                    FROM {schema_name}.{table_name}
                    LIMIT 1
                """)
                stats = self.cursor.fetchone()
                row_count = stats[0] if stats else None
            except:
                # If direct count fails, try system tables
                try:
                    self.cursor.execute("""
                        SELECT tbl_rows
                        FROM svv_table_info 
                        WHERE schema = %s AND "table" = %s
                    """, (schema_name, table_name))
                    result = self.cursor.fetchone()
                    row_count = result[0] if result else None
                except:
                    row_count = None
            
            # Get distribution and sort keys
            try:
                self.cursor.execute("""
                    SELECT 
                        distkey,
                        sortkey1,
                        sortkey2
                    FROM pg_table_def 
                    WHERE schemaname = %s AND tablename = %s
                    LIMIT 1
                """, (schema_name, table_name))
                
                dist_sort = self.cursor.fetchone()
                distribution_key = dist_sort[0] if dist_sort and dist_sort[0] else None
                sort_keys = [key for key in [dist_sort[1], dist_sort[2]] if dist_sort and key]
                
            except:
                distribution_key = None
                sort_keys = []
            
            return {
                "name": f"{schema_name}.{table_name}",
                "columns": column_info,
                "row_count": row_count,
                "distribution_key": distribution_key,
                "sort_keys": sort_keys
            }
        
        except Exception as e:
            logger.error(f"Error getting Redshift table info: {e}")
            return {"error": str(e)}
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate if query is safe to execute"""
        try:
            # Check for destructive operations
            query_upper = query.upper()
            dangerous_operations = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'COPY']
            
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
            # Get query plan with costs
            explain_query = f"EXPLAIN {query}"
            self.cursor.execute(explain_query)
            
            plan_rows = self.cursor.fetchall()
            plan_text = "\n".join([row[0] for row in plan_rows])
            
            # Extract cost information from explain plan
            # Look for patterns like "cost=X..Y rows=Z"
            cost_pattern = r'cost=([0-9.]+)\.\.([0-9.]+) rows=([0-9]+)'
            costs = re.findall(cost_pattern, plan_text)
            
            if costs:
                total_cost = sum(float(cost[1]) for cost in costs)
                total_rows = sum(int(cost[2]) for cost in costs)
                
                return {
                    "estimated_cost": total_cost,
                    "estimated_rows": total_rows,
                    "cost_units": "Redshift query planner units",
                    "plan_details": plan_text[:500] + "..." if len(plan_text) > 500 else plan_text
                }
            else:
                return {
                    "plan_available": True,
                    "cost_details": "Cost information not available in plan",
                    "plan_summary": plan_text[:200] + "..." if len(plan_text) > 200 else plan_text
                }
            
        except Exception as e:
            return {"error": f"Cost estimation failed: {str(e)}"}
    
    def get_relationships(self) -> List[Dict[str, str]]:
        """Get table relationships based on foreign keys"""
        if not self.cursor:
            return []
        
        relationships = []
        
        try:
            # Query for foreign key constraints
            self.cursor.execute("""
                SELECT 
                    tc.table_schema,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_schema AS foreign_table_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
            """)
            
            foreign_keys = self.cursor.fetchall()
            
            for fk in foreign_keys:
                relationships.append({
                    "from_table": f"{fk[0]}.{fk[1]}",
                    "from_column": fk[2],
                    "to_table": f"{fk[3]}.{fk[4]}",
                    "to_column": fk[5]
                })
        
        except Exception as e:
            logger.error(f"Error getting Redshift relationships: {e}")
        
        return relationships