"""
Configuration settings for the E-commerce Intelligence Agent
"""
import os
from pathlib import Path
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # API Keys
    GROQ_API_KEY: str = ""
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./database/ecommerce.db"
    VECTOR_DB_PATH: str = "./database/chromadb"
    
    # Application Settings
    LOG_LEVEL: str = "INFO"
    MAX_CONVERSATION_HISTORY: int = 10
    ENABLE_WEB_SEARCH: bool = True
    MAX_QUERY_RESULTS: int = 1000
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Model Configuration
    REASONING_MODEL: str = "gpt-oss-120b"
    SQL_MODEL: str = "llama-3.3-70b-versatile"
    DEFAULT_TEMPERATURE: float = 0.1
    SQL_TEMPERATURE: float = 0.0
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_DIR: Path = BASE_DIR / "database"
    
    @field_validator("ENABLE_WEB_SEARCH", mode="before")
    @classmethod
    def parse_bool(cls, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

# Global settings instance
settings = Settings()

# Database schema information
DATABASE_SCHEMA = {
    "orders": {
        "columns": [
            "order_id", "customer_id", "order_status", "order_purchase_timestamp",
            "order_approved_at", "order_delivered_carrier_date", 
            "order_delivered_customer_date", "order_estimated_delivery_date"
        ],
        "description": "Order details and status tracking"
    },
    "order_items": {
        "columns": [
            "order_id", "order_item_id", "product_id", "seller_id",
            "shipping_limit_date", "price", "freight_value"
        ],
        "description": "Product items in each order with pricing"
    },
    "order_payments": {
        "columns": [
            "order_id", "payment_sequential", "payment_type",
            "payment_installments", "payment_value"
        ],
        "description": "Payment information for orders"
    },
    "order_reviews": {
        "columns": [
            "review_id", "order_id", "review_score", "review_comment_title",
            "review_comment_message", "review_creation_date", "review_answer_timestamp"
        ],
        "description": "Customer reviews and ratings"
    },
    "customers": {
        "columns": [
            "customer_id", "customer_unique_id", "customer_zip_code_prefix",
            "customer_city", "customer_state"
        ],
        "description": "Customer information and location"
    },
    "sellers": {
        "columns": [
            "seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"
        ],
        "description": "Seller details and location"
    },
    "products": {
        "columns": [
            "product_id", "product_category_name", "product_name_length",
            "product_description_length", "product_photos_qty",
            "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"
        ],
        "description": "Product catalog with dimensions and categories"
    },
    "product_category_name_translation": {
        "columns": [
            "product_category_name", "product_category_name_english"
        ],
        "description": "Portuguese to English category translations"
    },
    "geolocation": {
        "columns": [
            "geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng",
            "geolocation_city", "geolocation_state"
        ],
        "description": "Brazilian zip code geolocation data"
    }
}

# Common SQL query templates
SQL_EXAMPLES = [
    {
        "question": "What are the top 5 product categories by sales?",
        "sql": """
            SELECT 
                COALESCE(pct.product_category_name_english, p.product_category_name) as category,
                COUNT(*) as sales_count, 
                SUM(oi.price) as total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN product_category_name_translation pct ON p.product_category_name = pct.product_category_name
            GROUP BY category
            ORDER BY total_revenue DESC
            LIMIT 5
        """
    },
    {
        "question": "Show average delivery time by state",
        "sql": """
            SELECT c.customer_state, 
                   AVG(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp)) as avg_delivery_days
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_delivered_customer_date IS NOT NULL
            GROUP BY c.customer_state
            ORDER BY avg_delivery_days
        """
    },
    {
        "question": "What is the average order value for items in the electronics category?",
        "sql": """
            SELECT AVG(oi.price) as average_order_value
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN product_category_name_translation pct ON p.product_category_name = pct.product_category_name
            WHERE pct.product_category_name_english LIKE '%electronics%' 
               OR pct.product_category_name_english LIKE '%eletronicos%'
               OR p.product_category_name LIKE '%eletronicos%'
               OR p.product_category_name LIKE '%informatica%'
        """
    },
    {
        "question": "Show me sales for furniture products",
        "sql": """
            SELECT 
                COALESCE(pct.product_category_name_english, p.product_category_name) as category,
                COUNT(*) as order_count,
                SUM(oi.price) as total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN product_category_name_translation pct ON p.product_category_name = pct.product_category_name
            WHERE pct.product_category_name_english LIKE '%furniture%'
               OR p.product_category_name LIKE '%moveis%'
            GROUP BY category
        """
    },
    {
        "question": "Which product category was the highest selling in the past 2 quarters?",
        "sql": """
            SELECT 
                COALESCE(pct.product_category_name_english, p.product_category_name) as category,
                COUNT(*) as sales_count,
                SUM(oi.price) as total_revenue,
                CAST(STRFTIME('%Y', o.order_purchase_timestamp) AS INTEGER) as year,
                CAST((CAST(STRFTIME('%m', o.order_purchase_timestamp) AS INTEGER) + 2) / 3 AS INTEGER) as quarter
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN product_category_name_translation pct ON p.product_category_name = pct.product_category_name
            WHERE o.order_purchase_timestamp >= DATE((SELECT MAX(order_purchase_timestamp) FROM orders), '-6 months')
            GROUP BY category
            ORDER BY total_revenue DESC
            LIMIT 1
        """
    },
    {
        "question": "Show sales by month for the last 6 months",
        "sql": """
            SELECT 
                STRFTIME('%Y-%m', o.order_purchase_timestamp) as month,
                COUNT(*) as order_count,
                SUM(oi.price) as revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_purchase_timestamp >= DATE((SELECT MAX(order_purchase_timestamp) FROM orders), '-6 months')
            GROUP BY month
            ORDER BY month DESC
        """
    },
    {
        "question": "What were the top selling products last year?",
        "sql": """
            SELECT 
                p.product_id,
                COALESCE(pct.product_category_name_english, p.product_category_name) as category,
                COUNT(*) as sales_count,
                SUM(oi.price) as revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN product_category_name_translation pct ON p.product_category_name = pct.product_category_name
            WHERE STRFTIME('%Y', o.order_purchase_timestamp) = CAST(STRFTIME('%Y', (SELECT MAX(order_purchase_timestamp) FROM orders)) AS INTEGER) - 1
            GROUP BY p.product_id, category
            ORDER BY sales_count DESC
            LIMIT 10
        """
    }
]
