"""
FastAPI Multi-Address Balance Checker
A web application for checking balances of multiple wallet addresses
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import asyncio
import httpx
import json
from typing import List, Dict, Optional
from datetime import datetime
import os
from pathlib import Path

# Create FastAPI app
app = FastAPI(
    title="Multi-Address Balance Checker",
    description="Check balances for multiple wallet addresses using DeBank API",
    version="1.0.0"
)

# Create necessary directories
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# Mount static files and templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration
DEBANK_API_KEY = os.getenv("DEBANK_API_KEY", "your_debank_api_key_here")
DEBANK_BASE_URL = "https://pro-openapi.debank.com/v1"

class DeBankClient:
    """Async client for DeBank API operations"""
    
    def __init__(self):
        self.access_key = DEBANK_API_KEY
        self.base_url = DEBANK_BASE_URL
    
    async def get_total_balance(self, client: httpx.AsyncClient, address: str) -> Optional[Dict]:
        """Get total balance for an address"""
        try:
            url = f"{self.base_url}/user/total_balance"
            params = {'id': address}
            headers = {
                'accept': 'application/json',
                'AccessKey': self.access_key
            }
            
            response = await client.get(url, params=params, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API error for {address}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting balance for {address}: {e}")
            return None
    
    def parse_balance_data(self, balance_data: Dict) -> Dict:
        """Parse balance data into standardized format"""
        if not balance_data:
            return {
                'total_balance_usd': 0.0,
                'is_valid': False,
                'error_message': 'No balance data available'
            }
        
        try:
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
                'error_message': f'Error parsing balance data: {e}'
            }

# Global DeBank client
debank_client = DeBankClient()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main page with balance checker interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/check-balances")
async def check_balances(addresses: str = Form(""), private_keys: str = Form(""), seed_phrases: str = Form("")):
    """Check balances for multiple addresses, private keys, and seed phrases"""
    try:
        # Parse addresses (one per line)
        address_list = []
        for line in addresses.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                address_list.append(line)
        
        # Parse private keys (one per line)
        pk_list = []
        for line in private_keys.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                pk_list.append(line)
        
        # Parse seed phrases (one per line)
        seed_list = []
        for line in seed_phrases.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                seed_list.append(line)
        
        if not address_list and not pk_list and not seed_list:
            raise HTTPException(status_code=400, detail="No valid addresses, private keys, or seed phrases provided")
        
        # Get addresses from private keys
        pk_addresses = []
        if pk_list:
            pk_addresses = await get_addresses_from_private_keys(pk_list)
        
        # Get addresses from seed phrases
        seed_addresses = []
        if seed_list:
            seed_addresses = await get_addresses_from_seed_phrases(seed_list)
        
        # Combine all addresses
        all_addresses = address_list + pk_addresses + seed_addresses
        
        # Check balances concurrently
        results = await check_multiple_balances(all_addresses)
        
        return JSONResponse(content={
            "success": True,
            "results": results,
            "summary": generate_summary(results),
            "timestamp": datetime.now().isoformat(),
            "address_count": len(address_list),
            "pk_count": len(pk_list),
            "seed_count": len(seed_list)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_addresses_from_private_keys(private_keys: List[str]) -> List[str]:
    """Convert private keys to addresses using ecdsa"""
    addresses = []
    
    for pk in private_keys:
        try:
            # Remove 0x prefix if present
            if pk.startswith('0x'):
                pk = pk[2:]
            
            # Validate private key format (allow both uppercase and lowercase hex)
            pk_lower = pk.lower()
            if len(pk) != 64 or not all(c in '0123456789abcdef' for c in pk_lower):
                addresses.append(f"INVALID_PK_{pk[:8]}...")
                continue
            
            # Convert private key to address using eth-account (same as your example)
            from eth_account import Account
            
            # Normalize private key (add 0x prefix if missing)
            if not pk.startswith('0x'):
                pk = '0x' + pk
            
            # Derive address using eth-account
            account = Account.from_key(pk)
            address = account.address  # This gives EIP-55 checksummed address
            
            addresses.append(address)
            
        except Exception as e:
            print(f"Error converting private key to address: {e}")
            addresses.append(f"INVALID_PK_{pk[:8]}...")
    
    return addresses

async def get_addresses_from_seed_phrases(seed_phrases: List[str]) -> List[str]:
    """Convert seed phrases to addresses using eth-account HD wallet"""
    addresses = []
    
    # Enable HD wallet features in eth-account
    from eth_account import Account
    Account.enable_unaudited_hdwallet_features()
    
    for seed in seed_phrases:
        try:
            # Derive account from mnemonic using default path m/44'/60'/0'/0/0
            account = Account.from_mnemonic(seed, account_path="m/44'/60'/0'/0/0")
            address = account.address
            addresses.append(address)
            
        except Exception as e:
            print(f"Error converting seed phrase to address: {e}")
            addresses.append(f"INVALID_SEED_{seed[:20]}...")
    
    return addresses

async def check_multiple_balances(addresses: List[str]) -> Dict:
    """Check balances for multiple addresses concurrently"""
    results = {}
    
    # Use httpx client for concurrent requests
    async with httpx.AsyncClient() as client:
        # Create tasks for all addresses
        tasks = []
        for address in addresses:
            task = check_single_balance(client, address)
            tasks.append(task)
        
        # Execute all tasks concurrently
        balance_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(balance_results):
            address = addresses[i]
            if isinstance(result, Exception):
                results[address] = {
                    'success': False,
                    'balance_usd': 0.0,
                    'error': str(result)
                }
            else:
                results[address] = result
    
    return results

async def check_single_balance(client: httpx.AsyncClient, address: str) -> Dict:
    """Check balance for a single address"""
    try:
        balance_data = await debank_client.get_total_balance(client, address)
        
        if balance_data:
            parsed = debank_client.parse_balance_data(balance_data)
            return {
                'success': True,
                'balance_usd': parsed['total_balance_usd'],
                'error': None
            }
        else:
            return {
                'success': False,
                'balance_usd': 0.0,
                'error': 'Failed to fetch balance'
            }
            
    except Exception as e:
        return {
            'success': False,
            'balance_usd': 0.0,
            'error': str(e)
        }

def generate_summary(results: Dict) -> Dict:
    """Generate summary statistics from results"""
    total_addresses = len(results)
    successful = sum(1 for r in results.values() if r['success'])
    failed = total_addresses - successful
    total_balance = sum(r['balance_usd'] for r in results.values() if r['success'])
    
    return {
        'total_addresses': total_addresses,
        'successful': successful,
        'failed': failed,
        'total_balance_usd': total_balance
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 