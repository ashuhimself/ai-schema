import pandas as pd
from google.cloud import bigquery
from typing import Dict, List, Any, Optional, Tuple
from .base import BaseConnector
import logging
import re

logger = logging.getLogger(__name__)


class BigQueryConnector(BaseConnector):
    """Google BigQuery connector"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self.project_id = config.get('project_id')
    
    def connect(self) -> bool:
        """Establish connection to BigQuery"""
        try:
            if self.config.get('credentials_path'):
                import os
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config['credentials_path']
            
            self.client = bigquery.Client(project=self.project_id)
            
            # Test connection
            list(self.client.list_datasets(max_results=1))
            
            logger.info("BigQuery connection established")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to BigQuery: {e}")
            return False
    
    def disconnect(self):
        """Close BigQuery connection"""
        if self.client:
            self.client.close()
            self.client = None
            logger.info("BigQuery connection closed")
    
    def execute_query(self, query: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        try:
            # Apply limit if specified
            if limit and not re.search(r'\bLIMIT\b', query, re.IGNORECASE):
                query = f"{query} LIMIT {limit}"
            
            # Configure job to avoid unnecessary costs
            job_config = bigquery.QueryJobConfig(
                dry_run=False,
                use_query_cache=True,
                maximum_bytes_billed=100 * 1024 * 1024  # 100MB limit
            )
            
            query_job = self.client.query(query, job_config=job_config)
            result = query_job.to_dataframe()
            
            return result
            
        except Exception as e:
            logger.error(f"BigQuery execution failed: {e}")
            raise e
    
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        if not self.client:
            return {}
        
        schema_info = {}
        
        try:
            datasets = list(self.client.list_datasets())
            
            for dataset in datasets:
                dataset_id = dataset.dataset_id
                schema_info[dataset_id] = {}
                
                tables = list(self.client.list_tables(dataset_id))
                
                for table in tables:
                    table_ref = self.client.get_table(f"{self.project_id}.{dataset_id}.{table.table_id}")
                    
                    columns = []
                    for field in table_ref.schema:
                        columns.append({
                            "name": field.name,
                            "type": field.field_type,
                            "mode": field.mode,
                            "description": field.description or ""
                        })
                    
                    schema_info[dataset_id][table.table_id] = {
                        "columns": columns,
                        "row_count": table_ref.num_rows,
                        "table_type": table_ref.table_type,
                        "created": table_ref.created.isoformat() if table_ref.created else None
                    }
        
        except Exception as e:
            logger.error(f"Error getting BigQuery schema: {e}")
        
        return schema_info
    
    def get_tables(self) -> List[str]:
        """Get list of available tables"""
        if not self.client:
            return []
        
        tables = []
        try:
            datasets = list(self.client.list_datasets())
            
            for dataset in datasets:
                dataset_tables = list(self.client.list_tables(dataset.dataset_id))
                for table in dataset_tables:
                    tables.append(f"{dataset.dataset_id}.{table.table_id}")
        
        except Exception as e:
            logger.error(f"Error getting BigQuery tables: {e}")
        
        return tables
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific table"""
        if not self.client:
            return {}
        
        try:
            # Parse dataset and table name
            if '.' in table_name:
                dataset_id, table_id = table_name.split('.', 1)
            else:
                # If no dataset specified, try to find it
                datasets = list(self.client.list_datasets())
                for dataset in datasets:
                    try:
                        table_ref = self.client.get_table(f"{self.project_id}.{dataset.dataset_id}.{table_name}")
                        dataset_id = dataset.dataset_id
                        table_id = table_name
                        break
                    except:
                        continue
                else:
                    return {"error": f"Table {table_name} not found"}
            
            table_ref = self.client.get_table(f"{self.project_id}.{dataset_id}.{table_id}")
            
            columns = []
            for field in table_ref.schema:
                columns.append({
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or ""
                })
            
            return {
                "name": table_name,
                "columns": columns,
                "row_count": table_ref.num_rows,
                "size_bytes": table_ref.num_bytes,
                "table_type": table_ref.table_type,
                "created": table_ref.created.isoformat() if table_ref.created else None,
                "modified": table_ref.modified.isoformat() if table_ref.modified else None,
                "clustering_fields": table_ref.clustering_fields or [],
                "partitioning": {
                    "type": table_ref.time_partitioning.type_ if table_ref.time_partitioning else None,
                    "field": table_ref.time_partitioning.field if table_ref.time_partitioning else None
                } if table_ref.time_partitioning else None
            }
        
        except Exception as e:
            logger.error(f"Error getting BigQuery table info: {e}")
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
            
            # Use BigQuery's dry run to validate syntax
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            self.client.query(query, job_config=job_config)
            
            return True, None
            
        except Exception as e:
            return False, f"Query validation failed: {str(e)}"
    
    def get_query_plan(self, query: str) -> str:
        """Get execution plan for a query"""
        try:
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            query_job = self.client.query(query, job_config=job_config)
            
            plan_info = []
            if hasattr(query_job, 'query_plan') and query_job.query_plan:
                for stage in query_job.query_plan:
                    stage_info = f"Stage {stage.id}: {stage.name}"
                    if stage.input_stages:
                        stage_info += f" (inputs: {', '.join(map(str, stage.input_stages))})"
                    plan_info.append(stage_info)
            
            return "\n".join(plan_info) if plan_info else "Query plan not available"
            
        except Exception as e:
            return f"Error getting query plan: {str(e)}"
    
    def estimate_query_cost(self, query: str) -> Dict[str, Any]:
        """Estimate the cost/resources needed for query execution"""
        try:
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            query_job = self.client.query(query, job_config=job_config)
            
            bytes_processed = query_job.total_bytes_processed
            bytes_billed = query_job.total_bytes_billed
            
            # Rough cost estimation (BigQuery pricing as of 2024)
            cost_per_tb = 5.00  # USD per TB
            estimated_cost = (bytes_billed / (1024**4)) * cost_per_tb
            
            return {
                "bytes_processed": bytes_processed,
                "bytes_billed": bytes_billed,
                "estimated_cost_usd": round(estimated_cost, 4),
                "cost_model": f"${cost_per_tb} per TB processed"
            }
            
        except Exception as e:
            return {"error": f"Cost estimation failed: {str(e)}"}
    
    def get_relationships(self) -> List[Dict[str, str]]:
        """Get table relationships - BigQuery doesn't have enforced FKs, so this returns empty"""
        # BigQuery doesn't have enforced foreign key relationships
        # Would need to infer from naming conventions or metadata
        return []