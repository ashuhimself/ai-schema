from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd


class BaseConnector(ABC):
    """Abstract base class for database connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the database"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close the database connection"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Execute a SQL query and return results as DataFrame"""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        pass
    
    @abstractmethod
    def get_tables(self) -> List[str]:
        """Get list of available tables"""
        pass
    
    @abstractmethod
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific table"""
        pass
    
    @abstractmethod
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate if query is safe to execute"""
        pass
    
    @abstractmethod
    def get_query_plan(self, query: str) -> str:
        """Get execution plan for a query"""
        pass
    
    @abstractmethod
    def estimate_query_cost(self, query: str) -> Dict[str, Any]:
        """Estimate the cost/resources needed for query execution"""
        pass
    
    def is_connected(self) -> bool:
        """Check if connection is active"""
        return self.connection is not None
    
    def format_error(self, error: Exception) -> str:
        """Format database error for user display"""
        return f"Database error: {str(error)}"