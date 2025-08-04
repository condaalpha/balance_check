import os
import json
import re
from datetime import datetime

def get_metamask_storage_path():
    """Get MetaMask storage path"""
    username = os.getenv('USERNAME') or os.getenv('USER')
    chrome_data = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data"
    metamask_id = "nkbihfbeogaeaoehlefnkodbefgpgknn"
    local_settings_path = os.path.join(chrome_data, "Default", "Local Extension Settings", metamask_id)
    return local_settings_path

def find_all_addresses_with_context(file_path):
    """Find all addresses with their surrounding context"""
    
    addresses_with_context = []
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        text_data = data.decode('utf-8', errors='ignore')
        
        # Find all Ethereum addresses
        eth_pattern = re.compile(r'0x[a-fA-F0-9]{40}')
        matches = eth_pattern.finditer(text_data)
        
        for match in matches:
            address = match.group()
            start_pos = max(0, match.start() - 200)
            end_pos = min(len(text_data), match.end() + 200)
            context = text_data[start_pos:end_pos]
            
            addresses_with_context.append({
                'address': address.lower(),
                'context': context,
                'position': match.start()
            })
        
        return addresses_with_context
        
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return []

def analyze_address_context(address_data):
    """Analyze the context around each address to determine if it's a personal account"""
    
    personal_indicators = [
        'selectedAddress', 'currentAccount', 'activeAccount', 'defaultAccount',
        'accounts', 'identities', 'addressBook', 'personal', 'wallet',
        'm/44\'/60\'/0\'/0/', 'derivation', 'hdpath', 'seed', 'mnemonic',
        'private', 'key', 'account', 'address'
    ]
    
    contract_indicators = [
        'token', 'coin', 'erc20', 'contract', 'totalSupply', 'balanceOf',
        'transfer', 'approve', 'allowance', 'mint', 'burn', 'symbol',
        'decimals', 'name', 'icon', 'logo'
    ]
    
    results = []
    
    for item in address_data:
        address = item['address']
        context = item['context'].lower()
        
        # Skip known special addresses
        if address in [
            '0x0000000000000000000000000000000000000000',
            '0xffffffffffffffffffffffffffffffffffffffff',
            '0xfffffffffffffffffffffffffffffffebaaedce6',
            '0x7ae96a2b657c07106e64479eac3434e99cf04975',
            '0x216936d3cd6e53fec0a4e231fdd6dc5c692cc760'
        ]:
            continue
        
        # Calculate personal vs contract score
        personal_score = sum(1 for indicator in personal_indicators if indicator in context)
        contract_score = sum(1 for indicator in contract_indicators if indicator in context)
        
        # Determine type based on context
        if personal_score > contract_score:
            account_type = 'personal'
        elif contract_score > personal_score:
            account_type = 'contract'
        else:
            account_type = 'unknown'
        
        results.append({
            'address': address,
            'context': item['context'],
            'personal_score': personal_score,
            'contract_score': contract_score,
            'type': account_type,
            'position': item['position']
        })
    
    return results

def find_specific_address(file_path, target_address):
    """Find a specific address and analyze its context"""
    
    target_address_lower = target_address.lower()
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        text_data = data.decode('utf-8', errors='ignore')
        
        # Find the specific address
        if target_address_lower in text_data.lower():
            index = text_data.lower().find(target_address_lower)
            start_pos = max(0, index - 300)
            end_pos = min(len(text_data), index + 300)
            context = text_data[start_pos:end_pos]
            
            return {
                'found': True,
                'address': target_address,
                'context': context,
                'position': index
            }
        else:
            return {'found': False}
        
    except Exception as e:
        return {'found': False, 'error': str(e)}

