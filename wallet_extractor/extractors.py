"""
Wallet extractors module
Contains extractors for different wallet types
"""

import re
import json
import os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from wallet_extractor.config import Config

class WalletExtractor(ABC):
    """Abstract base class for wallet extractors"""
    
    @abstractmethod
    def extract_from_log_file(self, file_path: str) -> List[Dict]:
        """Extract addresses from log files"""
        pass
    
    @abstractmethod
    def extract_from_ldb_file(self, file_path: str) -> List[Dict]:
        """Extract addresses from LDB files"""
        pass
    
    @abstractmethod
    def get_wallet_name(self) -> str:
        """Get wallet name"""
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
    """Main processor for extracting wallet addresses"""
    
    def __init__(self):
        self.extractors = {
            Config.SUPPORTED_WALLETS['metamask']: MetaMaskExtractor()
        }
    
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
    
    def process_folder_with_progress(self, folder_path: str, progress_callback=None) -> List[Dict]:
        """
        Process a wallet folder and extract all addresses from any browser structure with progress tracking
        
        Args:
            folder_path (str): Path to the wallet folder (e.g., '64_Duxs-MacBook-Pro.local')
            progress_callback (callable): Function to call with progress updates (current, total, message)
            
        Returns:
            List[Dict]: List of extracted addresses with metadata
        """
        
        folder_path = Path(folder_path)
        if not folder_path.exists():
            print(f"❌ Folder not found: {folder_path}")
            return []
        
        print(f"🔍 Processing folder: {folder_path.name}")
        
        if progress_callback:
            progress_callback(0, 100, "Scanning for wallet folders...")
        
        # First, find all wallet folders and count total files
        all_files_to_process = []
        wallet_folders_found = []
        
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
                        
                        # Get all files in this wallet folder
                        all_files = list(wallet_path.rglob('*'))
                        log_files = [f for f in all_files if f.is_file() and f.suffix.lower() == '.log']
                        ldb_files = [f for f in all_files if f.is_file() and f.suffix.lower() == '.ldb']
                        
                        wallet_folders_found.append({
                            'path': wallet_path,
                            'folder': wallet_folder,
                            'browser': browser,
                            'log_files': log_files,
                            'ldb_files': ldb_files
                        })
                        
                        all_files_to_process.extend(log_files)
                        all_files_to_process.extend(ldb_files)
            else:
                print(f"⚠️ {wallet_folder} not found in any subfolder")
        
        total_files = len(all_files_to_process)
        print(f"📊 Found {total_files} files to process across {len(wallet_folders_found)} wallet folders")
        
        if progress_callback:
            progress_callback(0, total_files, f"Found {total_files} files to process")
        
        if total_files == 0:
            if progress_callback:
                progress_callback(100, 100, "No files found to process")
            return []
        
        # Now process all files with accurate progress
        all_addresses = []
        processed_files = 0
        
        for wallet_info in wallet_folders_found:
            wallet_path = wallet_info['path']
            wallet_folder = wallet_info['folder']
            browser = wallet_info['browser']
            log_files = wallet_info['log_files']
            ldb_files = wallet_info['ldb_files']
            
            # Process log files
            for file_path in log_files:
                if progress_callback:
                    progress_callback(processed_files, total_files, f"Processing log: {file_path.name}")
                
                addresses = self.extractors[wallet_folder].extract_from_log_file(str(file_path))
                # Add browser information to each address
                for addr in addresses:
                    addr['browser'] = browser
                all_addresses.extend(addresses)
                
                processed_files += 1
            
            # Process LDB files
            for file_path in ldb_files:
                if progress_callback:
                    progress_callback(processed_files, total_files, f"Processing LDB: {file_path.name}")
                
                addresses = self.extractors[wallet_folder].extract_from_ldb_file(str(file_path))
                # Add browser information to each address
                for addr in addresses:
                    addr['browser'] = browser
                all_addresses.extend(addresses)
                
                processed_files += 1
        
        if progress_callback:
            progress_callback(processed_files, total_files, "Removing duplicates...")
        
        # Remove duplicates
        unique_addresses = self._remove_duplicates(all_addresses)
        
        if progress_callback:
            progress_callback(total_files, total_files, f"Extraction completed - Found {len(unique_addresses)} addresses")
        
        return unique_addresses
    
    def _detect_browser_from_path(self, wallet_path: Path, root_path: Path) -> str:
        """Detect browser from file path"""
        relative_path = wallet_path.relative_to(root_path)
        path_parts = relative_path.parts
        
        # Check for browser names in path parts
        for browser in Config.SUPPORTED_BROWSERS:
            if browser in path_parts:
                return browser
            
            # Case-insensitive check
            for part in path_parts:
                if part.lower() == browser.lower():
                    return browser
        
        # Additional checks for common browser patterns
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
        
        extractor = self.extractors[wallet_folder]
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
        seen_addresses = set()
        unique_addresses = []
        
        for addr in addresses:
            if addr['address'] not in seen_addresses:
                unique_addresses.append(addr)
                seen_addresses.add(addr['address'])
            else:
                # If we have a duplicate, merge the sources
                existing = next(a for a in unique_addresses if a['address'] == addr['address'])
                if 'sources' not in existing:
                    existing['sources'] = [existing['source']]
                if addr['source'] not in existing['sources']:
                    existing['sources'].append(addr['source'])
        
        print(f"✅ Extracted {len(unique_addresses)} unique addresses")
        return unique_addresses 