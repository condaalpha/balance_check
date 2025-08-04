#!/usr/bin/env python3
"""
Database models for wallet address extraction and balance checking
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSON
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

Base = declarative_base()

class Address(Base):
    """Model for storing extracted wallet addresses"""
    __tablename__ = 'addresses'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(42), unique=True, nullable=False, index=True)
    account_id = Column(String(255))
    wallet_type = Column(String(50))  # MetaMask, Phantom, etc.
    browser = Column(String(50))      # Chrome, Firefox, etc.
    source = Column(String(100))      # internalAccounts, identities, etc.
    file_path = Column(Text)
    file_name = Column(String(255))
    address_metadata = Column(JSON)   # Store additional extraction data
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Address(address='{self.address}', wallet='{self.wallet_type}', browser='{self.browser}')>"

class Balance(Base):
    """Model for storing address balances from DeBank API"""
    __tablename__ = 'balances'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(42), nullable=False, index=True)
    total_balance_usd = Column(Float)
    total_balance_eth = Column(Float)
    chain_balances = Column(JSON)     # Store chain-specific balances
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_valid = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Balance(address='{self.address}', usd={self.total_balance_usd}, eth={self.total_balance_eth})>"

class ExtractionSession(Base):
    """Model for tracking extraction sessions"""
    __tablename__ = 'extraction_sessions'
    
    id = Column(Integer, primary_key=True)
    folder_path = Column(Text)
    total_addresses = Column(Integer)
    browsers_found = Column(JSON)     # Array of browsers found
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default='running')  # running, completed, failed
    
    def __repr__(self):
        return f"<ExtractionSession(id={self.id}, addresses={self.total_addresses}, status='{self.status}')>"

class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_connection()
    
    def _setup_connection(self):
        """Setup database connection from environment variables"""
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        # Convert to explicit psycopg2 connection string (like test_postgresql.py)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+psycopg2://', 1)
        elif database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        
        # Use the exact same approach as the working test_postgresql.py
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database tables created successfully")
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def close_session(self, session):
        """Close database session"""
        session.close()

# Global database manager instance
db_manager = DatabaseManager() 