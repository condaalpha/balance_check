"""
Wallet configuration module
Defines different wallet types and their folder structures
"""

class WalletConfig:
    """Configuration for different wallet types"""
    
    # Supported wallets with their extension IDs and folder patterns
    SUPPORTED_WALLETS = {
        'metamask': {
            'name': 'MetaMask',
            'extension_id': 'nkbihfbeogaeaoehlefnkodbefgpgknn',
            'description': 'MetaMask - Ethereum wallet and Web3 gateway',
            'file_patterns': ['*.log', '*.ldb'],
            'extractors': {
                'log': 'internalAccounts.accounts',
                'ldb': 'identities'
            }
        },
        'phantom': {
            'name': 'Phantom',
            'extension_id': 'bfnaelmomeimhlpmgjnjophhpkkoljpa',
            'description': 'Phantom - Solana wallet',
            'file_patterns': ['*.log', '*.ldb'],
            'extractors': {
                'log': 'accounts',
                'ldb': 'identities'
            }
        },
        'coinbase': {
            'name': 'Coinbase Wallet',
            'extension_id': 'hnfanknocfeofbddlgpiimogohkmkeil',
            'description': 'Coinbase Wallet - Multi-chain wallet',
            'file_patterns': ['*.log', '*.ldb'],
            'extractors': {
                'log': 'accounts',
                'ldb': 'identities'
            }
        },
        'trust': {
            'name': 'Trust Wallet',
            'extension_id': 'egjidjbpglichdcondbcbdnbeeppgdph',
            'description': 'Trust Wallet - Multi-chain wallet',
            'file_patterns': ['*.log', '*.ldb'],
            'extractors': {
                'log': 'accounts',
                'ldb': 'identities'
            }
        },
        'brave': {
            'name': 'Brave Wallet',
            'extension_id': 'odbfpeeihdkbihmopkbjmoonfanlbfcl',
            'description': 'Brave Wallet - Built into Brave browser',
            'file_patterns': ['*.log', '*.ldb'],
            'extractors': {
                'log': 'accounts',
                'ldb': 'identities'
            }
        }
    }
    
    @classmethod
    def get_wallet_names(cls):
        """Get list of wallet names"""
        return [config['name'] for config in cls.SUPPORTED_WALLETS.values()]
    
    @classmethod
    def get_wallet_by_name(cls, wallet_name):
        """Get wallet config by name"""
        for wallet_id, config in cls.SUPPORTED_WALLETS.items():
            if config['name'] == wallet_name:
                return wallet_id, config
        return None, None
    
    @classmethod
    def get_wallet_by_id(cls, wallet_id):
        """Get wallet config by ID"""
        return cls.SUPPORTED_WALLETS.get(wallet_id)
    
    @classmethod
    def detect_wallets_in_folder(cls, folder_path):
        """Detect which wallets are present in a folder"""
        import os
        from pathlib import Path
        
        detected_wallets = []
        folder = Path(folder_path)
        
        if not folder.exists():
            return detected_wallets
        
        # Search for wallet extension folders
        for wallet_id, config in cls.SUPPORTED_WALLETS.items():
            extension_id = config['extension_id']
            
            # Search recursively for the extension folder
            wallet_paths = list(folder.rglob(extension_id))
            
            if wallet_paths:
                for wallet_path in wallet_paths:
                    if wallet_path.is_dir():
                        detected_wallets.append({
                            'wallet_id': wallet_id,
                            'name': config['name'],
                            'path': str(wallet_path),
                            'description': config['description']
                        })
        
        return detected_wallets
    
    @classmethod
    def get_wallet_extractors(cls):
        """Get available extractors for each wallet"""
        extractors = {}
        for wallet_id, config in cls.SUPPORTED_WALLETS.items():
            extractors[wallet_id] = config['extractors']
        return extractors 