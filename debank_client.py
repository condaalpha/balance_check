#!/usr/bin/env python3
"""
DeBank API client for fetching wallet balances
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
    """Client for interacting with DeBank API"""
    
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
            Dict: Balance information or None if error
        """
        try:
            url = f"{self.base_url}/user/total_balance?id={address}"
            
            print(f"🔍 Fetching balance for {address}...")
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Balance fetched successfully for {address}")
                return data
            else:
                print(f"❌ Error fetching balance for {address}: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error fetching balance for {address}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error fetching balance for {address}: {e}")
            return None
    
    def get_chain_balances(self, address: str) -> Optional[Dict]:
        """
        Get chain-specific balances for a wallet address
        
        Args:
            address (str): Ethereum address
            
        Returns:
            Dict: Chain balances or None if error
        """
        try:
            url = f"{self.base_url}/user/chain_balance?id={address}"
            
            print(f"🔍 Fetching chain balances for {address}...")
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chain balances fetched successfully for {address}")
                return data
            else:
                print(f"❌ Error fetching chain balances for {address}: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error fetching chain balances for {address}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error fetching chain balances for {address}: {e}")
            return None
    
    def get_multiple_balances(self, addresses: List[str], delay: float = 1.0) -> Dict[str, Dict]:
        """
        Get balances for multiple addresses with rate limiting
        
        Args:
            addresses (List[str]): List of Ethereum addresses
            delay (float): Delay between requests in seconds
            
        Returns:
            Dict: Address to balance mapping
        """
        results = {}
        
        for i, address in enumerate(addresses, 1):
            print(f"📊 Processing address {i}/{len(addresses)}: {address}")
            
            # Get total balance
            total_balance = self.get_total_balance(address)
            
            # Get chain balances
            chain_balances = self.get_chain_balances(address)
            
            # Combine results
            results[address] = {
                'total_balance': total_balance,
                'chain_balances': chain_balances,
                'fetched_at': datetime.utcnow().isoformat()
            }
            
            # Rate limiting
            if i < len(addresses):
                print(f"⏳ Waiting {delay} seconds before next request...")
                time.sleep(delay)
        
        return results
    
    def parse_balance_data(self, balance_data: Dict) -> Dict:
        """
        Parse and extract key information from DeBank balance response
        
        Args:
            balance_data (Dict): Raw balance data from DeBank API
            
        Returns:
            Dict: Parsed balance information
        """
        if not balance_data:
            return {
                'total_balance_usd': 0.0,
                'total_balance_eth': 0.0,
                'chain_balances': {},
                'is_valid': False,
                'error_message': 'No data received'
            }
        
        try:
            # Extract total balance in USD
            total_balance_usd = balance_data.get('total_usd_value', 0.0)
            
            # Extract total balance in ETH (if available)
            total_balance_eth = balance_data.get('total_eth_value', 0.0)
            
            # Extract chain-specific balances
            chain_balances = {}
            for chain_data in balance_data.get('chain_list', []):
                chain_id = chain_data.get('id', 'unknown')
                chain_balance = {
                    'usd_value': chain_data.get('usd_value', 0.0),
                    'eth_value': chain_data.get('eth_value', 0.0),
                    'tokens': chain_data.get('token_list', [])
                }
                chain_balances[chain_id] = chain_balance
            
            return {
                'total_balance_usd': total_balance_usd,
                'total_balance_eth': total_balance_eth,
                'chain_balances': chain_balances,
                'is_valid': True,
                'error_message': None
            }
            
        except Exception as e:
            return {
                'total_balance_usd': 0.0,
                'total_balance_eth': 0.0,
                'chain_balances': {},
                'is_valid': False,
                'error_message': f'Error parsing balance data: {str(e)}'
            }

# Global DeBank client instance
debank_client = DeBankClient() 