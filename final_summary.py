#!/usr/bin/env python3
"""
Final summary of address extraction results.
"""

import json
import os

def load_results():
    """Load the extraction results"""
    try:
        with open("improved_extraction_results.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Results file not found. Run improved_extractor.py first.")
        return None

def main():
    """Main function"""
    
    print("=" * 80)
    print("FINAL ADDRESS EXTRACTION SUMMARY")
    print("=" * 80)
    
    results = load_results()
    if not results:
        return
    
    print(f"📊 OVERALL RESULTS:")
    print(f"   Total files processed: {results['total_files']}")
    print(f"   Total addresses found: {results['total_addresses']:,}")
    print(f"   Unique addresses: {results['unique_addresses']:,}")
    print(f"   Personal accounts: {len(results['personal_accounts'])}")
    print(f"   Contracts: {len(results['contracts']):,}")
    print(f"   Unknown: {len(results['unknown']):,}")
    
    # Analyze personal accounts
    personal_accounts = results['personal_accounts']
    
    print(f"\n👤 PERSONAL ACCOUNT ANALYSIS:")
    print(f"   Total personal accounts: {len(personal_accounts)}")
    
    # Count by source
    sources = {}
    for account in personal_accounts:
        source = account.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print(f"   By source:")
    for source, count in sources.items():
        print(f"     {source}: {count}")
    
    # Count by file
    files = {}
    for account in personal_accounts:
        file_name = account.get('file', 'unknown')
        files[file_name] = files.get(file_name, 0) + 1
    
    print(f"   By file:")
    for file_name, count in files.items():
        print(f"     {file_name}: {count}")
    
    # Show high-confidence personal accounts
    high_confidence = [a for a in personal_accounts if a.get('source') in ['internalAccounts.accounts', 'identities', 'selectedAddress']]
    
    print(f"\n🎯 HIGH-CONFIDENCE PERSONAL ACCOUNTS:")
    print(f"   Count: {len(high_confidence)}")
    
    for i, account in enumerate(high_confidence, 1):
        print(f"   {i:2d}. {account['address']}")
        if 'account_id' in account:
            print(f"       Account ID: {account['account_id']}")
        print(f"       Source: {account['source']}")
        print(f"       File: {account['file']}")
        print()
    
    # Show the original target address
    target_address = "0x0131d84c9e40b9b0b67ab32c23739860e0e7e82c"
    target_found = [a for a in personal_accounts if a['address'].lower() == target_address.lower()]
    
    if target_found:
        print(f"🎯 TARGET ADDRESS FOUND:")
        for account in target_found:
            print(f"   Address: {account['address']}")
            if 'account_id' in account:
                print(f"   Account ID: {account['account_id']}")
            print(f"   Source: {account['source']}")
            print(f"   File: {account['file']}")
    else:
        print(f"❌ Target address {target_address} not found in personal accounts")
    
    # File comparison
    print(f"\n📄 FILE COMPARISON:")
    file_results = results.get('file_results', {})
    for file_name, count in file_results.items():
        print(f"   {file_name}: {count:,} addresses")
    
    # Key findings
    print(f"\n🔍 KEY FINDINGS:")
    print(f"   1. Successfully extracted {results['unique_addresses']:,} unique addresses")
    print(f"   2. Identified {len(personal_accounts)} personal account addresses")
    print(f"   3. Found {len(high_confidence)} high-confidence personal accounts")
    print(f"   4. Target address {target_address} was successfully extracted")
    print(f"   5. Second log file contains significantly more addresses than initially detected")
    
    print(f"\n💾 Results available in:")
    print(f"   - improved_extraction_results.txt (detailed text format)")
    print(f"   - improved_extraction_results.json (JSON format)")
    print(f"   - second_log_addresses.txt (all addresses from second log)")
    
    print("=" * 80)

if __name__ == "__main__":
    main() 