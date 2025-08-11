from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import uuid
import logging
from datetime import datetime

from app.models.schemas import ChatMessage, ChatSession, QueryRequest
from app.services.ai_service import AIService
from app.connectors.factory import ConnectorFactory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

# In-memory storage for chat sessions (in production, use Redis or database)
active_sessions: Dict[str, ChatSession] = {}
active_connections: Dict[str, WebSocket] = {}


class ChatManager:
    def __init__(self):
        self.ai_service = AIService()
    
    async def create_session(self) -> str:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        session = ChatSession(
            session_id=session_id,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        active_sessions[session_id] = session
        return session_id
    
    async def add_message(self, session_id: str, message: ChatMessage):
        """Add a message to a chat session"""
        if session_id in active_sessions:
            active_sessions[session_id].messages.append(message)
            active_sessions[session_id].updated_at = datetime.now()
    
    async def process_user_message(self, session_id: str, user_message: str) -> ChatMessage:
        """Process user message and generate AI response"""
        try:
            # Add user message to session
            user_msg = ChatMessage(
                role="user",
                content=user_message,
                timestamp=datetime.now()
            )
            await self.add_message(session_id, user_msg)
            
            # Determine if this is a query or conversation
            is_query = await self._is_database_query(user_message)
            
            if is_query:
                # Handle as database query
                response = await self._handle_database_query(session_id, user_message)
            else:
                # Handle as general conversation
                response = await self._handle_conversation(session_id, user_message)
            
            # Add assistant response to session
            assistant_msg = ChatMessage(
                role="assistant",
                content=response["content"],
                timestamp=datetime.now(),
                metadata=response.get("metadata", {})
            )
            await self.add_message(session_id, assistant_msg)
            
            return assistant_msg
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_msg = ChatMessage(
                role="assistant",
                content=f"I encountered an error while processing your request: {str(e)}",
                timestamp=datetime.now(),
                metadata={"error": True}
            )
            await self.add_message(session_id, error_msg)
            return error_msg
    
    async def _is_database_query(self, message: str) -> bool:
        """Determine if the message is a database query"""
        # Simple heuristics - in production, use more sophisticated classification
        query_keywords = [
            "show", "list", "find", "get", "how many", "count", "sum", "average",
            "select", "from", "where", "group by", "order by", "table", "column",
            "data", "records", "rows", "database", "query"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in query_keywords)
    
    async def _handle_database_query(self, session_id: str, message: str) -> Dict[str, Any]:
        """Handle database query messages"""
        try:
            # Get database connection and schema context
            connector = ConnectorFactory.create_connector()
            if not connector.connect():
                return {
                    "content": "I'm unable to connect to the database right now. Please try again later.",
                    "metadata": {"error": True}
                }
            
            try:
                # Get schema context
                schema_context = connector.get_schema()
                
                # Generate SQL using AI
                generated_sql = await self.ai_service.generate_sql(
                    query=message,
                    schema_context=schema_context,
                    database_type=connector.config.get('type', 'postgres')
                )
                
                if not generated_sql:
                    return {
                        "content": "I couldn't understand your query. Could you please rephrase it?",
                        "metadata": {"no_sql_generated": True}
                    }
                
                # Validate query
                is_valid, validation_error = connector.validate_query(generated_sql)
                if not is_valid:
                    return {
                        "content": f"The query I generated has some issues: {validation_error}. Could you clarify your request?",
                        "metadata": {"validation_error": validation_error}
                    }
                
                # Execute query
                results_df = connector.execute_query(generated_sql, limit=100)
                
                # Generate response with insights
                insights = await self.ai_service.generate_insights(
                    query=message,
                    results=results_df,
                    sql=generated_sql
                )
                
                # Format response
                row_count = len(results_df)
                response_content = f"{insights}\n\n"
                
                if row_count > 0:
                    response_content += f"**Query Results** ({row_count} rows):\n"
                    
                    # Show first few rows as preview
                    if row_count <= 5:
                        response_content += results_df.to_string(index=False)
                    else:
                        response_content += results_df.head().to_string(index=False)
                        response_content += f"\n... and {row_count - 5} more rows"
                else:
                    response_content += "No results found."
                
                response_content += f"\n\n**Generated SQL:**\n```sql\n{generated_sql}\n```"
                
                return {
                    "content": response_content,
                    "metadata": {
                        "query_type": "database",
                        "sql": generated_sql,
                        "row_count": row_count,
                        "results": results_df.to_dict('records') if row_count <= 20 else []
                    }
                }
                
            finally:
                connector.disconnect()
                
        except Exception as e:
            logger.error(f"Database query handling failed: {e}")
            return {
                "content": f"I encountered an error while querying the database: {str(e)}",
                "metadata": {"error": True, "error_message": str(e)}
            }
    
    async def _handle_conversation(self, session_id: str, message: str) -> Dict[str, Any]:
        """Handle general conversation messages"""
        try:
            # Get conversation context from session history
            session = active_sessions.get(session_id)
            conversation_history = []
            
            if session:
                # Get last few messages for context
                recent_messages = session.messages[-10:]  # Last 10 messages
                for msg in recent_messages:
                    conversation_history.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Generate conversational response
            response = await self.ai_service.generate_conversation_response(
                message=message,
                conversation_history=conversation_history
            )
            
            return {
                "content": response,
                "metadata": {"query_type": "conversation"}
            }
            
        except Exception as e:
            logger.error(f"Conversation handling failed: {e}")
            return {
                "content": "I'm sorry, I'm having trouble understanding right now. Could you try rephrasing your question?",
                "metadata": {"error": True, "error_message": str(e)}
            }


chat_manager = ChatManager()


@router.post("/sessions")
async def create_chat_session():
    """Create a new chat session"""
    session_id = await chat_manager.create_session()
    return {
        "success": True,
        "session_id": session_id,
        "message": "Chat session created successfully"
    }


@router.get("/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Get chat session details"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    session = active_sessions[session_id]
    return {
        "success": True,
        "session": session.dict()
    }


@router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, message: Dict[str, str]):
    """Send a message to a chat session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    user_message = message.get("message", "")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Process the message and get AI response
        response_message = await chat_manager.process_user_message(session_id, user_message)
        
        return {
            "success": True,
            "response": response_message.dict()
        }
    
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    if session_id not in active_sessions:
        await websocket.send_text(json.dumps({
            "error": "Chat session not found"
        }))
        await websocket.close()
        return
    
    active_connections[session_id] = websocket
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            if not user_message:
                await websocket.send_text(json.dumps({
                    "error": "Message cannot be empty"
                }))
                continue
            
            # Process message
            response_message = await chat_manager.process_user_message(session_id, user_message)
            
            # Send response back to client
            await websocket.send_text(json.dumps({
                "type": "message",
                "data": response_message.dict()
            }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "error": str(e)
        }))
    finally:
        if session_id in active_connections:
            del active_connections[session_id]


@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Close WebSocket connection if active
    if session_id in active_connections:
        await active_connections[session_id].close()
        del active_connections[session_id]
    
    # Delete session
    del active_sessions[session_id]
    
    return {
        "success": True,
        "message": "Chat session deleted successfully"
    }