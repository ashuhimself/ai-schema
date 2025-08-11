from typing import Dict, Any
from .base import BaseConnector
from .postgres_connector import PostgresConnector
from .bigquery_connector import BigQueryConnector
from .snowflake_connector import SnowflakeConnector
from .redshift_connector import RedshiftConnector
from app.config import settings


class ConnectorFactory:
    """Factory class for creating database connectors"""
    
    _connectors = {
        'postgres': PostgresConnector,
        'postgresql': PostgresConnector,
        'bigquery': BigQueryConnector,
        'bq': BigQueryConnector,
        'snowflake': SnowflakeConnector,
        'redshift': RedshiftConnector
    }
    
    @classmethod
    def create_connector(cls, db_type: str = None, config: Dict[str, Any] = None) -> BaseConnector:
        """Create a connector instance based on database type"""
        
        # Use settings if no explicit config provided
        if db_type is None:
            db_type = settings.database_type.lower()
        
        if config is None:
            config = cls._get_config_for_type(db_type)
        
        if db_type not in cls._connectors:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        connector_class = cls._connectors[db_type]
        return connector_class(config)
    
    @classmethod
    def _get_config_for_type(cls, db_type: str) -> Dict[str, Any]:
        """Get configuration dictionary for a specific database type"""
        
        if db_type in ['postgres', 'postgresql']:
            return {
                'host': settings.postgres_host,
                'port': settings.postgres_port,
                'database': settings.postgres_db,
                'user': settings.postgres_user,
                'password': settings.postgres_password
            }
        
        elif db_type in ['bigquery', 'bq']:
            return {
                'project_id': settings.bigquery_project_id,
                'credentials_path': settings.bigquery_credentials_path
            }
        
        elif db_type == 'snowflake':
            return {
                'account': settings.snowflake_account,
                'user': settings.snowflake_user,
                'password': settings.snowflake_password,
                'database': settings.snowflake_database,
                'schema': settings.snowflake_schema,
                'warehouse': settings.snowflake_warehouse
            }
        
        elif db_type == 'redshift':
            return {
                'host': settings.redshift_host,
                'port': settings.redshift_port,
                'database': settings.redshift_db,
                'user': settings.redshift_user,
                'password': settings.redshift_password
            }
        
        else:
            raise ValueError(f"No configuration available for database type: {db_type}")
    
    @classmethod
    def get_supported_types(cls) -> list:
        """Get list of supported database types"""
        return list(cls._connectors.keys())
    
    @classmethod
    def validate_config(cls, db_type: str, config: Dict[str, Any]) -> tuple:
        """Validate configuration for a database type"""
        
        required_fields = {
            'postgres': ['host', 'port', 'database', 'user', 'password'],
            'postgresql': ['host', 'port', 'database', 'user', 'password'],
            'bigquery': ['project_id'],
            'bq': ['project_id'],
            'snowflake': ['account', 'user', 'password'],
            'redshift': ['host', 'database', 'user', 'password']
        }
        
        if db_type not in required_fields:
            return False, f"Unsupported database type: {db_type}"
        
        missing_fields = []
        for field in required_fields[db_type]:
            if field not in config or not config[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, "Configuration is valid"