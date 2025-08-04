import re
import os

def extract_all_identities_keys(file_path):
    """
    Extract ALL keys of the identities object using a more robust approach
    
    Args:
        file_path (str): Path to the .ldb file
        
    Returns:
        list: List of addresses that are actual keys in identities object
    """
    try:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            return []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            
            # Method 1: Find the start of identities and capture everything until the closing brace
            # Look for "identities":{ and then find the matching closing brace
            start_pattern = r'"identities"\s*:\s*\{'
            start_match = re.search(start_pattern, content)
            
            if start_match:
                start_pos = start_match.end() - 1  # Position of the opening {
                print(f"Found identities start at position {start_pos}")
                
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
                print(f"Captured identities content from position {start_pos + 1} to {end_pos}")
                
                # Extract all address keys from this content
                key_pattern = r'"([^"]+)"\s*:\s*\{'
                keys = re.findall(key_pattern, identities_content)
                
                # Filter to only Ethereum addresses
                ethereum_keys = [key for key in keys if re.match(r'^0x[a-fA-F0-9]{40}$', key)]
                
                if ethereum_keys:
                    print(f"Found {len(ethereum_keys)} identity keys:")
                    for addr in ethereum_keys:
                        print(f"  - {addr}")
                    return ethereum_keys
                else:
                    print("No Ethereum address keys found in identities object")
            else:
                print("Identities object not found")
            
            return []
            
    except Exception as e:
        print(f"Error processing file: {e}")
        return []

def main():
    file_path = "1753899923248_446365.ldb"
    
    print(f"Extracting ALL identities keys from: {file_path}")
    print("-" * 50)
    
    keys = extract_all_identities_keys(file_path)
    
    print("\n" + "=" * 50)
    print("ALL IDENTITIES RESULTS:")
    print("=" * 50)
    
    if keys:
        print(f"Found {len(keys)} identity keys:")
        for i, key in enumerate(keys, 1):
            print(f"{i}. {key}")
    else:
        print("No identity keys found")
    
    print("=" * 50)

if __name__ == "__main__":
    main()