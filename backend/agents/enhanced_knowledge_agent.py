"""
Enhanced Knowledge Agent - Deep product information and external knowledge
"""
from typing import Dict, Any, List, Optional
import chromadb
from backend.graph.state import AgentState
from backend.llm.groq_client import groq_client
from backend.llm.embeddings import embedding_generator
from backend.utils.web_search import web_search
from backend.config import settings
from backend.database.connection import db_manager

def enhanced_knowledge_agent(state: AgentState) -> Dict[str, Any]:
    """
    Enhanced knowledge search with deeper product insights
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with comprehensive knowledge
    """
    user_query = state["user_query"]
    
    # Multi-source knowledge gathering
    web_results = []
    rag_results = []
    product_details = []
    category_info = None
    
    # 1. Web search for external knowledge
    if settings.ENABLE_WEB_SEARCH:
        try:
            web_results = web_search(user_query, max_results=5)
        except Exception as e:
            print(f"Web search error: {str(e)}")
    
    # 2. RAG search for product information
    try:
        rag_results = search_vector_store(user_query, top_k=10)
    except Exception as e:
        print(f"RAG search error: {str(e)}")
    
    # 3. Get detailed product information from database
    try:
        product_details = get_product_details(user_query)
    except Exception as e:
        print(f"Product details error: {str(e)}")
    
    # 4. Get category insights
    try:
        category_info = get_category_insights(user_query)
    except Exception as e:
        print(f"Category insights error: {str(e)}")
    
    # Generate comprehensive response
    response = generate_enhanced_response(
        user_query,
        web_results,
        rag_results,
        product_details,
        category_info
    )
    
    return {
        "search_results": web_results,
        "rag_results": rag_results,
        "product_details": product_details,
        "category_info": category_info,
        "response": response
    }

