"""
SQL Agent - Generates and executes SQL queries
"""
from typing import Dict, Any
import pandas as pd
from backend.graph.state import AgentState
from backend.llm.groq_client import groq_client
from backend.database.connection import db_manager
from backend.database.queries import get_schema_description, get_example_queries
from backend.utils.helpers import format_dataframe_for_display, clean_sql_query

def sql_agent(state: AgentState) -> Dict[str, Any]:
    """
    Generate and execute SQL query
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with query results
    """
    user_query = state["user_query"]
    context = state.get("conversation_context", "")
    
    # Get schema and examples
    schema_info = get_schema_description()
    examples = get_example_queries()
    
    # Generate SQL query
    try:
        sql_query = groq_client.generate_sql(
            question=f"{context}\n\nCurrent question: {user_query}",
            schema_info=schema_info,
            examples=examples
        )
        
        # Clean the query
        sql_query = clean_sql_query(sql_query)
        
        # Execute query
        result_df = db_manager.execute_query(sql_query)
        
        # Format results
        formatted_result = format_dataframe_for_display(result_df)
        
        return {
            "sql_query": sql_query,
            "query_result": result_df,
            "result_dataframe": formatted_result,
            "error": None
        }
    
    except Exception as e:
        error_msg = str(e)
        
        # Retry logic for SQL errors
        retry_count = state.get("retry_count", 0)
        if retry_count < 2 and "syntax error" in error_msg.lower():
            # Try to fix the query
            fix_prompt = f"""The following SQL query has an error:
            
Query: {sql_query}
Error: {error_msg}

Generate a corrected SQL query. Return ONLY the SQL query."""

            try:
                fixed_query = groq_client.generate_response(
                    prompt=fix_prompt,
                    temperature=0.0
                )
                fixed_query = clean_sql_query(fixed_query)
                
                # Try executing fixed query
                result_df = db_manager.execute_query(fixed_query)
                formatted_result = format_dataframe_for_display(result_df)
                
                return {
                    "sql_query": fixed_query,
                    "query_result": result_df,
                    "result_dataframe": formatted_result,
                    "retry_count": retry_count + 1,
                    "error": None
                }
            except Exception as retry_error:
                pass
        
        return {
            "sql_query": sql_query if 'sql_query' in locals() else None,
            "query_result": None,
            "result_dataframe": None,
            "error": f"SQL execution error: {error_msg}"
        }

def execute_query_agent(state: AgentState) -> Dict[str, Any]:
    """
    Execute pre-generated SQL query
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with execution results
    """
    sql_query = state.get("sql_query")
    
    if not sql_query:
        return {"error": "No SQL query to execute"}
    
    try:
        result_df = db_manager.execute_query(sql_query)
        formatted_result = format_dataframe_for_display(result_df)
        
        return {
            "query_result": result_df,
            "result_dataframe": formatted_result,
            "error": None
        }
    
    except Exception as e:
        return {
            "query_result": None,
            "result_dataframe": None,
            "error": f"Query execution error: {str(e)}"
        }
