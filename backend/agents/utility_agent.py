"""
Utility Agent - Handles definitions, lookups, greetings, and helper functions
"""
from typing import Dict, Any, Optional
import re
from datetime import datetime
from backend.graph.state import AgentState
from backend.llm.groq_client import groq_client
from backend.memory.enhanced_memory import enhanced_memory
from backend.utils.web_search import web_search

def utility_agent(state: AgentState) -> Dict[str, Any]:
    """
    Handle utility queries like greetings, help, definitions, etc.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with utility response
    """
    user_query = state["user_query"].lower()
    session_id = state["session_id"]
    
    # Get user profile for personalization
    user_profile = enhanced_memory.get_user_preferences(session_id)
    
    # Detect utility type
    if any(word in user_query for word in ['hello', 'hi', 'hey', 'olá', 'oi']):
        response = handle_greeting(session_id, user_profile)
    
    elif any(word in user_query for word in ['help', 'what can you', 'capabilities', 'ajuda']):
        response = handle_help_request(user_profile)
    
    elif any(word in user_query for word in ['define', 'definition', 'what is', 'what are', 'o que é']):
        response = handle_definition(user_query)
    
    elif any(word in user_query for word in ['time', 'date', 'today', 'now', 'hora', 'data']):
        response = handle_time_date()
    
    elif any(word in user_query for word in ['thank', 'thanks', 'obrigad']):
        response = handle_thanks()
    
    elif 'location' in user_query or 'where' in user_query or 'onde' in user_query:
        response = handle_location_query(user_query)
    
    else:
        # General conversational response
        response = handle_general_conversation(user_query, session_id)
    
    return {
        "response": response,
        "utility_type": "conversational"
    }

def handle_greeting(session_id: str, user_profile: Dict[str, Any]) -> str:
    """Handle greeting with personalization"""
    interactions = user_profile.get('total_interactions', 0)
    
    if interactions == 0:
        return """Hello! 👋 Welcome to the E-commerce Intelligence Agent!

I'm here to help you analyze Brazilian e-commerce data and answer your questions. I can:

📊 **Analyze Data**: Query sales, orders, customers, products, and reviews
🔍 **Search Knowledge**: Find information about products and categories
🌐 **Translate**: Convert Portuguese category names to English
📍 **Provide Insights**: Help you understand trends and patterns

What would you like to explore today?"""
    
    elif interactions < 5:
        return f"""Hello again! 👋 

Welcome back! I see you've been exploring the data. What would you like to know today?"""
    
    else:
        # Returning user - more personalized
        topics = user_profile.get('topics_of_interest', {})
        if topics:
            top_topic = max(topics.items(), key=lambda x: x[1])[0]
            return f"""Welcome back! 👋

Great to see you again! Last time we were exploring {top_topic} data. Would you like to continue, or shall we look at something new?"""
        else:
            return """Welcome back! 👋 Ready to dive into more data insights?"""

def handle_help_request(user_profile: Dict[str, Any]) -> str:
    """Provide help information"""
    return """🤖 **E-commerce Intelligence Agent - Capabilities**

**📊 Data Analysis**
- Sales trends and revenue analysis
- Top products and categories
- Customer behavior patterns
- Delivery time analysis
- Review sentiment insights

**🔍 Knowledge Search**
- Product category information
- Market trends and insights
- External knowledge lookup

**🌐 Translation**
- Portuguese ↔ English category names
- Product descriptions

**📍 Location Services**
- Order location tracking
- Geographic distribution analysis
- Delivery route insights

**💡 Smart Features**
- Conversational context memory
- Personalized recommendations
- Multi-turn dialogues
- Data visualization

**Example Queries:**
- "Show me top 10 products by revenue"
- "What's the average delivery time?"
- "Translate 'cama_mesa_banho' to English"
- "Tell me about furniture products"
- "Where are most orders from?"

Just ask me anything! I'll understand and help you out. 😊"""

def handle_definition(query: str) -> str:
    """Handle definition requests"""
    # Extract the term to define
    patterns = [
        r'define\s+(.+)',
        r'definition\s+of\s+(.+)',
        r'what\s+is\s+(.+)',
        r'what\s+are\s+(.+)',
        r'o\s+que\s+é\s+(.+)'
    ]
    
    term = None
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            term = match.group(1).strip('?').strip()
            break
    
    if not term:
        return "I'd be happy to define something for you! What term would you like me to explain?"
    
    # Use LLM to provide definition
    prompt = f"""Provide a clear, concise definition of "{term}" in the context of e-commerce and business analytics.

Keep it brief (2-3 sentences) and practical."""
    
    try:
        definition = groq_client.generate_response(prompt, temperature=0.3, max_tokens=150)
        return f"**Definition of '{term}':**\n\n{definition}"
    except Exception as e:
        return f"I encountered an error looking up the definition: {str(e)}"

def handle_time_date() -> str:
    """Handle time and date queries"""
    now = datetime.now()
    
    return f"""⏰ **Current Date & Time**

📅 Date: {now.strftime('%B %d, %Y')}
🕐 Time: {now.strftime('%I:%M %p')}
📆 Day: {now.strftime('%A')}

Is there anything specific you'd like to know about dates in the dataset?"""

def handle_thanks() -> str:
    """Handle thank you messages"""
    responses = [
        "You're welcome! 😊 Happy to help! Anything else you'd like to know?",
        "My pleasure! Feel free to ask if you need anything else!",
        "Glad I could help! What else can I do for you?",
        "You're welcome! I'm here whenever you need data insights! 📊"
    ]
    
    import random
    return random.choice(responses)

def handle_location_query(query: str) -> str:
    """Handle location-related queries"""
    if 'order' in query or 'delivery' in query or 'shipping' in query:
        return """📍 **Location & Delivery Information**

I can help you analyze:
- Geographic distribution of orders
- Delivery times by region
- Top cities for orders
- Shipping patterns

Try asking:
- "Show orders by state"
- "Which cities have the most orders?"
- "Average delivery time by location"
- "Map of customer distribution"

What specific location data would you like to see?"""
    
    else:
        # General location query - use web search
        try:
            results = web_search(query, max_results=2)
            if results:
                response = f"**Location Information:**\n\n"
                for result in results[:2]:
                    response += f"📍 {result['title']}\n{result['snippet']}\n\n"
                return response
            else:
                return "I couldn't find specific location information. Could you provide more details?"
        except:
            return "I can help with location queries! Please provide more specific details about what you're looking for."

def handle_general_conversation(query: str, session_id: str) -> str:
    """Handle general conversational queries"""
    # Get conversation context
    context = enhanced_memory.get_personalized_context(session_id)
    
    system_prompt = """You are a helpful, friendly AI assistant for an e-commerce analytics platform.
    
Be conversational, warm, and helpful. Keep responses concise but informative.
If the user's query is unclear, ask clarifying questions.
Always relate responses back to e-commerce data analysis when relevant."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context: {context}\n\nUser: {query}"}
    ]
    
    try:
        response = groq_client.chat_completion(messages=messages, temperature=0.7, max_tokens=300)
        return response.choices[0].message.content
    except Exception as e:
        return f"I'm here to help! Could you rephrase your question or ask about specific data you'd like to analyze?"
