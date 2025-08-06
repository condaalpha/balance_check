"""
Database service for Wallet Extractor
Handles data persistence and database operations
"""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from wallet_extractor.models import db_manager, Address, Balance, ExtractionSession

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def save_addresses(self, addresses: List[Dict]) -> bool:
        """Save extracted addresses to database"""
        try:
            session = self.db_manager.get_session()
            saved_count = 0
            
            for addr_data in addresses:
                try:
                    # Check if address already exists
                    existing = session.query(Address).filter_by(address=addr_data['address']).first()
                    
                    if existing:
                        # Update existing record
                        existing.account_id = addr_data.get('account_id')
                        existing.wallet_type = addr_data.get('wallet')
                        existing.browser = addr_data.get('browser')
                        existing.source = addr_data.get('source')
                        existing.file_name = addr_data.get('file')
                        existing.file_path = addr_data.get('file_path')
                        existing.address_metadata = addr_data
                        existing.updated_at = datetime.utcnow()
                    else:
                        # Create new record
                        new_address = Address(
                            address=addr_data['address'],
                            account_id=addr_data.get('account_id'),
                            wallet_type=addr_data.get('wallet'),
                            browser=addr_data.get('browser'),
                            source=addr_data.get('source'),
                            file_name=addr_data.get('file'),
                            file_path=addr_data.get('file_path'),
                            address_metadata=addr_data
                        )
                        session.add(new_address)
                    
                    saved_count += 1
                    
                except IntegrityError:
                    # Handle duplicate key errors
                    session.rollback()
                    continue
            
            session.commit()
            print(f"✅ Saved {saved_count} addresses to database")
            return True
            
        except Exception as e:
            print(f"❌ Error saving addresses: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def save_balance(self, address: str, balance_data: Dict) -> bool:
        """Save balance data to database"""
        try:
            session = self.db_manager.get_session()
            
            # Parse balance data
            from wallet_extractor.api_client import DeBankClient
            debank_client = DeBankClient()
            parsed_data = debank_client.parse_balance_data(balance_data)
            
            # Check if balance record exists
            existing = session.query(Balance).filter_by(address=address).first()
            
            if existing:
                # Update existing record
                existing.total_balance_usd = parsed_data['total_balance_usd']
                existing.last_updated = datetime.utcnow()
                existing.is_valid = parsed_data['is_valid']
                existing.error_message = parsed_data['error_message']
            else:
                # Create new record
                new_balance = Balance(
                    address=address,
                    total_balance_usd=parsed_data['total_balance_usd'],
                    is_valid=parsed_data['is_valid'],
                    error_message=parsed_data['error_message']
                )
                session.add(new_balance)
            
            session.commit()
            return True
            
        except Exception as e:
            print(f"❌ Error saving balance for {address}: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def save_balances(self, balance_results: Dict[str, Dict]) -> int:
        """Save multiple balances to database"""
        saved_count = 0
        
        for address, result in balance_results.items():
            if result.get('total_balance'):
                if self.save_balance(address, result['total_balance']):
                    saved_count += 1
        
        print(f"✅ Saved {saved_count} balances to database")
        return saved_count
    
    def get_total_balance_summary(self) -> Dict:
        """Get summary of all balances in database"""
        try:
            session = self.db_manager.get_session()
            
            # Get all balances
            balances = session.query(Balance).filter_by(is_valid=True).all()
            
            if not balances:
                return {
                    'total_addresses': 0,
                    'total_balance_usd': 0.0,
                    'average_balance_usd': 0.0
                }
            
            total_usd = sum(b.total_balance_usd or 0 for b in balances)
            total_addresses = len(balances)
            average_usd = total_usd / total_addresses if total_addresses > 0 else 0.0
            
            return {
                'total_addresses': total_addresses,
                'total_balance_usd': total_usd,
                'average_balance_usd': average_usd
            }
            
        except Exception as e:
            print(f"❌ Error getting balance summary: {e}")
            return {
                'total_addresses': 0,
                'total_balance_usd': 0.0,
                'average_balance_usd': 0.0
            }
        finally:
            session.close()
    
    def get_all_addresses(self) -> List[Dict]:
        """Get all addresses from database"""
        try:
            session = self.db_manager.get_session()
            addresses = session.query(Address).all()
            
            return [
                {
                    'address': addr.address,
                    'account_id': addr.account_id,
                    'wallet': addr.wallet_type,
                    'browser': addr.browser,
                    'source': addr.source,
                    'file': addr.file_name,
                    'file_path': addr.file_path,
                    'metadata': addr.address_metadata
                }
                for addr in addresses
            ]
            
        except Exception as e:
            print(f"❌ Error getting addresses: {e}")
            return []
        finally:
            session.close()
    
    def get_address_balance(self, address: str) -> Optional[Dict]:
        """Get balance for a specific address"""
        try:
            session = self.db_manager.get_session()
            balance = session.query(Balance).filter_by(address=address).first()
            
            if balance:
                return {
                    'address': balance.address,
                    'total_balance_usd': balance.total_balance_usd,
                    'last_updated': balance.last_updated,
                    'is_valid': balance.is_valid,
                    'error_message': balance.error_message
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting balance for {address}: {e}")
            return None
        finally:
            session.close()
    
    def create_extraction_session(self, folder_path: str, total_addresses: int) -> str:
        """Create a new extraction session"""
        try:
            session = self.db_manager.get_session()
            
            session_id = f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            new_session = ExtractionSession(
                session_id=session_id,
                folder_path=folder_path,
                total_addresses=total_addresses,
                status='running'
            )
            
            session.add(new_session)
            session.commit()
            
            return session_id
            
        except Exception as e:
            print(f"❌ Error creating extraction session: {e}")
            session.rollback()
            return None
        finally:
            session.close()
    
    def complete_extraction_session(self, session_id: str, wallets_found: int, browsers_found: int):
        """Mark extraction session as completed"""
        try:
            session = self.db_manager.get_session()
            
            extraction_session = session.query(ExtractionSession).filter_by(session_id=session_id).first()
            
            if extraction_session:
                extraction_session.completed_at = datetime.utcnow()
                extraction_session.wallets_found = wallets_found
                extraction_session.browsers_found = browsers_found
                extraction_session.status = 'completed'
                
                session.commit()
            
        except Exception as e:
            print(f"❌ Error completing extraction session: {e}")
            session.rollback()
        finally:
            session.close()

# Global database service instance
db_service = DatabaseService() 