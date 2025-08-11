from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from app.models.database import get_vector_db
from app.models.schemas import RAGDocument, DocumentType
from app.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Retrieval Augmented Generation service for grounding AI responses"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dimension = 384  # Dimension for all-MiniLM-L6-v2
    
    async def add_document(self, document: RAGDocument, db_session: Session = None) -> bool:
        """Add a document to the RAG vector store"""
        
        if db_session is None:
            db_session = next(get_vector_db())
        
        try:
            # Generate embedding for the document
            embedding = self.embedding_model.encode(document.content)
            embedding_list = embedding.tolist()
            
            # Insert into vector database
            query = text("""
                INSERT INTO document_embeddings 
                (document_id, document_type, title, content, embedding, metadata)
                VALUES (:doc_id, :doc_type, :title, :content, :embedding, :metadata)
                ON CONFLICT (document_id) DO UPDATE SET
                    document_type = EXCLUDED.document_type,
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    created_at = CURRENT_TIMESTAMP
            """)
            
            db_session.execute(query, {
                'doc_id': document.id,
                'doc_type': document.document_type,
                'title': document.title,
                'content': document.content,
                'embedding': embedding_list,
                'metadata': json.dumps(document.metadata)
            })
            
            db_session.commit()
            logger.info(f"Added document {document.id} to RAG store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add document to RAG store: {e}")
            db_session.rollback()
            return False
        finally:
            if db_session:
                db_session.close()
    
    async def search_documents(
        self, 
        query: str, 
        document_types: List[str] = None, 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query"""
        
        db_session = next(get_vector_db())
        
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode(query)
            query_embedding_list = query_embedding.tolist()
            
            # Prepare document type filter
            type_filter = ""
            params = {
                'embedding': query_embedding_list,
                'limit': limit,
                'threshold': similarity_threshold
            }
            
            if document_types:
                type_placeholders = ','.join([f':type_{i}' for i in range(len(document_types))])
                type_filter = f"AND document_type IN ({type_placeholders})"
                for i, doc_type in enumerate(document_types):
                    params[f'type_{i}'] = doc_type
            
            # Search using cosine similarity
            search_query = text(f"""
                SELECT 
                    document_id,
                    document_type,
                    title,
                    content,
                    metadata,
                    1 - (embedding <=> :embedding) as similarity_score
                FROM document_embeddings
                WHERE 1 - (embedding <=> :embedding) >= :threshold
                {type_filter}
                ORDER BY similarity_score DESC
                LIMIT :limit
            """)
            
            result = db_session.execute(search_query, params)
            documents = []
            
            for row in result:
                documents.append({
                    'document_id': row.document_id,
                    'document_type': row.document_type,
                    'title': row.title,
                    'content': row.content,
                    'metadata': json.loads(row.metadata) if row.metadata else {},
                    'similarity_score': float(row.similarity_score)
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []
        finally:
            db_session.close()
    
    async def get_schema_context(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant schema documentation for a query"""
        
        schema_docs = await self.search_documents(
            query=query,
            document_types=[DocumentType.SCHEMA.value],
            limit=3,
            similarity_threshold=0.6
        )
        
        return schema_docs
    
    async def get_metric_definitions(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant metric definitions for a query"""
        
        metric_docs = await self.search_documents(
            query=query,
            document_types=[DocumentType.METRIC.value],
            limit=3,
            similarity_threshold=0.6
        )
        
        return metric_docs
    
    async def get_governance_context(self, query: str) -> List[Dict[str, Any]]:
        """Get relevant governance and compliance information"""
        
        governance_docs = await self.search_documents(
            query=query,
            document_types=[DocumentType.GOVERNANCE.value],
            limit=2,
            similarity_threshold=0.7
        )
        
        return governance_docs
    
    async def index_schema_metadata(self, schema_context: Dict[str, Any]) -> bool:
        """Index database schema metadata for RAG"""
        
        try:
            for table_name, table_info in schema_context.items():
                columns = table_info.get('columns', [])
                
                # Create document content for the table
                content_parts = [f"Table: {table_name}"]
                
                for col in columns:
                    if isinstance(col, dict):
                        col_name = col.get('name', 'unknown')
                        col_type = col.get('type', 'unknown')
                        col_desc = col.get('description', '')
                        
                        col_info = f"Column {col_name}: {col_type}"
                        if col_desc:
                            col_info += f" - {col_desc}"
                        
                        content_parts.append(col_info)
                
                content = "\n".join(content_parts)
                
                # Create RAG document
                document = RAGDocument(
                    id=f"schema_{table_name}",
                    title=f"Schema for table {table_name}",
                    content=content,
                    document_type=DocumentType.SCHEMA.value,
                    metadata={
                        "table_name": table_name,
                        "column_count": len(columns),
                        "indexed_at": datetime.now().isoformat()
                    }
                )
                
                await self.add_document(document)
            
            logger.info(f"Indexed {len(schema_context)} tables for RAG")
            return True
            
        except Exception as e:
            logger.error(f"Schema indexing failed: {e}")
            return False
    
    async def add_metric_definition(
        self, 
        metric_name: str, 
        definition: str, 
        calculation: str, 
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Add a business metric definition to the RAG store"""
        
        content = f"""
Metric: {metric_name}
Definition: {definition}
Calculation: {calculation}
        """.strip()
        
        document = RAGDocument(
            id=f"metric_{metric_name.lower().replace(' ', '_')}",
            title=f"Metric Definition: {metric_name}",
            content=content,
            document_type=DocumentType.METRIC.value,
            metadata=metadata or {}
        )
        
        return await self.add_document(document)
    
    async def add_governance_policy(
        self, 
        policy_name: str, 
        description: str, 
        rules: List[str],
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Add a data governance policy to the RAG store"""
        
        content_parts = [
            f"Policy: {policy_name}",
            f"Description: {description}",
            "Rules:"
        ]
        
        for rule in rules:
            content_parts.append(f"- {rule}")
        
        content = "\n".join(content_parts)
        
        document = RAGDocument(
            id=f"governance_{policy_name.lower().replace(' ', '_')}",
            title=f"Governance Policy: {policy_name}",
            content=content,
            document_type=DocumentType.GOVERNANCE.value,
            metadata=metadata or {}
        )
        
        return await self.add_document(document)
    
    async def get_contextual_information(self, query: str) -> Dict[str, Any]:
        """Get all relevant contextual information for a query"""
        
        try:
            # Search across all document types
            all_docs = await self.search_documents(
                query=query,
                document_types=None,  # Search all types
                limit=10,
                similarity_threshold=0.5
            )
            
            # Group by document type
            context = {
                'schema': [],
                'metrics': [],
                'governance': [],
                'other': []
            }
            
            for doc in all_docs:
                doc_type = doc.get('document_type', 'other')
                if doc_type == DocumentType.SCHEMA.value:
                    context['schema'].append(doc)
                elif doc_type == DocumentType.METRIC.value:
                    context['metrics'].append(doc)
                elif doc_type == DocumentType.GOVERNANCE.value:
                    context['governance'].append(doc)
                else:
                    context['other'].append(doc)
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get contextual information: {e}")
            return {
                'schema': [],
                'metrics': [],
                'governance': [],
                'other': []
            }
    
    async def cleanup_old_documents(self, days_old: int = 30) -> int:
        """Clean up old documents from the vector store"""
        
        db_session = next(get_vector_db())
        
        try:
            cleanup_query = text("""
                DELETE FROM document_embeddings
                WHERE created_at < CURRENT_TIMESTAMP - INTERVAL ':days days'
            """)
            
            result = db_session.execute(cleanup_query, {'days': days_old})
            deleted_count = result.rowcount
            
            db_session.commit()
            logger.info(f"Cleaned up {deleted_count} old documents")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Document cleanup failed: {e}")
            db_session.rollback()
            return 0
        finally:
            db_session.close()