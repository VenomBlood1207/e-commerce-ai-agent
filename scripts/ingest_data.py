"""
Data ingestion script to load CSV files into SQLite database
"""
import sys
import os
from pathlib import Path
import pandas as pd
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.config import settings
from backend.database.connection import db_manager
from backend.llm.embeddings import embedding_generator
import chromadb

# CSV file mappings
CSV_FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "product_category_name_translation": "product_category_name_translation.csv",
    "geolocation": "olist_geolocation_dataset.csv"
}

# Date columns for parsing
DATE_COLUMNS = {
    "orders": [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ],
    "order_items": ["shipping_limit_date"],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"]
}

def load_csv_to_db(csv_path: Path, table_name: str):
    """
    Load CSV file into database table
    
    Args:
        csv_path: Path to CSV file
        table_name: Name of database table
    """
    print(f"Loading {table_name}...")
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Parse date columns
    if table_name in DATE_COLUMNS:
        for col in DATE_COLUMNS[table_name]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Load into database
    df.to_sql(table_name, db_manager.engine, if_exists='replace', index=False)
    
    print(f"  ✓ Loaded {len(df)} rows into {table_name}")

def create_vector_store():
    """Create vector store for product embeddings"""
    print("\nCreating vector store...")
    
    # Create ChromaDB client
    chroma_client = chromadb.PersistentClient(path=str(settings.VECTOR_DB_PATH))
    
    # Create or get collection
    try:
        collection = chroma_client.get_or_create_collection(
            name="products",
            metadata={"description": "Product catalog embeddings"}
        )
    except Exception as e:
        print(f"  ⚠ Vector store creation skipped: {str(e)}")
        return
    
    # Load products from database
    query = """
        SELECT 
            p.product_id,
            p.product_category_name,
            pct.product_category_name_english,
            p.product_weight_g,
            p.product_length_cm,
            p.product_height_cm,
            p.product_width_cm
        FROM products p
        LEFT JOIN product_category_name_translation pct 
            ON p.product_category_name = pct.product_category_name
        LIMIT 1000
    """
    
    try:
        df = db_manager.execute_query(query)
        
        if df.empty:
            print("  ⚠ No products found in database")
            return
        
        # Create text descriptions for embedding
        documents = []
        metadatas = []
        ids = []
        
        for _, row in df.iterrows():
            category = row['product_category_name_english'] or row['product_category_name'] or 'unknown'
            description = f"Product category: {category}"
            
            if pd.notna(row['product_weight_g']):
                description += f", weight: {row['product_weight_g']}g"
            
            documents.append(description)
            metadatas.append({
                "product_id": row['product_id'],
                "category": category
            })
            ids.append(row['product_id'])
        
        # Generate embeddings and add to collection
        print(f"  Generating embeddings for {len(documents)} products...")
        embeddings = embedding_generator.generate_embeddings(documents)
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            collection.add(
                documents=documents[i:end_idx],
                embeddings=embeddings[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )
        
        print(f"  ✓ Created vector store with {len(documents)} product embeddings")
    
    except Exception as e:
        print(f"  ⚠ Vector store creation failed: {str(e)}")

def main():
    """Main ingestion function"""
    parser = argparse.ArgumentParser(description='Ingest e-commerce data into database')
    parser.add_argument('--force', action='store_true', help='Force recreation of database')
    parser.add_argument('--skip-vectors', action='store_true', help='Skip vector store creation')
    args = parser.parse_args()
    
    print("=" * 60)
    print("E-commerce Data Ingestion")
    print("=" * 60)
    
    # Check if data directory exists
    if not settings.DATA_DIR.exists():
        print(f"\n❌ Data directory not found: {settings.DATA_DIR}")
        print("\nPlease download the dataset:")
        print("1. Visit: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/")
        print("2. Download and extract to: data/")
        return
    
    # Create database directory
    settings.DATABASE_DIR.mkdir(exist_ok=True)
    
    # Drop tables if force flag is set
    if args.force:
        print("\n⚠ Force flag set - dropping existing tables...")
        db_manager.drop_tables()
    
    # Create tables
    print("\nCreating database tables...")
    db_manager.create_tables()
    print("  ✓ Tables created")
    
    # Load CSV files
    print("\nLoading CSV files...")
    for table_name, csv_file in CSV_FILES.items():
        csv_path = settings.DATA_DIR / csv_file
        
        if not csv_path.exists():
            print(f"  ⚠ Skipping {table_name} - file not found: {csv_file}")
            continue
        
        try:
            load_csv_to_db(csv_path, table_name)
        except Exception as e:
            print(f"  ❌ Error loading {table_name}: {str(e)}")
    
    # Create vector store
    if not args.skip_vectors:
        try:
            create_vector_store()
        except Exception as e:
            print(f"  ⚠ Vector store creation failed: {str(e)}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Ingestion Complete!")
    print("=" * 60)
    
    try:
        tables = db_manager.get_all_tables()
        print(f"\nTables created: {len(tables)}")
        for table in tables:
            query = f"SELECT COUNT(*) as count FROM {table}"
            result = db_manager.execute_query(query)
            count = result['count'].iloc[0]
            print(f"  • {table}: {count:,} rows")
    except Exception as e:
        print(f"\n⚠ Could not retrieve table statistics: {str(e)}")
    
    print("\n✓ Database ready for use!")
    print(f"  Location: {settings.DATABASE_URL}")

if __name__ == "__main__":
    main()
