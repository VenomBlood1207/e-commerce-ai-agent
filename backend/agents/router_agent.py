"""
Router Agent - Classifies user queries and determines routing
"""
from typing import Dict, Any
from backend.graph.state import AgentState
from backend.llm.groq_client import groq_client
from backend.memory.conversation_memory import conversation_memory

def router_agent(state: AgentState) -> Dict[str, Any]:
    """
    Route user query to appropriate agent
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with query classification
    """
    user_query = state["user_query"]
    session_id = state["session_id"]
    
    # Get conversation context
    context = conversation_memory.get_context_summary(session_id)
    
    # Classification prompt
    system_prompt = """You are a query router for an e-commerce analytics system.
    
Classify the user's query into ONE of these categories:

1. **data_query**: Questions about sales, orders, customers, products, reviews, etc. that require database queries
   Examples: "Show top products", "What's the average delivery time?", "Revenue by category"

2. **knowledge_search**: Questions requiring external knowledge or product information
   Examples: "Tell me about this product category", "What is cama_mesa_banho?", "Current trends in furniture"

3. **translation**: Translation requests between Portuguese and English
   Examples: "Translate moveis_decoracao", "What does this category mean in English?"

4. **utility**: Greetings, help requests, or system queries
   Examples: "Hello", "What can you do?", "Help me"

Respond with ONLY the category name, nothing else."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context: {context}\n\nQuery: {user_query}"}
    ]
    
    try:
        response = groq_client.chat_completion(
            messages=messages,
            temperature=0.0,
            max_tokens=50
        )
        
        query_type = response.choices[0].message.content.strip().lower()
        
        # Validate query type
        valid_types = ['data_query', 'knowledge_search', 'translation', 'utility']
        if query_type not in valid_types:
            # Default to data_query if unclear
            query_type = 'data_query'
        
        return {
            "query_type": query_type,
            "conversation_context": context
        }
    
    except Exception as e:
        return {
            "query_type": "data_query",  # Default fallback
            "error": f"Router error: {str(e)}"
        }
