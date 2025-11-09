"""
Knowledge Agent - Performs web search and RAG
"""
from typing import Dict, Any, List
import chromadb
from backend.graph.state import AgentState
from backend.llm.groq_client import groq_client
from backend.llm.embeddings import embedding_generator
from backend.utils.web_search import web_search
from backend.config import settings

def knowledge_agent(state: AgentState) -> Dict[str, Any]:
    """
    Search external knowledge sources
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with search results
    """
    user_query = state["user_query"]
    
    # Perform web search
    search_results = []
    if settings.ENABLE_WEB_SEARCH:
        try:
            search_results = web_search(user_query, max_results=3)
        except Exception as e:
            print(f"Web search error: {str(e)}")
    
    # Perform RAG search
    rag_results = []
    try:
        rag_results = search_vector_store(user_query)
    except Exception as e:
        print(f"RAG search error: {str(e)}")
    
    # Generate response from search results
    response = generate_knowledge_response(user_query, search_results, rag_results)
    
    return {
        "search_results": search_results,
        "rag_results": rag_results,
        "response": response
    }

def search_vector_store(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search vector store for relevant products
    
    Args:
        query: Search query
        top_k: Number of results to return
        
    Returns:
        List of relevant results
    """
    try:
        # Connect to ChromaDB
        chroma_client = chromadb.PersistentClient(path=str(settings.VECTOR_DB_PATH))
        collection = chroma_client.get_collection(name="products")
        
        # Generate query embedding
        query_embedding = embedding_generator.generate_embedding(query)
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "document": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })
        
        return formatted_results
    
    except Exception as e:
        print(f"Vector search error: {str(e)}")
        return []

def generate_knowledge_response(
    query: str,
    search_results: List[Dict[str, Any]],
    rag_results: List[Dict[str, Any]]
) -> str:
    """
    Generate response from knowledge sources
    
    Args:
        query: User query
        search_results: Web search results
        rag_results: RAG search results
        
    Returns:
        Generated response
    """
    # Prepare context
    context = "Based on available information:\n\n"
    
    if search_results:
        context += "Web Search Results:\n"
        for i, result in enumerate(search_results[:3], 1):
            context += f"{i}. {result['title']}\n"
            context += f"   {result['snippet']}\n\n"
    
    if rag_results:
        context += "Product Information:\n"
        for i, result in enumerate(rag_results[:3], 1):
            context += f"{i}. {result['document']}\n"
    
    # Generate response
    prompt = f"""Answer the user's question using the provided context.
    
Context:
{context}

Question: {query}

Provide a clear, concise answer based on the context. If the context doesn't contain relevant information, say so."""

    try:
        response = groq_client.generate_response(prompt, temperature=0.3)
        return response
    except Exception as e:
        return f"I found some information but encountered an error generating the response: {str(e)}"
