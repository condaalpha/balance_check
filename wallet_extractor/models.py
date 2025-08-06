"""
Database models for Wallet Extractor
Defines SQLAlchemy ORM models for storing wallet data
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
import os

Base = declarative_base()

class Address(Base):
    """Model for storing extracted wallet addresses"""
    __tablename__ = 'addresses'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(42), unique=True, nullable=False, index=True)
    account_id = Column(String(255))
    wallet_type = Column(String(50), nullable=False)
    browser = Column(String(50))
    source = Column(String(100))
    file_name = Column(String(255))
    file_path = Column(Text)
    address_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Balance(Base):
    """Model for storing wallet balances"""
    __tablename__ = 'balances'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(42), nullable=False, index=True)
    total_balance_usd = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_valid = Column(Boolean, default=True)
    error_message = Column(Text)

class ExtractionSession(Base):
    """Model for tracking extraction sessions"""
    __tablename__ = 'extraction_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False)
    folder_path = Column(Text)
    total_addresses = Column(Integer, default=0)
    wallets_found = Column(Integer, default=0)
    browsers_found = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String(50), default='running')

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_connection()
    
    def _setup_connection(self):
        """Setup database connection"""
        from wallet_extractor.config import Config
        
        database_url = Config.DATABASE_URL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        inspector = inspect(self.engine)
        existing_tables = inspector.get_table_names()
        tables_to_create = ['addresses', 'balances', 'extraction_sessions']
        missing_tables = [table for table in tables_to_create if table not in existing_tables]
        
        if missing_tables:
            print(f"🔧 Creating missing tables: {missing_tables}")
            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created successfully")
        else:
            print("✅ All database tables already exist - data will be preserved")
    
    def check_tables_exist(self):
        """Check if all required tables exist"""
        inspector = inspect(self.engine)
        existing_tables = inspector.get_table_names()
        required_tables = ['addresses', 'balances', 'extraction_sessions']
        return all(table in existing_tables for table in required_tables)
    
    def get_table_info(self):
        """Get information about existing tables"""
        inspector = inspect(self.engine)
        table_info = {}
        
        for table_name in ['addresses', 'balances', 'extraction_sessions']:
            if inspector.has_table(table_name):
                columns = inspector.get_columns(table_name)
                table_info[table_name] = {
                    'column_count': len(columns),
                    'columns': [col['name'] for col in columns]
                }
        
        return table_info
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

# Global database manager instance
db_manager = DatabaseManager() 