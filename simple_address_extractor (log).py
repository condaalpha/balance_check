#!/usr/bin/env python3
"""
Simple address extractor based on 1_process_log_folders.py logic.
Only extracts and prints addresses from a specific log file.
"""

import json
import os
from pathlib import Path

def extract_addresses_from_log(log_file_path):
    """
    Extract addresses from a log file using the same logic as 1_process_log_folders.py
    
    Args:
        log_file_path (str): Path to the log file
        
    Returns:
        list: List of extracted addresses
    """
    
    if not os.path.exists(log_file_path):
        print(f"❌ File not found: {log_file_path}")
        return []
    
    print(f"🔍 Processing: {os.path.basename(log_file_path)}")
    
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Look for internalAccounts key
        key = '"internalAccounts"'
        key_index = content.find(key)
        
        if key_index == -1:
            print(f"⚠️ 'internalAccounts' not found in {os.path.basename(log_file_path)}")
            return []
        
        print("✅ Found 'internalAccounts' structure")
        
        # Find the opening brace after the key
        brace_start = content.find('{', key_index)
        if brace_start == -1:
            print(f"⚠️ Opening brace not found after key in {os.path.basename(log_file_path)}")
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
                if address and address not in addresses:
                    addresses.append(address)
                    print(f"📄 Found account: {account_id} -> {address}")
        
        return addresses
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return []
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return []

def main():
    """Main function"""
    
    print("=" * 60)
    print("SIMPLE ADDRESS EXTRACTOR")
    print("=" * 60)
    
    # Target log file
    log_file = "1753902236563_1142622.log"
    
    print(f"🎯 Extracting addresses from: {log_file}")
    print("=" * 60)
    
    # Extract addresses
    addresses = extract_addresses_from_log(log_file)
    
    if addresses:
        print(f"\n✅ SUCCESS! Found {len(addresses)} addresses:")
        print("-" * 50)
        
        for i, address in enumerate(addresses, 1):
            print(f"{i:2d}. {address}")
        
        print(f"\n📊 Summary: {len(addresses)} unique addresses extracted")
    else:
        print(f"\n❌ No addresses found in {log_file}")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 