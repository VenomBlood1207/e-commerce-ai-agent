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
            SELECT p.product_category_name, COUNT(*) as sales_count, SUM(oi.price) as total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY p.product_category_name
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
    }
]
