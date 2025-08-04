#!/usr/bin/env python3
"""
DeBank API client for fetching wallet total balances
"""

import os
import time
import requests
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

class DeBankClient:
    """Client for interacting with DeBank API - Total Balance Only"""
    
    def __init__(self):
        self.access_key = os.getenv('DEBANK_ACCESS_KEY')
        if not self.access_key:
            raise ValueError("DEBANK_ACCESS_KEY not found in environment variables")
        
        self.base_url = "https://pro-openapi.debank.com/v1"
        self.headers = {
            'accept': 'application/json',
            'AccessKey': self.access_key
        }
    
    def get_total_balance(self, address: str) -> Optional[Dict]:
        """
        Get total balance for a wallet address
        
        Args:
            address (str): Ethereum address
            
        Returns:
            Dict: Balance information with total_usd_value or None if error
        """
        try:
            url = f"{self.base_url}/user/total_balance?id={address}"
            
            print(f"🔍 Fetching total balance for {address}...")
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Total balance fetched successfully for {address}")
                return data
            else:
                print(f"❌ Error fetching total balance for {address}: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error fetching total balance for {address}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error fetching total balance for {address}: {e}")
            return None
    
    def get_multiple_balances(self, addresses: List[str], delay: float = 1.0) -> Dict[str, Dict]:
        """
        Get total balances for multiple addresses with rate limiting
        
        Args:
            addresses (List[str]): List of Ethereum addresses
            delay (float): Delay between requests in seconds
            
        Returns:
            Dict: Address to total balance mapping
        """
        results = {}
        
        for i, address in enumerate(addresses, 1):
            print(f"📊 Processing address {i}/{len(addresses)}: {address}")
            
            # Get total balance only
            total_balance = self.get_total_balance(address)
            
            # Store result
            results[address] = {
                'total_balance': total_balance,
                'fetched_at': datetime.utcnow().isoformat()
            }
            
            # Rate limiting
            if i < len(addresses):
                print(f"⏳ Waiting {delay} seconds before next request...")
                time.sleep(delay)
        
        return results
    
    def parse_balance_data(self, balance_data: Dict) -> Dict:
        """
        Parse and extract total USD value from DeBank balance response
        
        Args:
            balance_data (Dict): Raw balance data from DeBank API
            
        Returns:
            Dict: Parsed balance information with total_usd_value
        """
        if not balance_data:
            return {
                'total_balance_usd': 0.0,
                'is_valid': False,
                'error_message': 'No data received'
            }
        
        try:
            # Extract only total balance in USD
            total_balance_usd = balance_data.get('total_usd_value', 0.0)
            
            return {
                'total_balance_usd': total_balance_usd,
                'is_valid': True,
                'error_message': None
            }
            
        except Exception as e:
            return {
                'total_balance_usd': 0.0,
                'is_valid': False,
                'error_message': f'Error parsing balance data: {str(e)}'
            }

# Global DeBank client instance
debank_client = DeBankClient() 