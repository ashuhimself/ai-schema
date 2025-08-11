from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import field_validator


class Settings(BaseSettings):
    # Database Configuration
    database_type: str = "postgres"
    
    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "warehouse"
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    
    # BigQuery
    bigquery_project_id: Optional[str] = None
    bigquery_credentials_path: Optional[str] = None
    
    # Snowflake
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    snowflake_database: Optional[str] = None
    snowflake_schema: Optional[str] = None
    snowflake_warehouse: Optional[str] = None
    
    # Redshift
    redshift_host: Optional[str] = None
    redshift_port: int = 5439
    redshift_db: Optional[str] = None
    redshift_user: Optional[str] = None
    redshift_password: Optional[str] = None
    
    # AI Configuration
    google_api_key: str
    gemini_model: str = "gemini-1.5-pro"
    
    # Vector Store
    vector_db_host: str = "postgres"
    vector_db_port: int = 5432
    vector_db_name: str = "vector_store"
    vector_db_user: str = "postgres"
    vector_db_password: str = "password"
    
    # Security
    secret_key: str
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    def get_allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(',')]
    
    # Logging
    log_level: str = "INFO"
    enable_query_logging: bool = True
    
    # Query Limits
    max_query_rows: int = 10000
    query_timeout_seconds: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()