def search_vector_store(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """Enhanced vector store search with better ranking"""
    try:
        chroma_client = chromadb.PersistentClient(path=str(settings.VECTOR_DB_PATH))
        collection = chroma_client.get_collection(name="products")
        
        # Generate query embedding
        query_embedding = embedding_generator.generate_embedding(query)
        
        # Search with metadata filtering if applicable
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format and enrich results
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 0
                
                # Calculate relevance score (inverse of distance)
                relevance_score = 1 / (1 + distance) if distance else 1.0
                
                formatted_results.append({
                    "document": doc,
                    "metadata": metadata,
                    "distance": distance,
                    "relevance_score": relevance_score,
                    "product_id": metadata.get('product_id'),
                    "category": metadata.get('category_name')
                })
        
        # Sort by relevance
        formatted_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return formatted_results
    
    except Exception as e:
        print(f"Vector search error: {str(e)}")
        return []

def get_product_details(query: str) -> List[Dict[str, Any]]:
    """Get detailed product information from database"""
    try:
        # Extract potential product keywords
        keywords = extract_product_keywords(query)
        
        if not keywords:
            return []
        
        # Query database for matching products
        sql = f"""
        SELECT 
            p.product_id,
            p.product_category_name,
            pct.product_category_name_english,
            COUNT(DISTINCT oi.order_id) as total_orders,
            ROUND(AVG(oi.price), 2) as avg_price,
            COUNT(DISTINCT or2.review_id) as total_reviews,
            ROUND(AVG(or2.review_score), 2) as avg_rating
        FROM products p
        LEFT JOIN product_category_translation pct 
            ON p.product_category_name = pct.product_category_name
        LEFT JOIN order_items oi ON p.product_id = oi.product_id
        LEFT JOIN order_reviews or2 ON oi.order_id = or2.order_id
        WHERE p.product_category_name LIKE '%{keywords[0]}%'
           OR pct.product_category_name_english LIKE '%{keywords[0]}%'
        GROUP BY p.product_id, p.product_category_name, pct.product_category_name_english
        ORDER BY total_orders DESC
        LIMIT 10
        """
        
        result = db_manager.execute_query(sql)
        
        if result is not None and not result.empty:
            return result.to_dict('records')
        
        return []
    
    except Exception as e:
        print(f"Product details query error: {str(e)}")
        return []

def get_category_insights(query: str) -> Optional[Dict[str, Any]]:
    """Get insights about product categories"""
    try:
        # Check if query mentions a category
        keywords = extract_product_keywords(query)
        
        if not keywords:
            return None
        
        # Get category statistics
        sql = f"""
        SELECT 
            p.product_category_name,
            pct.product_category_name_english,
            COUNT(DISTINCT p.product_id) as total_products,
            COUNT(DISTINCT oi.order_id) as total_orders,
            ROUND(SUM(oi.price), 2) as total_revenue,
            ROUND(AVG(oi.price), 2) as avg_price,
            COUNT(DISTINCT or2.review_id) as total_reviews,
            ROUND(AVG(or2.review_score), 2) as avg_rating
        FROM products p
        LEFT JOIN product_category_translation pct 
            ON p.product_category_name = pct.product_category_name
        LEFT JOIN order_items oi ON p.product_id = oi.product_id
        LEFT JOIN order_reviews or2 ON oi.order_id = or2.order_id
        WHERE p.product_category_name LIKE '%{keywords[0]}%'
           OR pct.product_category_name_english LIKE '%{keywords[0]}%'
        GROUP BY p.product_category_name, pct.product_category_name_english
        LIMIT 1
        """
        
        result = db_manager.execute_query(sql)
        
        if result is not None and not result.empty:
            return result.to_dict('records')[0]
        
        return None
    
    except Exception as e:
        print(f"Category insights error: {str(e)}")
        return None

def extract_product_keywords(query: str) -> List[str]:
    """Extract potential product keywords from query"""
    # Common product categories and keywords
    product_terms = [
        'furniture', 'electronics', 'clothing', 'books', 'toys', 'sports',
        'beauty', 'health', 'home', 'garden', 'automotive', 'food',
        'moveis', 'eletronicos', 'roupa', 'livros', 'brinquedos',
        'beleza', 'saude', 'casa', 'jardim', 'cama', 'mesa', 'banho'
    ]
    
    query_lower = query.lower()
    keywords = [term for term in product_terms if term in query_lower]
    
    # Also extract quoted terms
    import re
    quoted = re.findall(r'"([^"]*)"', query)
    quoted += re.findall(r"'([^']*)'", query)
    
    keywords.extend(quoted)
    
    return keywords[:3]  # Return top 3 keywords

def generate_enhanced_response(
    query: str,
    web_results: List[Dict[str, Any]],
    rag_results: List[Dict[str, Any]],
    product_details: List[Dict[str, Any]],
    category_info: Optional[Dict[str, Any]]
) -> str:
    """Generate comprehensive response from all knowledge sources"""
    
    # Build context from all sources
    context_parts = []
    
    # Add category insights
    if category_info:
        context_parts.append(f"""**Category Overview:**
- Category: {category_info.get('product_category_name_english', 'N/A')}
- Total Products: {category_info.get('total_products', 0)}
- Total Orders: {category_info.get('total_orders', 0)}
- Total Revenue: ${category_info.get('total_revenue', 0):,.2f}
- Average Price: ${category_info.get('avg_price', 0):.2f}
- Average Rating: {category_info.get('avg_rating', 0):.1f}/5.0
""")
    
    # Add product details
    if product_details:
        context_parts.append("\n**Top Products in this Category:**")
        for i, product in enumerate(product_details[:5], 1):
            context_parts.append(
                f"{i}. {product.get('product_category_name_english', 'N/A')} - "
                f"Orders: {product.get('total_orders', 0)}, "
                f"Avg Price: ${product.get('avg_price', 0):.2f}, "
                f"Rating: {product.get('avg_rating', 0):.1f}/5"
            )
    
    # Add RAG results
    if rag_results:
        context_parts.append("\n**Product Information from Database:**")
        for i, result in enumerate(rag_results[:3], 1):
            context_parts.append(f"{i}. {result['document']}")
    
    # Add web search results
    if web_results:
        context_parts.append("\n**External Information:**")
        for i, result in enumerate(web_results[:3], 1):
            context_parts.append(f"{i}. {result['title']}: {result['snippet']}")
    
    context = "\n".join(context_parts)
    
    # Generate response using LLM
    prompt = f"""You are an e-commerce expert. Answer the user's question using the provided comprehensive information.

Question: {query}

Available Information:
{context}

Provide a detailed, informative answer that:
1. Directly answers the question
2. Includes relevant statistics and insights
3. Provides context and explanations
4. Suggests related information the user might find useful

Keep the tone professional but friendly."""
    
    try:
        response = groq_client.generate_response(prompt, temperature=0.4, max_tokens=500)
        return response
    except Exception as e:
        # Fallback to structured response
        if context_parts:
            return "\n".join(context_parts)
        return "I found some information but encountered an error generating a detailed response. Please try rephrasing your question."
