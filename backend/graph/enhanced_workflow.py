"""
Enhanced LangGraph workflow with better conversational abilities
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from backend.graph.state import AgentState, create_initial_state
from backend.agents.router_agent import router_agent
from backend.agents.sql_agent import sql_agent
from backend.agents.enhanced_knowledge_agent import enhanced_knowledge_agent
from backend.agents.translator_agent import translator_agent
from backend.agents.visualizer_agent import visualizer_agent
from backend.agents.utility_agent import utility_agent
from backend.llm.groq_client import groq_client
from backend.memory.enhanced_memory import enhanced_memory

def enhanced_router(state: AgentState) -> Dict[str, Any]:
    """Enhanced router with better context awareness"""
    user_query = state["user_query"]
    session_id = state["session_id"]
    
    # Get personalized context
    context = enhanced_memory.get_personalized_context(session_id)
    
    # Use router agent with enhanced context
    routing_result = router_agent(state)
    
    # Add context to state
    routing_result["conversation_context"] = context
    
    return routing_result

def enhanced_response_generator(state: AgentState) -> Dict[str, Any]:
    """
    Generate final response with conversational enhancements
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with enhanced response
    """
    query_type = state.get("query_type")
    error = state.get("error")
    session_id = state["session_id"]
    user_query = state["user_query"]
    
    # Handle errors gracefully
    if error:
        return {
            "response": generate_error_response(error, session_id),
            "response_metadata": {"error": error}
        }
    
    # Generate response based on query type
    if query_type == "data_query":
        response_data = generate_enhanced_data_response(state)
    elif query_type == "knowledge_search":
        response_data = {"response_metadata": {"type": "knowledge"}}
    elif query_type == "translation":
        response_data = {"response_metadata": {"type": "translation"}}
    elif query_type == "utility":
        response_data = {"response_metadata": {"type": "utility"}}
    else:
        response_data = {
            "response": "I'm not sure how to help with that. Could you rephrase your question?",
            "response_metadata": {"type": "unknown"}
        }
    
    # Add conversation tracking
    if "response" in response_data:
        enhanced_memory.add_message(
            session_id,
            "assistant",
            response_data["response"],
            metadata={
                "query_type": query_type,
                **response_data.get("response_metadata", {})
            }
        )
    
    return response_data

def generate_enhanced_data_response(state: AgentState) -> Dict[str, Any]:
    """Generate enhanced response for data queries with insights"""
    result_df_dict = state.get("result_dataframe")
    sql_query = state.get("sql_query")
    session_id = state["session_id"]
    user_query = state["user_query"]
    
    if not result_df_dict or not result_df_dict.get("data"):
        return {
            "response": "I couldn't find any data matching your query. Would you like to try a different question?",
            "response_metadata": {"type": "data", "has_results": False}
        }
    
    # Get user preferences for personalization
    user_prefs = enhanced_memory.get_user_preferences(session_id)
    
    # Generate natural language response with insights
    row_count = result_df_dict.get("row_count", 0)
    columns = result_df_dict.get("columns", [])
    sample_data = result_df_dict['data'][:5]
    
    # Get conversation context for continuity
    context = enhanced_memory.get_personalized_context(session_id)
    
    prompt = f"""Generate a comprehensive, conversational response to the user's query.

User Query: {user_query}
SQL Query: {sql_query}
Number of Results: {row_count}
Columns: {', '.join(columns)}
Sample Data: {sample_data}

User Context: {context}

Provide a response that:
1. Directly answers the question in natural language
2. Highlights 2-3 key insights from the data
3. Mentions interesting patterns or trends
4. Suggests related questions they might want to ask
5. Is conversational and friendly

Keep it concise but informative (3-4 sentences)."""
    
    try:
        nl_response = groq_client.generate_response(prompt, temperature=0.4, max_tokens=300)
    except Exception as e:
        nl_response = f"I found {row_count} results for your query. The data shows {', '.join(columns[:3])} information."
    
    return {
        "response": nl_response,
        "response_metadata": {
            "type": "data",
            "has_results": True,
            "row_count": row_count,
            "insights_generated": True
        }
    }

def generate_error_response(error: str, session_id: str) -> str:
    """Generate helpful error response"""
    user_prefs = enhanced_memory.get_user_preferences(session_id)
    interactions = user_prefs.get('total_interactions', 0)
    
    if interactions > 5:
        # Experienced user - more technical
        return f"""I encountered an issue: {error}

Let me help you troubleshoot:
- Check if your query is specific enough
- Try rephrasing with different keywords
- Ask for help if you need guidance on query format

What would you like to try?"""
    else:
        # New user - more guidance
        return f"""I had trouble with that request. 

Don't worry! Here's what you can try:
- Ask about sales, orders, or products
- Request translations of Portuguese terms
- Ask for help to see what I can do

What would you like to explore?"""

def route_query(state: AgentState) -> str:
    """Determine which agent to route to"""
    query_type = state.get("query_type", "utility")
    
    if query_type == "data_query":
        return "sql_agent"
    elif query_type == "knowledge_search":
        return "knowledge_agent"
    elif query_type == "translation":
        return "translator_agent"
    elif query_type == "utility":
        return "utility_agent"
    else:
        return "utility_agent"

def create_enhanced_workflow() -> StateGraph:
    """Create enhanced workflow graph"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("router", enhanced_router)
    workflow.add_node("sql_agent", sql_agent)
    workflow.add_node("knowledge_agent", enhanced_knowledge_agent)
    workflow.add_node("translator_agent", translator_agent)
    workflow.add_node("utility_agent", utility_agent)
    workflow.add_node("visualizer", visualizer_agent)
    workflow.add_node("response_generator", enhanced_response_generator)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add conditional routing
    workflow.add_conditional_edges(
        "router",
        route_query,
        {
            "sql_agent": "sql_agent",
            "knowledge_agent": "knowledge_agent",
            "translator_agent": "translator_agent",
            "utility_agent": "utility_agent"
        }
    )
    
    # SQL agent -> visualizer -> response
    workflow.add_edge("sql_agent", "visualizer")
    workflow.add_edge("visualizer", "response_generator")
    
    # Other agents -> response
    workflow.add_edge("knowledge_agent", "response_generator")
    workflow.add_edge("translator_agent", "response_generator")
    workflow.add_edge("utility_agent", "response_generator")
    
    # Response generator -> END
    workflow.add_edge("response_generator", END)
    
    return workflow.compile()

# Create enhanced workflow instance
enhanced_agent_workflow = create_enhanced_workflow()

async def process_enhanced_query(
    query: str,
    session_id: str = "default"
) -> Dict[str, Any]:
    """
    Process query through enhanced workflow
    
    Args:
        query: User query
        session_id: Session identifier
        
    Returns:
        Response dictionary
    """
    # Add user message to memory
    enhanced_memory.add_message(
        session_id,
        "user",
        query,
        metadata={"timestamp": "now"}
    )
    
    # Create initial state
    initial_state = create_initial_state(query, session_id)
    
    # Run workflow
    try:
        result = await enhanced_agent_workflow.ainvoke(initial_state)
        return result
    except Exception as e:
        error_response = f"I encountered an error processing your request: {str(e)}"
        enhanced_memory.add_message(
            session_id,
            "assistant",
            error_response,
            metadata={"error": True}
        )
        return {
            "response": error_response,
            "error": str(e)
        }
