"""
State management for LangGraph workflow
"""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import add_messages
import operator

class AgentState(TypedDict):
    """State for the agent workflow"""
    
    # User input and session
    user_query: str
    session_id: str
    
    # Conversation history
    messages: Annotated[List[Dict[str, str]], add_messages]
    
    # Query classification
    query_type: Optional[str]  # 'data_query', 'knowledge_search', 'translation', 'utility'
    intent: Optional[str]
    
    # SQL generation and execution
    sql_query: Optional[str]
    query_result: Optional[Any]
    result_dataframe: Optional[Dict[str, Any]]
    
    # Knowledge search
    search_query: Optional[str]
    search_results: Optional[List[Dict[str, Any]]]
    rag_results: Optional[List[Dict[str, Any]]]
    
    # Translation
    source_language: Optional[str]
    target_language: Optional[str]
    translated_text: Optional[str]
    
    # Visualization
    chart_type: Optional[str]
    chart_data: Optional[Dict[str, Any]]
    
    # Response generation
    response: Optional[str]
    response_metadata: Optional[Dict[str, Any]]
    
    # Error handling
    error: Optional[str]
    retry_count: int
    
    # Context
    conversation_context: Optional[str]
    previous_results: Optional[List[Dict[str, Any]]]

def create_initial_state(user_query: str, session_id: str) -> AgentState:
    """
    Create initial state for workflow
    
    Args:
        user_query: User's query
        session_id: Session identifier
        
    Returns:
        Initial agent state
    """
    return AgentState(
        user_query=user_query,
        session_id=session_id,
        messages=[],
        query_type=None,
        intent=None,
        sql_query=None,
        query_result=None,
        result_dataframe=None,
        search_query=None,
        search_results=None,
        rag_results=None,
        source_language=None,
        target_language=None,
        translated_text=None,
        chart_type=None,
        chart_data=None,
        response=None,
        response_metadata=None,
        error=None,
        retry_count=0,
        conversation_context=None,
        previous_results=None
    )
