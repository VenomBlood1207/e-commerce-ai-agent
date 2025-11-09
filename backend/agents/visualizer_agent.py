"""
Visualizer Agent - Generates chart configurations from query results
"""
from typing import Dict, Any, Optional
import pandas as pd
from backend.graph.state import AgentState
from backend.utils.helpers import detect_chart_type

def visualizer_agent(state: AgentState) -> Dict[str, Any]:
    """
    Generate visualization configuration
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with chart configuration
    """
    result_df = state.get("query_result")
    
    if result_df is None or not isinstance(result_df, pd.DataFrame) or result_df.empty:
        return {
            "chart_type": None,
            "chart_data": None
        }
    
    # Detect appropriate chart type
    chart_type = detect_chart_type(result_df)
    
    # Generate chart configuration
    chart_data = generate_chart_config(result_df, chart_type)
    
    return {
        "chart_type": chart_type,
        "chart_data": chart_data
    }

def generate_chart_config(df: pd.DataFrame, chart_type: str) -> Optional[Dict[str, Any]]:
    """
    Generate chart configuration based on data and chart type
    
    Args:
        df: Data DataFrame
        chart_type: Type of chart
        
    Returns:
        Chart configuration dictionary
    """
    if df.empty or chart_type == "table":
        return None
    
    try:
        # Get column names
        columns = df.columns.tolist()
        
        if chart_type == "bar":
            return {
                "type": "bar",
                "x_axis": columns[0],
                "y_axis": columns[1] if len(columns) > 1 else columns[0],
                "data": df.to_dict('records')
            }
        
        elif chart_type == "line":
            return {
                "type": "line",
                "x_axis": columns[0],
                "y_axis": columns[1] if len(columns) > 1 else columns[0],
                "data": df.to_dict('records')
            }
        
        elif chart_type == "pie":
            return {
                "type": "pie",
                "label": columns[0],
                "value": columns[1] if len(columns) > 1 else columns[0],
                "data": df.to_dict('records')
            }
        
        elif chart_type == "scatter":
            return {
                "type": "scatter",
                "x_axis": columns[0],
                "y_axis": columns[1] if len(columns) > 1 else columns[0],
                "data": df.to_dict('records')
            }
        
        return None
    
    except Exception as e:
        print(f"Chart config generation error: {str(e)}")
        return None
