"""
Test script for agent system
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.graph.workflow import process_query
from backend.config import settings

async def test_query(query: str, session_id: str = "test"):
    """Test a single query"""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    try:
        result = await process_query(query, session_id)
        
        print(f"\nQuery Type: {result.get('query_type')}")
        
        if result.get('sql_query'):
            print(f"\nSQL Query:\n{result.get('sql_query')}")
        
        if result.get('result_dataframe'):
            data = result.get('result_dataframe')
            print(f"\nResults: {data.get('row_count')} rows")
        
        print(f"\nResponse:\n{result.get('response')}")
        
        if result.get('error'):
            print(f"\n⚠ Error: {result.get('error')}")
        
        return result
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None

async def main():
    """Run test queries"""
    print("=" * 60)
    print("Agent System Test Suite")
    print("=" * 60)
    
    # Check if API key is set
    if not settings.GROQ_API_KEY:
        print("\n❌ GROQ_API_KEY not set in environment")
        print("Please set your Groq API key in .env file")
        return
    
    print(f"\n✓ Groq API Key: {'*' * 20}{settings.GROQ_API_KEY[-4:]}")
    
    # Test queries
    test_queries = [
        # Data queries
        "What are the top 5 product categories by sales?",
        "Show me average delivery time by state",
        "Which sellers have the highest ratings?",
        
        # Translation
        "Translate 'cama_mesa_banho' to English",
        
        # Knowledge search
        "What is the population of São Paulo?",
        
        # Utility
        "Hello, what can you do?"
    ]
    
    session_id = "test_session"
    
    for query in test_queries:
        await test_query(query, session_id)
        await asyncio.sleep(1)  # Rate limiting
    
    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
