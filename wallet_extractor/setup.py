"""
Setup script for Wallet Extractor
Installs dependencies and validates configuration
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    requirements = [
        "psycopg2==2.9.10",
        "sqlalchemy==1.4.53",
        "requests==2.31.0",
        "python-dotenv==1.0.0"
    ]
    
    for package in requirements:
        try:
            print(f"  Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"  ✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install {package}: {e}")
            return False
    
    return True

def check_config_file():
    """Check if config.env exists"""
    config_path = Path("config.env")
    
    if not config_path.exists():
        print("❌ config.env file not found!")
        print("Please create config.env with the following content:")
        print("DEBANK_ACCESS_KEY=YOUR_ACCESS_KEY")
        print("DATABASE_URL=postgres://username:password@host:port/database?sslmode=require")
        return False
    
    print("✅ config.env file found")
    return True

def test_connections():
    """Test database and API connections"""
    print("\n🔧 Testing connections...")
    
    try:
        # Test configuration
        from wallet_extractor.config import Config
        Config.validate_config()
        print("✅ Configuration validation passed")
        
        # Test database connection
        from wallet_extractor.models import db_manager
        tables_exist = db_manager.check_tables_exist()
        table_info = db_manager.get_table_info()
        
        print("✅ Database connection successful")
        print("📊 Database tables:")
        for table_name, info in table_info.items():
            print(f"  ✅ {table_name}: {info['column_count']} columns")
        
        # Test DeBank API connection
        from wallet_extractor.api_client import DeBankClient
        debank_client = DeBankClient()
        
        if debank_client.test_connection():
            print("✅ DeBank API connection successful")
        else:
            print("❌ DeBank API connection failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def create_tables():
    """Create database tables"""
    print("\n🗄️ Creating database tables...")
    
    try:
        from wallet_extractor.models import db_manager
        db_manager.create_tables()
        print("✅ Database tables created/verified successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Wallet Extractor Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return False
    
    # Check config file
    if not check_config_file():
        return False
    
    # Test connections
    if not test_connections():
        print("❌ Connection tests failed")
        return False
    
    # Create tables
    if not create_tables():
        print("❌ Failed to create database tables")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("You can now run the application with:")
    print("python wallet_extractor/main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 