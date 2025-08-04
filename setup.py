#!/usr/bin/env python3
"""
Setup script for Enhanced Wallet Address Extractor
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    requirements = [
        'sqlalchemy==1.4.53',
        'requests==2.31.0',
        'python-dotenv==1.0.0'
    ]
    
    for package in requirements:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def check_config():
    """Check if configuration file exists"""
    if not os.path.exists('config.env'):
        print("❌ config.env file not found!")
        print("Please create config.env with your DeBank API key and database URL:")
        return False
    
    print("✅ config.env file found")
    return True

def test_database_connection():
    """Test database connection"""
    print("🔗 Testing database connection...")
    
    try:
        from database_models import db_manager
        db_manager.create_tables()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_debank_api():
    """Test DeBank API connection"""
    print("🌐 Testing DeBank API connection...")
    
    try:
        from debank_client import debank_client
        print("✅ DeBank API client initialized")
        return True
    except Exception as e:
        print(f"❌ DeBank API initialization failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("ENHANCED WALLET ADDRESS EXTRACTOR SETUP")
    print("=" * 60)
    
    # Check configuration
    if not check_config():
        return
    
    # Install requirements
    if not install_requirements():
        print("❌ Failed to install requirements")
        return
    
    # Test database connection
    if not test_database_connection():
        print("❌ Database connection failed")
        return
    
    # Test DeBank API
    if not test_debank_api():
        print("❌ DeBank API initialization failed")
        return
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nYou can now run the enhanced GUI:")
    print("python enhanced_gui.py")
    print("\nOr the basic GUI:")
    print("python gui_wallet_extractor.py")

if __name__ == "__main__":
    main() 