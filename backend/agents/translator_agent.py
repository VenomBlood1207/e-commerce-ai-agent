"""
Translator Agent - Handles translation between Portuguese and English
"""
from typing import Dict, Any
from backend.graph.state import AgentState
from backend.llm.groq_client import groq_client
from backend.database.connection import db_manager

def translator_agent(state: AgentState) -> Dict[str, Any]:
    """
    Translate text between Portuguese and English
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with translation
    """
    user_query = state["user_query"]
    
    # Check if it's a category translation request
    category_translation = check_category_translation(user_query)
    if category_translation:
        return {
            "response": category_translation,
            "translated_text": category_translation
        }
    
    # General translation
    system_prompt = """You are a translator specializing in Portuguese and English.
    
Translate the user's text accurately. If the text is in Portuguese, translate to English.
If it's in English, translate to Portuguese. Provide ONLY the translation."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    
    try:
        response = groq_client.chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=512
        )
        
        translation = response.choices[0].message.content.strip()
        
        return {
            "translated_text": translation,
            "response": translation
        }
    
    except Exception as e:
        return {
            "error": f"Translation error: {str(e)}",
            "response": "I encountered an error while translating. Please try again."
        }

def check_category_translation(query: str) -> str:
    """
    Check if query is asking for category translation
    
    Args:
        query: User query
        
    Returns:
        Translation if found, empty string otherwise
    """
    # Extract potential category name
    query_lower = query.lower()
    
    # Common patterns
    patterns = [
        "translate", "what does", "what is", "meaning of",
        "in english", "in portuguese", "category"
    ]
    
    if not any(pattern in query_lower for pattern in patterns):
        return ""
    
    try:
        # Try to find category in database
        # Extract words that might be category names
        words = query.split()
        for word in words:
            clean_word = word.strip('"\',.:;?!')
            if len(clean_word) > 3:
                # Check in database
                sql = f"""
                    SELECT product_category_name, product_category_name_english
                    FROM product_category_name_translation
                    WHERE product_category_name LIKE '%{clean_word}%'
                       OR product_category_name_english LIKE '%{clean_word}%'
                    LIMIT 1
                """
                result = db_manager.execute_query(sql)
                
                if not result.empty:
                    pt_name = result['product_category_name'].iloc[0]
                    en_name = result['product_category_name_english'].iloc[0]
                    return f"'{pt_name}' in Portuguese means '{en_name}' in English."
    
    except Exception as e:
        print(f"Category translation lookup error: {str(e)}")
    
    return ""