def main():
    print("=" * 80)
    print("IMPROVED METAMASK ACCOUNT FINDER")
    print("=" * 80)
    print("⚠️  WARNING: This script is for educational purposes only!")
    print("⚠️  Only use on your own systems and test environments!")
    print("=" * 80)
    
    storage_path = get_metamask_storage_path()
    
    if not os.path.exists(storage_path):
        print(f"❌ MetaMask storage not found at: {storage_path}")
        return
    
    print(f"✅ MetaMask storage path: {storage_path}")
    
    # Get all files
    files = os.listdir(storage_path)
    
    if not files:
        print("❌ No storage files found!")
        return
    
    print(f"\n📁 Found {len(files)} storage files")
    
    # Your actual address
    your_address = "0x1CEeE4d395bBECAbA02b9ca40A6472C5b2111997"
    print(f"\n🔍 Looking for your address: {your_address}")
    
    all_addresses = []
    found_your_address = False
    
    # Process each file
    for file in files:
        file_path = os.path.join(storage_path, file)
        
        if file.endswith('.ldb'):
            print(f"\n🔍 Processing LevelDB file: {file}")
            
            # Look for your specific address
            specific_result = find_specific_address(file_path, your_address)
            if specific_result['found']:
                print(f"   ✅ FOUND YOUR ADDRESS in {file}!")
                found_your_address = True
                print(f"   📍 Position: {specific_result['position']}")
                print(f"   📄 Context: {specific_result['context'][:200]}...")
            
            # Get all addresses with context
            addresses = find_all_addresses_with_context(file_path)
            all_addresses.extend(addresses)
            
            print(f"   📊 Found {len(addresses)} addresses in {file}")
    
    # Analyze all addresses
    print(f"\n🔍 Analyzing {len(all_addresses)} addresses...")
    analyzed_addresses = analyze_address_context(all_addresses)
    
    # Filter personal accounts
    personal_accounts = [addr for addr in analyzed_addresses if addr['type'] == 'personal']
    
    # Save detailed results
    output_file = "detailed_metamask_analysis.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("DETAILED METAMASK ADDRESS ANALYSIS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Target Address: {your_address}\n\n")
        
        if found_your_address:
            f.write("✅ YOUR ADDRESS WAS FOUND!\n")
            f.write("-" * 60 + "\n")
        else:
            f.write("❌ YOUR ADDRESS WAS NOT FOUND!\n")
            f.write("-" * 60 + "\n")
        
        f.write(f"\n📊 ANALYSIS SUMMARY:\n")
        f.write("-" * 60 + "\n")
        f.write(f"Total addresses found: {len(analyzed_addresses)}\n")
        f.write(f"Personal accounts: {len(personal_accounts)}\n")
        f.write(f"Contract addresses: {len([a for a in analyzed_addresses if a['type'] == 'contract'])}\n")
        f.write(f"Unknown addresses: {len([a for a in analyzed_addresses if a['type'] == 'unknown'])}\n")
        
        f.write(f"\n🏦 PERSONAL ACCOUNTS FOUND:\n")
        f.write("-" * 60 + "\n")
        
        for i, account in enumerate(personal_accounts, 1):
            f.write(f"{i}. Address: {account['address']}\n")
            f.write(f"   Personal Score: {account['personal_score']}\n")
            f.write(f"   Contract Score: {account['contract_score']}\n")
            f.write(f"   Context: {account['context'][:150]}...\n")
            f.write(f"   Etherscan: https://etherscan.io/address/{account['address']}\n\n")
        
        f.write(f"\n🔍 ALL ADDRESSES WITH SCORES:\n")
        f.write("-" * 60 + "\n")
        
        for i, addr in enumerate(analyzed_addresses[:20], 1):  # Show first 20
            f.write(f"{i:2d}. {addr['address']} ({addr['type']})\n")
            f.write(f"    Personal: {addr['personal_score']}, Contract: {addr['contract_score']}\n")
            f.write(f"    Context: {addr['context'][:100]}...\n\n")
        
        if len(analyzed_addresses) > 20:
            f.write(f"... and {len(analyzed_addresses) - 20} more addresses\n")
    
    # Display results
    print(f"\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if found_your_address:
        print(f"✅ SUCCESS: Found your address {your_address}!")
    else:
        print(f"❌ FAILED: Your address {your_address} was not found")
    
    print(f"📊 Total addresses analyzed: {len(analyzed_addresses)}")
    print(f"🏦 Personal accounts found: {len(personal_accounts)}")
    
    if personal_accounts:
        print(f"\n🏦 Personal Accounts:")
        print("-" * 60)
        for i, account in enumerate(personal_accounts, 1):
            print(f"{i}. {account['address']}")
            print(f"   Score: Personal={account['personal_score']}, Contract={account['contract_score']}")
    
    print(f"\n💾 Detailed analysis saved to: {output_file}")
    
    print(f"\n" + "=" * 80)
    print("ALGORITHM IMPROVEMENTS:")
    print("=" * 80)
    print("🔍 Why the previous algorithm failed:")
    print("   1. Too restrictive pattern matching")
    print("   2. Didn't look for your specific address")
    print("   3. Missed addresses in different contexts")
    print("   4. Incorrect filtering criteria")
    print("\n✅ This improved algorithm:")
    print("   1. Searches for your specific address")
    print("   2. Analyzes context around each address")
    print("   3. Uses scoring system to classify addresses")
    print("   4. Provides detailed context for verification")

if __name__ == "__main__":
    main() 