#!/usr/bin/env python3
"""
Startup script for Multi-Address Balance Checker
Handles environment setup and application startup
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def main():
    """Main startup function"""
    
    # Load environment variables from .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)
    
    # Check for required environment variables
    debank_api_key = os.getenv("DEBANK_API_KEY")
    if not debank_api_key or debank_api_key == "your_debank_api_key_here":
        print("❌ Error: DEBANK_API_KEY environment variable is not set!")
        print("Please set your DeBank API key:")
        print("  Windows: set DEBANK_API_KEY=your_api_key_here")
        print("  Linux/Mac: export DEBANK_API_KEY=your_api_key_here")
        print("  Or create a .env file with: DEBANK_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Directories will be created automatically by the main application
    
    print("🚀 Starting Multi-Address Balance Checker...")
    print(f"📊 DeBank API Key: {debank_api_key[:8]}...")
    print("🌐 Application will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    # Import and run the application
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 