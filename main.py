"""
FastAPI server for E-commerce Intelligence Agent
"""
# IMPORTANT: This must be imported FIRST to fix Python 3.12 compatibility
import fix_pydantic

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import asyncio
import json
from datetime import datetime

from backend.config import settings
from backend.graph.workflow import process_query, agent_workflow
from backend.graph.enhanced_workflow import process_enhanced_query, enhanced_agent_workflow
from backend.memory.conversation_memory import conversation_memory
from backend.memory.enhanced_memory import enhanced_memory
from backend.database.connection import db_manager

# Create FastAPI app
app = FastAPI(
    title="E-commerce Intelligence Agent",
    description="GenAI-powered conversational analytics for Brazilian e-commerce data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"

class QueryResponse(BaseModel):
    response: str
    query_type: Optional[str] = None
    sql_query: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    chart_type: Optional[str] = None
    chart_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class ConversationHistory(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "E-commerce Intelligence Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        tables = db_manager.get_all_tables()
        
        return {
            "status": "healthy",
            "database": "connected",
            "tables": len(tables),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Process a user query
    
    Args:
        request: Query request with user query and session ID
        
    Returns:
        Query response with results
    """
    try:
        # Process query
        result = await process_query(request.query, request.session_id)
        
        return QueryResponse(
            response=result.get("response", ""),
            query_type=result.get("query_type"),
            sql_query=result.get("sql_query"),
            result_data=result.get("result_dataframe"),
            chart_type=result.get("chart_type"),
            chart_data=result.get("chart_data"),
            error=result.get("error"),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/{session_id}", response_model=ConversationHistory)
async def get_conversation(session_id: str, limit: Optional[int] = 20):
    """
    Get conversation history for a session
    
    Args:
        session_id: Session identifier
        limit: Maximum number of messages to return
        
    Returns:
        Conversation history
    """
    try:
        history = conversation_memory.get_history(session_id, limit=limit)
        
        return ConversationHistory(
            session_id=session_id,
            messages=history
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """
    Clear conversation history for a session
    
    Args:
        session_id: Session identifier
        
    Returns:
        Success message
    """
    try:
        conversation_memory.clear_session(session_id)
        return {"message": f"Conversation history cleared for session {session_id}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/enhanced", response_model=QueryResponse)
async def enhanced_query_endpoint(request: QueryRequest):
    """
    Process a user query with enhanced conversational features
    
    Args:
        request: Query request with user query and session ID
        
    Returns:
        Enhanced query response with personalization
    """
    try:
        # Process query with enhanced workflow
        result = await process_enhanced_query(request.query, request.session_id)
        
        return QueryResponse(
            response=result.get("response", ""),
            query_type=result.get("query_type"),
            sql_query=result.get("sql_query"),
            result_data=result.get("result_dataframe"),
            chart_type=result.get("chart_type"),
            chart_data=result.get("chart_data"),
            error=result.get("error"),
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}/profile")
async def get_session_profile(session_id: str):
    """
    Get user profile and preferences for a session
    
    Args:
        session_id: Session identifier
        
    Returns:
        User profile and statistics
    """
    try:
        profile = enhanced_memory.get_user_preferences(session_id)
        stats = enhanced_memory.get_session_stats(session_id)
        
        return {
            "session_id": session_id,
            "profile": profile,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        tables = db_manager.get_all_tables()
        table_stats = {}
        
        for table in tables:
            query = f"SELECT COUNT(*) as count FROM {table}"
            result = db_manager.execute_query(query)
            table_stats[table] = result['count'].iloc[0]
        
        return {
            "tables": table_stats,
            "active_sessions": conversation_memory.get_session_count(),
            "enhanced_sessions": len(enhanced_memory.user_profiles),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time streaming
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
    """
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            query = message.get("query", "")
            
            if not query:
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": "No query provided"
                })
                continue
            
            # Send processing status
            await manager.send_message(session_id, {
                "type": "status",
                "message": "Processing your query..."
            })
            
            # Process query
            try:
                result = await process_query(query, session_id)
                
                # Send result
                await manager.send_message(session_id, {
                    "type": "result",
                    "data": {
                        "response": result.get("response", ""),
                        "query_type": result.get("query_type"),
                        "sql_query": result.get("sql_query"),
                        "result_data": result.get("result_dataframe"),
                        "chart_type": result.get("chart_type"),
                        "chart_data": result.get("chart_data"),
                        "error": result.get("error")
                    }
                })
            
            except Exception as e:
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": str(e)
                })
    
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(session_id)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("=" * 60)
    print("E-commerce Intelligence Agent Starting...")
    print("=" * 60)
    
    # Check database
    try:
        tables = db_manager.get_all_tables()
        print(f"✓ Database connected: {len(tables)} tables found")
    except Exception as e:
        print(f"⚠ Database warning: {str(e)}")
    
    print(f"✓ Server running on http://{settings.HOST}:{settings.PORT}")
    print(f"✓ API docs available at http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 60)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\nShutting down E-commerce Intelligence Agent...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
