#!/usr/bin/env python3
"""
Database service for saving wallet addresses and balances
"""

from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from database_models import db_manager, Address, Balance, ExtractionSession
from debank_client import debank_client

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def save_addresses(self, addresses: List[Dict]) -> bool:
        """
        Save extracted addresses to database
        
        Args:
            addresses (List[Dict]): List of address dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        session = self.db_manager.get_session()
        
        try:
            saved_count = 0
            for addr_data in addresses:
                # Check if address already exists
                existing = session.query(Address).filter(Address.address == addr_data['address']).first()
                
                if existing:
                    # Update existing record
                    existing.account_id = addr_data.get('account_id', existing.account_id)
                    existing.wallet_type = addr_data.get('wallet', existing.wallet_type)
                    existing.browser = addr_data.get('browser', existing.browser)
                    existing.source = addr_data.get('source', existing.source)
                    existing.file_path = addr_data.get('file_path', existing.file_path)
                    existing.file_name = addr_data.get('file', existing.file_name)
                    existing.address_metadata = addr_data
                    existing.extracted_at = datetime.utcnow()
                    print(f"🔄 Updated existing address: {addr_data['address']}")
                else:
                    # Create new record
                    new_address = Address(
                        address=addr_data['address'],
                        account_id=addr_data.get('account_id'),
                        wallet_type=addr_data.get('wallet'),
                        browser=addr_data.get('browser', 'Unknown'),
                        source=addr_data.get('source'),
                        file_path=addr_data.get('file_path'),
                        file_name=addr_data.get('file'),
                        address_metadata=addr_data,
                        extracted_at=datetime.utcnow()
                    )
                    session.add(new_address)
                    print(f"💾 Saved new address: {addr_data['address']}")
                
                saved_count += 1
            
            session.commit()
            print(f"✅ Successfully saved {saved_count} addresses to database")
            return True
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving addresses to database: {e}")
            return False
        finally:
            self.db_manager.close_session(session)
    
    def save_balance(self, address: str, balance_data: Dict) -> bool:
        """
        Save total balance information for an address
        
        Args:
            address (str): Ethereum address
            balance_data (Dict): Balance data from DeBank API
            
        Returns:
            bool: True if successful, False otherwise
        """
        session = self.db_manager.get_session()
        
        try:
            # Parse balance data to get total_usd_value
            parsed_data = debank_client.parse_balance_data(balance_data.get('total_balance', {}))
            
            # Check if balance record already exists
            existing = session.query(Balance).filter(Balance.address == address).first()
            
            if existing:
                # Update existing record
                existing.total_balance_usd = parsed_data['total_balance_usd']
                existing.last_updated = datetime.utcnow()
                existing.is_valid = parsed_data['is_valid']
                existing.error_message = parsed_data['error_message']
                print(f"🔄 Updated total balance for: {address}")
            else:
                # Create new record
                new_balance = Balance(
                    address=address,
                    total_balance_usd=parsed_data['total_balance_usd'],
                    last_updated=datetime.utcnow(),
                    is_valid=parsed_data['is_valid'],
                    error_message=parsed_data['error_message']
                )
                session.add(new_balance)
                print(f"💾 Saved total balance for: {address}")
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving total balance for {address}: {e}")
            return False
        finally:
            self.db_manager.close_session(session)
    
    def save_multiple_balances(self, balance_results: Dict[str, Dict]) -> bool:
        """
        Save balances for multiple addresses
        
        Args:
            balance_results (Dict): Address to balance mapping
            
        Returns:
            bool: True if successful, False otherwise
        """
        success_count = 0
        total_count = len(balance_results)
        
        for address, balance_data in balance_results.items():
            if self.save_balance(address, balance_data):
                success_count += 1
        
        print(f"✅ Successfully saved {success_count}/{total_count} balances")
        return success_count == total_count
    
    def create_extraction_session(self, folder_path: str, total_addresses: int, browsers_found: List[str]) -> int:
        """
        Create a new extraction session record
        
        Args:
            folder_path (str): Path to the extracted folder
            total_addresses (int): Number of addresses found
            browsers_found (List[str]): List of browsers found
            
        Returns:
            int: Session ID
        """
        session = self.db_manager.get_session()
        
        try:
            extraction_session = ExtractionSession(
                folder_path=folder_path,
                total_addresses=total_addresses,
                browsers_found=browsers_found,
                started_at=datetime.utcnow(),
                status='running'
            )
            
            session.add(extraction_session)
            session.commit()
            
            session_id = extraction_session.id
            print(f"📊 Created extraction session: {session_id}")
            return session_id
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error creating extraction session: {e}")
            return None
        finally:
            self.db_manager.close_session(session)
    
    def complete_extraction_session(self, session_id: int, status: str = 'completed') -> bool:
        """
        Mark extraction session as completed
        
        Args:
            session_id (int): Session ID
            status (str): Final status
            
        Returns:
            bool: True if successful, False otherwise
        """
        session = self.db_manager.get_session()
        
        try:
            extraction_session = session.query(ExtractionSession).filter(ExtractionSession.id == session_id).first()
            
            if extraction_session:
                extraction_session.completed_at = datetime.utcnow()
                extraction_session.status = status
                session.commit()
                print(f"✅ Completed extraction session: {session_id}")
                return True
            else:
                print(f"❌ Extraction session not found: {session_id}")
                return False
                
        except Exception as e:
            session.rollback()
            print(f"❌ Error completing extraction session: {e}")
            return False
        finally:
            self.db_manager.close_session(session)
    
    def get_addresses_without_balances(self) -> List[str]:
        """
        Get addresses that don't have balance information
        
        Returns:
            List[str]: List of addresses without balances
        """
        session = self.db_manager.get_session()
        
        try:
            # Find addresses that don't have corresponding balance records
            addresses_with_balances = session.query(Balance.address).distinct()
            addresses_with_balances = [addr[0] for addr in addresses_with_balances]
            
            all_addresses = session.query(Address.address).distinct()
            all_addresses = [addr[0] for addr in all_addresses]
            
            addresses_without_balances = [addr for addr in all_addresses if addr not in addresses_with_balances]
            
            return addresses_without_balances
            
        except Exception as e:
            print(f"❌ Error getting addresses without balances: {e}")
            return []
        finally:
            self.db_manager.close_session(session)
    
    def get_total_balance_summary(self) -> Dict:
        """
        Get summary of total balances across all addresses
        
        Returns:
            Dict: Summary statistics
        """
        session = self.db_manager.get_session()
        
        try:
            # Get all valid balances
            balances = session.query(Balance).filter(Balance.is_valid == True).all()
            
            total_usd = sum(b.total_balance_usd or 0 for b in balances)
            address_count = len(balances)
            
            return {
                'total_addresses': address_count,
                'total_balance_usd': total_usd,
                'average_balance_usd': total_usd / address_count if address_count > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ Error getting balance summary: {e}")
            return {}
        finally:
            self.db_manager.close_session(session)

# Global database service instance
db_service = DatabaseService() 