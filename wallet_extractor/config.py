"""
Configuration module for Wallet Extractor
Handles environment variables and application settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('config.env')

class Config:
    """Application configuration"""
    
    # DeBank API Configuration
    DEBANK_ACCESS_KEY = os.getenv('DEBANK_ACCESS_KEY')
    DEBANK_BASE_URL = 'https://pro-openapi.debank.com/v1'
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Application Settings
    SUPPORTED_WALLETS = {
        'metamask': 'nkbihfbeogaeaoehlefnkodbefgpgknn'
    }
    
    SUPPORTED_BROWSERS = [
        'Chrome', 'Firefox', 'Brave', 'Edge', 'Opera', 'Safari'
    ]
    
    # File patterns
    LOG_FILE_PATTERN = '*.log'
    LDB_FILE_PATTERN = '*.ldb'
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        missing = []
        
        if not cls.DEBANK_ACCESS_KEY:
            missing.append('DEBANK_ACCESS_KEY')
        
        if not cls.DATABASE_URL:
            missing.append('DATABASE_URL')
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True 