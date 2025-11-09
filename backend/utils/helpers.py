"""
Helper utilities for data processing and formatting
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import re

def format_dataframe_for_display(df: pd.DataFrame, max_rows: int = 100) -> Dict[str, Any]:
    """
    Format DataFrame for display in frontend
    
    Args:
        df: Pandas DataFrame
        max_rows: Maximum rows to include
        
    Returns:
        Dictionary with formatted data
    """
    if df.empty:
        return {
            "columns": [],
            "data": [],
            "row_count": 0,
            "column_count": 0
        }
    
    # Limit rows
    df_display = df.head(max_rows)
    
    # Convert to records
    data = df_display.to_dict('records')
    
    # Get column names and types
    columns = [
        {
            "name": col,
            "type": str(df[col].dtype)
        }
        for col in df.columns
    ]
    
    return {
        "columns": columns,
        "data": data,
        "row_count": len(df),
        "column_count": len(df.columns),
        "truncated": len(df) > max_rows
    }

def detect_chart_type(df: pd.DataFrame) -> str:
    """
    Detect appropriate chart type based on DataFrame structure
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        Chart type ('bar', 'line', 'pie', 'scatter', 'table')
    """
    if df.empty or len(df.columns) < 2:
        return "table"
    
    # Check for time series data
    first_col = df.iloc[:, 0]
    if pd.api.types.is_datetime64_any_dtype(first_col) or \
       any(keyword in str(df.columns[0]).lower() for keyword in ['date', 'time', 'year', 'month']):
        return "line"
    
    # Check for categorical data with counts/values
    if len(df) <= 10 and len(df.columns) == 2:
        second_col = df.iloc[:, 1]
        if pd.api.types.is_numeric_dtype(second_col):
            # If values sum to ~100, likely percentages (pie chart)
            if 90 <= second_col.sum() <= 110:
                return "pie"
            return "bar"
    
    # Check for scatter plot (two numeric columns)
    if len(df.columns) >= 2:
        if pd.api.types.is_numeric_dtype(df.iloc[:, 0]) and \
           pd.api.types.is_numeric_dtype(df.iloc[:, 1]):
            return "scatter"
    
    # Default to bar chart for categorical data
    if len(df) <= 20:
        return "bar"
    
    return "table"

def clean_sql_query(query: str) -> str:
    """
    Clean and validate SQL query
    
    Args:
        query: Raw SQL query
        
    Returns:
        Cleaned SQL query
    """
    # Remove markdown code blocks
    query = re.sub(r'```sql\s*', '', query)
    query = re.sub(r'```\s*', '', query)
    
    # Remove comments
    query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
    
    # Remove extra whitespace
    query = ' '.join(query.split())
    
    # Ensure query ends with semicolon
    query = query.rstrip(';').strip() + ';'
    
    return query

def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text
    
    Args:
        text: Input text
        
    Returns:
        List of keywords
    """
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'what', 'which', 'who',
        'when', 'where', 'why', 'how', 'show', 'me', 'get', 'find'
    }
    
    # Extract words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    return keywords

def format_number(value: float, decimals: int = 2) -> str:
    """
    Format number for display
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.{decimals}f}M"
    elif abs(value) >= 1_000:
        return f"{value / 1_000:.{decimals}f}K"
    else:
        return f"{value:.{decimals}f}"

def calculate_statistics(df: pd.DataFrame, column: str) -> Dict[str, float]:
    """
    Calculate basic statistics for a numeric column
    
    Args:
        df: Pandas DataFrame
        column: Column name
        
    Returns:
        Dictionary with statistics
    """
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return {}
    
    series = df[column].dropna()
    
    return {
        "mean": float(series.mean()),
        "median": float(series.median()),
        "std": float(series.std()),
        "min": float(series.min()),
        "max": float(series.max()),
        "count": int(series.count())
    }
