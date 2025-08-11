from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Vector database connection for RAG
VECTOR_DATABASE_URL = f"postgresql://{settings.vector_db_user}:{settings.vector_db_password}@{settings.vector_db_host}:{settings.vector_db_port}/{settings.vector_db_name}"

vector_engine = create_engine(VECTOR_DATABASE_URL)
VectorSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=vector_engine)

Base = declarative_base()


def get_vector_db():
    """Get vector database session"""
    db = VectorSessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_warehouse_connection():
    """Get connection to the main data warehouse"""
    db_type = settings.database_type.lower()
    
    if db_type == "postgres":
        url = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
        return create_engine(url)
    
    elif db_type == "bigquery":
        from google.cloud import bigquery
        if settings.bigquery_credentials_path:
            import os
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.bigquery_credentials_path
        return bigquery.Client(project=settings.bigquery_project_id)
    
    elif db_type == "snowflake":
        import snowflake.connector
        return snowflake.connector.connect(
            account=settings.snowflake_account,
            user=settings.snowflake_user,
            password=settings.snowflake_password,
            database=settings.snowflake_database,
            schema=settings.snowflake_schema,
            warehouse=settings.snowflake_warehouse
        )
    
    elif db_type == "redshift":
        url = f"redshift+psycopg2://{settings.redshift_user}:{settings.redshift_password}@{settings.redshift_host}:{settings.redshift_port}/{settings.redshift_db}"
        return create_engine(url)
    
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


def get_database_metadata():
    """Get metadata for schema exploration"""
    try:
        if settings.database_type.lower() == "bigquery":
            client = get_warehouse_connection()
            datasets = list(client.list_datasets())
            metadata = {}
            
            for dataset in datasets:
                tables = list(client.list_tables(dataset.dataset_id))
                metadata[dataset.dataset_id] = {}
                
                for table in tables:
                    table_ref = client.get_table(f"{dataset.dataset_id}.{table.table_id}")
                    columns = [{"name": field.name, "type": field.field_type, "mode": field.mode} 
                              for field in table_ref.schema]
                    metadata[dataset.dataset_id][table.table_id] = columns
            
            return metadata
        
        else:
            engine = get_warehouse_connection()
            metadata = MetaData()
            metadata.reflect(bind=engine)
            
            schema_info = {}
            for table_name, table in metadata.tables.items():
                columns = []
                for column in table.columns:
                    columns.append({
                        "name": column.name,
                        "type": str(column.type),
                        "nullable": column.nullable,
                        "primary_key": column.primary_key
                    })
                schema_info[table_name] = columns
            
            return schema_info
            
    except Exception as e:
        logger.error(f"Error getting database metadata: {e}")
        return {}