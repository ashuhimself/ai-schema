from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import uuid

from app.models.database import get_vector_db
from app.config import settings

logger = logging.getLogger(__name__)


class QueryLogger:
    """Service for logging and tracking query executions"""
    
    def __init__(self):
        self.enabled = settings.enable_query_logging
    
    async def log_query(
        self,
        query_id: str,
        original_query: str,
        generated_sql: Optional[str] = None,
        success: bool = True,
        execution_time_ms: Optional[int] = None,
        row_count: Optional[int] = None,
        error_message: Optional[str] = None,
        user_id: Optional[str] = None,
        query_type: str = "natural"
    ) -> bool:
        """Log a query execution"""
        
        if not self.enabled:
            return True
        
        db_session = next(get_vector_db())
        
        try:
            log_query = text("""
                INSERT INTO query_logs 
                (id, user_id, query_text, generated_sql, query_type, execution_time_ms, 
                 row_count, success, error_message, timestamp)
                VALUES (:id, :user_id, :query_text, :generated_sql, :query_type, 
                        :execution_time_ms, :row_count, :success, :error_message, :timestamp)
            """)
            
            db_session.execute(log_query, {
                'id': query_id,
                'user_id': user_id,
                'query_text': original_query,
                'generated_sql': generated_sql,
                'query_type': query_type,
                'execution_time_ms': execution_time_ms,
                'row_count': row_count,
                'success': success,
                'error_message': error_message,
                'timestamp': datetime.now()
            })
            
            db_session.commit()
            logger.debug(f"Logged query {query_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            db_session.rollback()
            return False
        finally:
            db_session.close()
    
    async def get_query_history(
        self, 
        user_id: Optional[str] = None,
        limit: int = 50, 
        offset: int = 0,
        success_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get query execution history"""
        
        db_session = next(get_vector_db())
        
        try:
            # Build query with optional filters
            where_clauses = []
            params = {'limit': limit, 'offset': offset}
            
            if user_id:
                where_clauses.append("user_id = :user_id")
                params['user_id'] = user_id
            
            if success_only:
                where_clauses.append("success = true")
            
            where_clause = " AND ".join(where_clauses)
            if where_clause:
                where_clause = "WHERE " + where_clause
            
            history_query = text(f"""
                SELECT 
                    id,
                    user_id,
                    query_text,
                    generated_sql,
                    query_type,
                    execution_time_ms,
                    row_count,
                    success,
                    error_message,
                    timestamp
                FROM query_logs
                {where_clause}
                ORDER BY timestamp DESC
                LIMIT :limit OFFSET :offset
            """)
            
            result = db_session.execute(history_query, params)
            
            history = []
            for row in result:
                history.append({
                    'id': row.id,
                    'user_id': row.user_id,
                    'query_text': row.query_text,
                    'generated_sql': row.generated_sql,
                    'query_type': row.query_type,
                    'execution_time_ms': row.execution_time_ms,
                    'row_count': row.row_count,
                    'success': row.success,
                    'error_message': row.error_message,
                    'timestamp': row.timestamp.isoformat() if row.timestamp else None
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get query history: {e}")
            return []
        finally:
            db_session.close()
    
    async def get_query_stats(
        self, 
        days: int = 7,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get query execution statistics"""
        
        db_session = next(get_vector_db())
        
        try:
            # Date range for stats
            start_date = datetime.now() - timedelta(days=days)
            
            params = {'start_date': start_date}
            where_clause = "WHERE timestamp >= :start_date"
            
            if user_id:
                where_clause += " AND user_id = :user_id"
                params['user_id'] = user_id
            
            stats_query = text(f"""
                SELECT 
                    COUNT(*) as total_queries,
                    COUNT(CASE WHEN success = true THEN 1 END) as successful_queries,
                    COUNT(CASE WHEN success = false THEN 1 END) as failed_queries,
                    AVG(execution_time_ms) as avg_execution_time,
                    MAX(execution_time_ms) as max_execution_time,
                    AVG(row_count) as avg_row_count,
                    MAX(row_count) as max_row_count,
                    COUNT(DISTINCT user_id) as unique_users
                FROM query_logs
                {where_clause}
            """)
            
            result = db_session.execute(stats_query, params).fetchone()
            
            # Get query type breakdown
            type_query = text(f"""
                SELECT 
                    query_type,
                    COUNT(*) as count
                FROM query_logs
                {where_clause}
                GROUP BY query_type
            """)
            
            type_result = db_session.execute(type_query, params)
            query_types = {row.query_type: row.count for row in type_result}
            
            # Get daily query counts
            daily_query = text(f"""
                SELECT 
                    DATE(timestamp) as query_date,
                    COUNT(*) as count
                FROM query_logs
                {where_clause}
                GROUP BY DATE(timestamp)
                ORDER BY query_date
            """)
            
            daily_result = db_session.execute(daily_query, params)
            daily_counts = [
                {'date': row.query_date.isoformat(), 'count': row.count}
                for row in daily_result
            ]
            
            stats = {
                'period_days': days,
                'total_queries': result.total_queries or 0,
                'successful_queries': result.successful_queries or 0,
                'failed_queries': result.failed_queries or 0,
                'success_rate': (result.successful_queries / result.total_queries * 100) if result.total_queries > 0 else 0,
                'avg_execution_time_ms': float(result.avg_execution_time) if result.avg_execution_time else 0,
                'max_execution_time_ms': result.max_execution_time or 0,
                'avg_row_count': float(result.avg_row_count) if result.avg_row_count else 0,
                'max_row_count': result.max_row_count or 0,
                'unique_users': result.unique_users or 0,
                'query_types': query_types,
                'daily_counts': daily_counts
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get query stats: {e}")
            return {}
        finally:
            db_session.close()
    
    async def get_popular_queries(
        self, 
        limit: int = 10,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get most popular/frequent queries"""
        
        db_session = next(get_vector_db())
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            popular_query = text("""
                SELECT 
                    query_text,
                    COUNT(*) as frequency,
                    AVG(execution_time_ms) as avg_execution_time,
                    AVG(row_count) as avg_row_count,
                    MAX(timestamp) as last_used
                FROM query_logs
                WHERE timestamp >= :start_date
                    AND success = true
                    AND query_text IS NOT NULL
                GROUP BY query_text
                HAVING COUNT(*) > 1
                ORDER BY frequency DESC
                LIMIT :limit
            """)
            
            result = db_session.execute(popular_query, {
                'start_date': start_date,
                'limit': limit
            })
            
            popular_queries = []
            for row in result:
                popular_queries.append({
                    'query_text': row.query_text,
                    'frequency': row.frequency,
                    'avg_execution_time_ms': float(row.avg_execution_time) if row.avg_execution_time else 0,
                    'avg_row_count': float(row.avg_row_count) if row.avg_row_count else 0,
                    'last_used': row.last_used.isoformat() if row.last_used else None
                })
            
            return popular_queries
            
        except Exception as e:
            logger.error(f"Failed to get popular queries: {e}")
            return []
        finally:
            db_session.close()
    
    async def get_slow_queries(
        self, 
        limit: int = 10,
        min_execution_time: int = 1000  # milliseconds
    ) -> List[Dict[str, Any]]:
        """Get slowest executing queries"""
        
        db_session = next(get_vector_db())
        
        try:
            slow_query = text("""
                SELECT 
                    id,
                    query_text,
                    generated_sql,
                    execution_time_ms,
                    row_count,
                    timestamp
                FROM query_logs
                WHERE execution_time_ms >= :min_time
                    AND success = true
                ORDER BY execution_time_ms DESC
                LIMIT :limit
            """)
            
            result = db_session.execute(slow_query, {
                'min_time': min_execution_time,
                'limit': limit
            })
            
            slow_queries = []
            for row in result:
                slow_queries.append({
                    'id': row.id,
                    'query_text': row.query_text,
                    'generated_sql': row.generated_sql,
                    'execution_time_ms': row.execution_time_ms,
                    'row_count': row.row_count,
                    'timestamp': row.timestamp.isoformat() if row.timestamp else None
                })
            
            return slow_queries
            
        except Exception as e:
            logger.error(f"Failed to get slow queries: {e}")
            return []
        finally:
            db_session.close()
    
    async def cleanup_old_logs(self, days_old: int = 90) -> int:
        """Clean up old query logs"""
        
        db_session = next(get_vector_db())
        
        try:
            cleanup_date = datetime.now() - timedelta(days=days_old)
            
            cleanup_query = text("""
                DELETE FROM query_logs
                WHERE timestamp < :cleanup_date
            """)
            
            result = db_session.execute(cleanup_query, {'cleanup_date': cleanup_date})
            deleted_count = result.rowcount
            
            db_session.commit()
            logger.info(f"Cleaned up {deleted_count} old query logs")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Query log cleanup failed: {e}")
            db_session.rollback()
            return 0
        finally:
            db_session.close()