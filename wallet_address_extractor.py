#!/usr/bin/env python3
"""
Scalable Wallet Address Extractor
Supports multiple wallet types and file formats.
Currently supports MetaMask (.log and .ldb files).
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Set
from abc import ABC, abstractmethod

class WalletExtractor(ABC):
    """Abstract base class for wallet-specific extractors"""
    
    @abstractmethod
    def extract_from_log_file(self, file_path: str) -> List[Dict]:
        """Extract addresses from log files"""
        pass
    
    @abstractmethod
    def extract_from_ldb_file(self, file_path: str) -> List[Dict]:
        """Extract addresses from ldb files"""
        pass
    
    @abstractmethod
    def get_wallet_name(self) -> str:
        """Return wallet name"""
        pass

class MetaMaskExtractor(WalletExtractor):
    """MetaMask-specific address extractor"""
    
    def get_wallet_name(self) -> str:
        return "MetaMask"
    
    def extract_from_log_file(self, file_path: str) -> List[Dict]:
        """Extract addresses from MetaMask log files using internalAccounts logic"""
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return []
        
        print(f"🔍 Processing log file: {os.path.basename(file_path)}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Look for internalAccounts key
            key = '"internalAccounts"'
            key_index = content.find(key)
            
            if key_index == -1:
                print(f"⚠️ 'internalAccounts' not found in {os.path.basename(file_path)}")
                return []
            
            print("✅ Found 'internalAccounts' structure")
            
            # Find the opening brace after the key
            brace_start = content.find('{', key_index)
            if brace_start == -1:
                print(f"⚠️ Opening brace not found after key in {os.path.basename(file_path)}")
                return []
            
            # Find the matching closing brace
            brace_count = 1
            end_index = brace_start + 1
            while end_index < len(content) and brace_count > 0:
                if content[end_index] == '{':
                    brace_count += 1
                elif content[end_index] == '}':
                    brace_count -= 1
                end_index += 1
            
            # Extract the JSON object
            object_str = content[brace_start:end_index]
            full_json = '{"internalAccounts": ' + object_str + '}'
            
            # Parse the JSON
            parsed = json.loads(full_json)
            accounts = parsed["internalAccounts"].get("accounts", {})
            
            # Extract addresses
            addresses = []
            for account_id, info in accounts.items():
                if "address" in info:
                    address = info["address"]
                    if address and self._is_valid_ethereum_address(address):
                        addresses.append({
                            'address': address,
                            'account_id': account_id,
                            'source': 'internalAccounts.accounts',
                            'file': os.path.basename(file_path),
                            'file_path': str(file_path),
                            'wallet': self.get_wallet_name()
                        })
                        print(f"📄 Found account: {account_id} -> {address}")
            
            return addresses
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return []
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return []
    
    def extract_from_ldb_file(self, file_path: str) -> List[Dict]:
        """Extract addresses from MetaMask ldb files using identities logic"""
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return []
        
        print(f"🔍 Processing ldb file: {os.path.basename(file_path)}")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Look for identities structure
            start_pattern = r'"identities"\s*:\s*\{'
            start_match = re.search(start_pattern, content)
            
            if not start_match:
                print(f"⚠️ Identities structure not found in {os.path.basename(file_path)}")
                return []
            
            start_pos = start_match.end() - 1  # Position of the opening {
            print(f"✅ Found identities structure at position {start_pos}")
            
            # Find the matching closing brace by counting braces
            brace_count = 0
            end_pos = start_pos
            
            for i in range(start_pos, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i
                        break
            
            identities_content = content[start_pos + 1:end_pos]
            print(f"✅ Captured identities content from position {start_pos + 1} to {end_pos}")
            
            # Extract all address keys from this content
            key_pattern = r'"([^"]+)"\s*:\s*\{'
            keys = re.findall(key_pattern, identities_content)
            
            # Filter to only Ethereum addresses
            ethereum_keys = [key for key in keys if self._is_valid_ethereum_address(key)]
            
            addresses = []
            for address in ethereum_keys:
                addresses.append({
                    'address': address,
                    'account_id': address,  # For ldb files, address is the key
                    'source': 'identities',
                    'file': os.path.basename(file_path),
                    'file_path': str(file_path),
                    'wallet': self.get_wallet_name()
                })
                print(f"📄 Found identity: {address}")
            
            return addresses
            
        except Exception as e:
            print(f"❌ Error processing ldb file: {e}")
            return []
    
    def _is_valid_ethereum_address(self, address: str) -> bool:
        """Validate Ethereum address format"""
        return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))

class WalletProcessor:
    """Main processor for handling wallet folder structures"""
    
    def __init__(self):
        self.extractors = {
            'nkbihfbeogaeaoehlefnkodbefgpgknn': MetaMaskExtractor()
            # Add other wallet extractors here in the future
        }
    
    def get_wallet_extractor(self, wallet_folder: str) -> WalletExtractor:
        """Get the appropriate extractor for a wallet folder"""
        return self.extractors.get(wallet_folder, None)
    
    def process_folder(self, folder_path: str) -> List[Dict]:
        """
        Process a wallet folder and extract all addresses from any browser structure
        
        Args:
            folder_path (str): Path to the wallet folder (e.g., '64_Duxs-MacBook-Pro.local')
            
        Returns:
            List[Dict]: List of extracted addresses with metadata
        """
        
        folder_path = Path(folder_path)
        if not folder_path.exists():
            print(f"❌ Folder not found: {folder_path}")
            return []
        
        print(f"🔍 Processing folder: {folder_path.name}")
        
        all_addresses = []
        
        # Search recursively for any wallet extension folders
        for wallet_folder in self.extractors.keys():
            print(f"🔍 Looking for {wallet_folder}...")
            
            # Search recursively for the wallet folder anywhere in the structure
            wallet_paths = list(folder_path.rglob(wallet_folder))
            
            if wallet_paths:
                for wallet_path in wallet_paths:
                    if wallet_path.is_dir():
                        # Try to detect browser from the path
                        browser = self._detect_browser_from_path(wallet_path, folder_path)
                        print(f"✅ Found {wallet_folder} at {wallet_path.relative_to(folder_path)} (Browser: {browser})")
                        addresses = self._process_wallet_folder(wallet_path, wallet_folder, browser)
                        all_addresses.extend(addresses)
            else:
                print(f"⚠️ {wallet_folder} not found in any subfolder")
        
        # Remove duplicates
        unique_addresses = self._remove_duplicates(all_addresses)
        
        return unique_addresses
    
    def _detect_browser_from_path(self, wallet_path: Path, root_path: Path) -> str:
        """Detect browser type from wallet folder path"""
        relative_path = wallet_path.relative_to(root_path)
        path_parts = relative_path.parts
        
        # Common browser folder names (case-insensitive matching)
        browser_names = ['Chrome', 'Firefox', 'Brave', 'Edge', 'Opera', 'Safari']
        
        for browser in browser_names:
            # Check for exact match first
            if browser in path_parts:
                return browser
            
            # Check for case-insensitive match
            for part in path_parts:
                if part.lower() == browser.lower():
                    return browser
        
        # Additional checks for common variations
        path_str = str(relative_path).lower()
        if 'brave' in path_str:
            return 'Brave'
        elif 'chrome' in path_str:
            return 'Chrome'
        elif 'firefox' in path_str:
            return 'Firefox'
        elif 'edge' in path_str:
            return 'Edge'
        elif 'opera' in path_str:
            return 'Opera'
        elif 'safari' in path_str:
            return 'Safari'
        
        return "Unknown"
    
    def _process_wallet_folder(self, wallet_path: Path, wallet_folder: str, browser: str = "Unknown") -> List[Dict]:
        """Process a specific wallet folder"""
        
        extractor = self.get_wallet_extractor(wallet_folder)
        if not extractor:
            print(f"❌ No extractor found for wallet: {wallet_folder}")
            return []
        
        all_addresses = []
        
        # Process all files in the wallet folder
        for file_path in wallet_path.rglob('*'):
            if file_path.is_file():
                if file_path.suffix.lower() == '.log':
                    addresses = extractor.extract_from_log_file(str(file_path))
                    # Add browser information to each address
                    for addr in addresses:
                        addr['browser'] = browser
                    all_addresses.extend(addresses)
                elif file_path.suffix.lower() == '.ldb':
                    addresses = extractor.extract_from_ldb_file(str(file_path))
                    # Add browser information to each address
                    for addr in addresses:
                        addr['browser'] = browser
                    all_addresses.extend(addresses)
        
        return all_addresses
    
    def _remove_duplicates(self, addresses: List[Dict]) -> List[Dict]:
        """Remove duplicate addresses while preserving metadata"""
        
        seen = set()
        unique_addresses = []
        
        for addr in addresses:
            address_lower = addr['address'].lower()
            if address_lower not in seen:
                seen.add(address_lower)
                unique_addresses.append(addr)
            else:
                # Update existing entry with additional sources if needed
                existing = next(a for a in unique_addresses if a['address'].lower() == address_lower)
                if addr['source'] not in existing.get('sources', []):
                    if 'sources' not in existing:
                        existing['sources'] = [existing['source']]
                    existing['sources'].append(addr['source'])
        
        return unique_addresses

def main():
    """Main function for testing"""
    
    print("=" * 80)
    print("WALLET ADDRESS EXTRACTOR")
    print("=" * 80)
    
    # Example usage
    processor = WalletProcessor()
    
    # You can test with a specific folder path
    # folder_path = "64_Duxs-MacBook-Pro.local"  # Replace with actual path
    
    # For now, let's test with the current directory structure
    folder_path = "."  # Current directory
    
    print(f"🎯 Processing folder: {folder_path}")
    print("=" * 80)
    
    addresses = processor.process_folder(folder_path)
    
    if addresses:
        print(f"\n✅ SUCCESS! Found {len(addresses)} unique addresses:")
        print("-" * 60)
        
        for i, addr in enumerate(addresses, 1):
            print(f"{i:2d}. {addr['address']}")
            print(f"    Account ID: {addr['account_id']}")
            print(f"    Source: {addr['source']}")
            print(f"    File: {addr['file']}")
            print(f"    Wallet: {addr['wallet']}")
            if 'sources' in addr:
                print(f"    Sources: {', '.join(addr['sources'])}")
            print()
        
        print(f"📊 Summary: {len(addresses)} unique addresses extracted")
    else:
        print(f"\n❌ No addresses found in {folder_path}")
    
    print("=" * 80)

if __name__ == "__main__":
    main() 