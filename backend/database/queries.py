"""
Predefined SQL query templates and helpers
"""
from typing import Dict, Any
from backend.config import DATABASE_SCHEMA

def get_schema_description() -> str:
    """
    Get formatted database schema description
    
    Returns:
        Formatted schema string
    """
    schema_text = """Database Schema:

IMPORTANT NOTES:
1. Product categories are stored in PORTUGUESE in the 'products' table
2. ALWAYS use the 'product_category_name_translation' table to handle English category names
3. When filtering by category in English (e.g., 'electronics', 'furniture'), use:
   - JOIN with product_category_name_translation table
   - Use LIKE '%keyword%' for flexible matching
   - Check both English translation AND Portuguese names
4. Common category mappings:
   - electronics → eletronicos, informatica_acessorios
   - furniture → moveis_decoracao
   - toys → brinquedos
   - books → livros_tecnicos, livros_interesse_geral
5. DATE/TIME queries:
   - Primary date column: order_purchase_timestamp in orders table
   - For relative dates (past N months/quarters), use: DATE((SELECT MAX(order_purchase_timestamp) FROM orders), '-N months')
   - For quarters: Calculate as CAST((CAST(STRFTIME('%m', date) AS INTEGER) + 2) / 3 AS INTEGER)
   - For year/month: Use STRFTIME('%Y-%m', date)
   - The dataset spans from 2016 to 2018

"""
    
    for table_name, table_info in DATABASE_SCHEMA.items():
        schema_text += f"Table: {table_name}\n"
        schema_text += f"Description: {table_info['description']}\n"
        schema_text += f"Columns: {', '.join(table_info['columns'])}\n\n"
    
    return schema_text

def get_example_queries() -> str:
    """
    Get example SQL queries for few-shot learning
    
    Returns:
        Formatted examples string
    """
    from backend.config import SQL_EXAMPLES
    
    examples_text = "Example Queries:\n\n"
    
    for i, example in enumerate(SQL_EXAMPLES, 1):
        examples_text += f"Example {i}:\n"
        examples_text += f"Question: {example['question']}\n"
        examples_text += f"SQL: {example['sql']}\n\n"
    
    return examples_text

# Common query patterns
QUERY_PATTERNS = {
    "top_products": """
        SELECT p.product_id, p.product_category_name, COUNT(*) as order_count
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        GROUP BY p.product_id, p.product_category_name
        ORDER BY order_count DESC
        LIMIT {limit}
    """,
    
    "revenue_by_category": """
        SELECT 
            pct.product_category_name_english as category,
            COUNT(DISTINCT oi.order_id) as order_count,
            SUM(oi.price) as total_revenue,
            AVG(oi.price) as avg_price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN product_category_name_translation pct 
            ON p.product_category_name = pct.product_category_name
        GROUP BY pct.product_category_name_english
        ORDER BY total_revenue DESC
    """,
    
    "customer_orders": """
        SELECT 
            c.customer_state,
            COUNT(DISTINCT o.order_id) as total_orders,
            COUNT(DISTINCT c.customer_id) as total_customers,
            AVG(op.payment_value) as avg_order_value
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_payments op ON o.order_id = op.order_id
        GROUP BY c.customer_state
        ORDER BY total_orders DESC
    """,
    
    "seller_performance": """
        SELECT 
            s.seller_id,
            s.seller_city,
            s.seller_state,
            COUNT(DISTINCT oi.order_id) as total_orders,
            SUM(oi.price) as total_revenue,
            AVG(or2.review_score) as avg_rating
        FROM sellers s
        JOIN order_items oi ON s.seller_id = oi.seller_id
        LEFT JOIN order_reviews or2 ON oi.order_id = or2.order_id
        GROUP BY s.seller_id, s.seller_city, s.seller_state
        ORDER BY total_revenue DESC
        LIMIT {limit}
    """,
    
    "delivery_performance": """
        SELECT 
            c.customer_state,
            AVG(JULIANDAY(o.order_delivered_customer_date) - 
                JULIANDAY(o.order_purchase_timestamp)) as avg_delivery_days,
            COUNT(*) as total_deliveries
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_delivered_customer_date IS NOT NULL
        GROUP BY c.customer_state
        ORDER BY avg_delivery_days
    """
}

def get_query_pattern(pattern_name: str, **kwargs) -> str:
    """
    Get a predefined query pattern with parameters
    
    Args:
        pattern_name: Name of the query pattern
        **kwargs: Parameters to format into the query
        
    Returns:
        Formatted SQL query
    """
    if pattern_name not in QUERY_PATTERNS:
        raise ValueError(f"Unknown query pattern: {pattern_name}")
    
    query = QUERY_PATTERNS[pattern_name]
    return query.format(**kwargs)
