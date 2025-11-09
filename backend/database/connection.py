"""
Database connection manager
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator
import pandas as pd
from backend.config import settings
from backend.database.models import Base

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, database_url: str = None):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url or settings.DATABASE_URL
        
        # Create engine with connection pooling
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {},
            poolclass=StaticPool if "sqlite" in self.database_url else None,
            echo=False
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all database tables"""
        Base.metadata.drop_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session context manager
        
        Yields:
            Database session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame
        
        Args:
            query: SQL query string
            
        Returns:
            Query results as pandas DataFrame
        """
        try:
            with self.engine.connect() as connection:
                result = pd.read_sql_query(text(query), connection)
            return result
        except Exception as e:
            raise Exception(f"Query execution error: {str(e)}")
    
    def execute_raw_query(self, query: str):
        """
        Execute raw SQL query without returning results
        
        Args:
            query: SQL query string
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text(query))
                connection.commit()
        except Exception as e:
            raise Exception(f"Query execution error: {str(e)}")
    
    def get_table_info(self, table_name: str) -> dict:
        """
        Get information about a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        query = f"PRAGMA table_info({table_name})"
        result = self.execute_query(query)
        return result.to_dict('records')
    
    def get_all_tables(self) -> list:
        """
        Get list of all tables in database
        
        Returns:
            List of table names
        """
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        result = self.execute_query(query)
        return result['name'].tolist()

# Global database manager instance
db_manager = DatabaseManager()

def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session
    
    Yields:
        Database session
    """
    with db_manager.get_session() as session:
        yield session
