"""
Main entry point for Wallet Extractor application
"""

import sys
import os

# Add the parent directory to the path so we can import from wallet_extractor
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wallet_extractor.gui import main

if __name__ == "__main__":
    main() 
 