import google.generativeai as genai
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
import json
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """AI service for SQL generation, insights, and conversations"""
    
    def __init__(self):
        self.api_key = settings.google_api_key
        if not self.api_key:
            raise ValueError("Google API key is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize LangChain with Gemini
        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=self.api_key,
            temperature=0.1,  # Lower temperature for more deterministic SQL generation
            top_p=0.8
        )
        
        self.conversation_llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=self.api_key,
            temperature=0.7,  # Higher temperature for more creative conversations
            top_p=0.9
        )
    
    async def generate_sql(self, query: str, schema_context: Dict[str, Any], database_type: str = "postgres") -> Optional[str]:
        """Generate SQL query from natural language"""
        
        try:
            # Prepare schema context for the prompt
            schema_description = self._format_schema_context(schema_context)
            
            # Create SQL generation prompt
            sql_prompt = PromptTemplate(
                input_variables=["query", "schema", "database_type"],
                template="""
You are an expert SQL query generator for {database_type} databases. 
Your task is to convert natural language queries into safe, optimized SQL queries.

Database Schema:
{schema}

Rules:
1. Only generate SELECT statements - never INSERT, UPDATE, DELETE, DROP, or ALTER
2. Use proper {database_type} SQL syntax and functions
3. Include appropriate JOINs when querying multiple tables
4. Add reasonable LIMIT clauses for large result sets (default 1000 unless specified)
5. Use proper column aliases for readability
6. Apply WHERE clauses to filter data efficiently
7. If the query is ambiguous, make reasonable assumptions and add comments

User Query: {query}

Generate only the SQL query, no explanation:
"""
            )
            
            # Create LangChain chain
            sql_chain = LLMChain(llm=self.llm, prompt=sql_prompt)
            
            # Generate SQL
            result = await sql_chain.arun(
                query=query,
                schema=schema_description,
                database_type=database_type
            )
            
            # Clean up the result (remove markdown formatting if present)
            sql_query = self._clean_sql_output(result)
            
            logger.info(f"Generated SQL for query '{query}': {sql_query}")
            return sql_query
            
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return None
    
    async def generate_insights(self, query: str, results: pd.DataFrame, sql: str) -> str:
        """Generate insights from query results"""
        
        try:
            # Prepare results summary
            results_summary = self._summarize_results(results)
            
            # Create insights prompt
            insights_prompt = PromptTemplate(
                input_variables=["query", "sql", "results_summary"],
                template="""
You are a data analyst providing insights based on query results.

Original Question: {query}
SQL Query: {sql}
Results Summary: {results_summary}

Provide a concise, business-focused analysis including:
1. Key findings from the data
2. Notable patterns or trends
3. Data quality observations (if any)
4. Suggested follow-up questions or analyses

Keep the response conversational and under 200 words:
"""
            )
            
            insights_chain = LLMChain(llm=self.conversation_llm, prompt=insights_prompt)
            
            insights = await insights_chain.arun(
                query=query,
                sql=sql,
                results_summary=results_summary
            )
            
            return insights.strip()
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            return "I found the data you requested. The results are displayed above."
    
    async def generate_conversation_response(self, message: str, conversation_history: List[Dict[str, str]]) -> str:
        """Generate conversational response for general chat"""
        
        try:
            # Build conversation context
            context = "\n".join([
                f"{msg['role'].capitalize()}: {msg['content']}"
                for msg in conversation_history[-5:]  # Last 5 messages for context
            ])
            
            conversation_prompt = PromptTemplate(
                input_variables=["message", "context"],
                template="""
You are Warehouse Copilot, an AI assistant that helps users explore and analyze their data.

You can help users:
- Write and execute SQL queries
- Understand database schemas
- Analyze query results
- Explore data relationships
- Answer questions about data analysis

Recent conversation context:
{context}

Current message: {message}

Respond in a helpful, conversational tone. If the message seems like it might be related to data or databases, guide the user toward asking specific questions about their data:
"""
            )
            
            conv_chain = LLMChain(llm=self.conversation_llm, prompt=conversation_prompt)
            
            response = await conv_chain.arun(
                message=message,
                context=context
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Conversation response generation failed: {e}")
            return "I'm here to help you explore and analyze your data. What would you like to know?"
    
    def _format_schema_context(self, schema_context: Dict[str, Any]) -> str:
        """Format schema context for prompts"""
        
        if not schema_context:
            return "No schema information available."
        
        formatted_schema = []
        
        for table_name, table_info in schema_context.items():
            columns = table_info.get('columns', [])
            
            if isinstance(columns, list) and columns:
                column_descriptions = []
                for col in columns[:10]:  # Limit to first 10 columns per table
                    if isinstance(col, dict):
                        col_name = col.get('name', 'unknown')
                        col_type = col.get('type', 'unknown')
                        col_nullable = ' (nullable)' if col.get('nullable', True) else ' (not null)'
                        col_desc = f"  {col_name}: {col_type}{col_nullable}"
                        if col.get('description'):
                            col_desc += f" - {col['description']}"
                        column_descriptions.append(col_desc)
                
                table_desc = f"Table: {table_name}\n" + "\n".join(column_descriptions)
                formatted_schema.append(table_desc)
        
        return "\n\n".join(formatted_schema) if formatted_schema else "No tables found in schema."
    
    def _summarize_results(self, results: pd.DataFrame) -> str:
        """Summarize DataFrame results for insights generation"""
        
        if results.empty:
            return "No results found."
        
        summary_parts = [
            f"Results: {len(results)} rows, {len(results.columns)} columns"
        ]
        
        # Column information
        columns = results.columns.tolist()
        summary_parts.append(f"Columns: {', '.join(columns[:5])}" + ("..." if len(columns) > 5 else ""))
        
        # Sample data (first few rows)
        if len(results) > 0:
            # Convert first few rows to a readable format
            sample_data = results.head(3).to_dict('records')
            summary_parts.append(f"Sample data: {sample_data}")
        
        # Basic statistics for numeric columns
        numeric_cols = results.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats = []
            for col in numeric_cols[:3]:  # First 3 numeric columns
                col_stats = results[col].describe()
                stats.append(f"{col}: mean={col_stats['mean']:.2f}, min={col_stats['min']:.2f}, max={col_stats['max']:.2f}")
            if stats:
                summary_parts.append("Numeric stats: " + "; ".join(stats))
        
        return ". ".join(summary_parts)
    
    def _clean_sql_output(self, sql_output: str) -> str:
        """Clean up SQL output from the AI model"""
        
        # Remove markdown code blocks
        sql_output = sql_output.strip()
        if sql_output.startswith('```sql'):
            sql_output = sql_output[6:]
        if sql_output.startswith('```'):
            sql_output = sql_output[3:]
        if sql_output.endswith('```'):
            sql_output = sql_output[:-3]
        
        # Remove extra whitespace
        sql_output = sql_output.strip()
        
        # Ensure it ends with semicolon
        if sql_output and not sql_output.endswith(';'):
            sql_output += ';'
        
        return sql_output
    
    async def enhance_schema_with_ai(self, schema_context: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to enhance schema with descriptions and relationships"""
        
        try:
            # Create prompt for schema enhancement
            enhance_prompt = PromptTemplate(
                input_variables=["schema"],
                template="""
Analyze this database schema and provide insights:

Schema:
{schema}

Please provide:
1. Business purpose of each table (infer from table and column names)
2. Likely relationships between tables (even if not explicitly defined)
3. Potential data quality issues to watch for
4. Suggestions for common queries users might want to run

Format as JSON:
"""
            )
            
            enhance_chain = LLMChain(llm=self.llm, prompt=enhance_prompt)
            
            schema_description = self._format_schema_context(schema_context)
            
            enhancement = await enhance_chain.arun(schema=schema_description)
            
            try:
                enhanced_info = json.loads(enhancement)
                return enhanced_info
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw text
                return {"ai_analysis": enhancement}
            
        except Exception as e:
            logger.error(f"Schema enhancement failed: {e}")
            return {"error": str(e)}