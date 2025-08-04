#!/usr/bin/env python3
"""
Enhanced GUI with Balance Checking and Database Integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from wallet_address_extractor import WalletProcessor
from database_service import db_service
from debank_client import debank_client
from database_models import db_manager
from pathlib import Path
import threading
import json
from datetime import datetime

class EnhancedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Wallet Extractor")
        self.root.geometry("900x600")
        
        # Initialize components
        self.processor = WalletProcessor()
        self.addresses = []
        self.balance_results = {}
        
        # Create GUI
        self.create_widgets()
        self.initialize_database()
        
    def create_widgets(self):
        """Create GUI widgets"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Enhanced Wallet Address Extractor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Folder input
        ttk.Label(main_frame, text="Folder Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.folder_path_var = tk.StringVar()
        self.folder_entry = ttk.Entry(main_frame, textvariable=self.folder_path_var, width=50)
        self.folder_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        self.browse_button = ttk.Button(main_frame, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, pady=5)
        
        # Action buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        self.extract_button = ttk.Button(buttons_frame, text="Extract Addresses", 
                                        command=self.extract_addresses)
        self.extract_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.check_balances_button = ttk.Button(buttons_frame, text="Check Balances", 
                                               command=self.check_balances, state='disabled')
        self.check_balances_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_db_button = ttk.Button(buttons_frame, text="Save to DB", 
                                        command=self.save_to_database, state='disabled')
        self.save_db_button.pack(side=tk.LEFT)
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Summary tab
        self.summary_text = scrolledtext.ScrolledText(self.notebook, height=20, width=80)
        self.notebook.add(self.summary_text, text="Summary")
        
        # Addresses tab
        self.addresses_text = scrolledtext.ScrolledText(self.notebook, height=20, width=80)
        self.notebook.add(self.addresses_text, text="Addresses")
        
        # Balances tab
        self.balances_text = scrolledtext.ScrolledText(self.notebook, height=20, width=80)
        self.notebook.add(self.balances_text, text="Balances")
        
        # Database tab
        self.db_text = scrolledtext.ScrolledText(self.notebook, height=20, width=80)
        self.notebook.add(self.db_text, text="Database")
        
    def initialize_database(self):
        """Initialize database"""
        try:
            # Check existing tables
            tables_exist = db_manager.check_tables_exist()
            
            # Get table information
            table_info = db_manager.get_table_info()
            
            # Create tables if needed (safe operation)
            db_manager.create_tables()
            
            # Show status
            status = "✅ Database initialized successfully\n\n"
            status += "📊 Tables status:\n"
            for table_name, info in table_info.items():
                status += f"  ✅ {table_name}: {info['column_count']} columns\n"
            
            status += "\n💾 Data will be preserved across application runs"
            
            self.update_db_tab(status)
        except Exception as e:
            self.update_db_tab(f"❌ Database error: {e}")
    
    def browse_folder(self):
        """Browse for folder"""
        folder_path = filedialog.askdirectory(title="Select Wallet Folder")
        if folder_path:
            self.folder_path_var.set(folder_path)
    
    def extract_addresses(self):
        """Extract addresses"""
        folder_path = self.folder_path_var.get().strip()
        
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder path")
            return
        
        if not Path(folder_path).exists():
            messagebox.showerror("Error", f"Folder not found: {folder_path}")
            return
        
        # Disable buttons
        self.disable_buttons()
        self.progress_var.set("Extracting addresses...")
        self.progress_bar.start()
        
        # Run in thread
        thread = threading.Thread(target=self._extract_thread, args=(folder_path,))
        thread.daemon = True
        thread.start()
    
    def _extract_thread(self, folder_path):
        """Extract addresses in thread"""
        try:
            self.addresses = self.processor.process_folder(folder_path)
            self.root.after(0, self._update_extraction_results)
        except Exception as e:
            self.root.after(0, lambda: self._show_error(str(e)))
        finally:
            self.root.after(0, self._enable_buttons)
    
    def check_balances(self):
        """Check balances"""
        if not self.addresses:
            messagebox.showwarning("Warning", "No addresses to check")
            return
        
        # Disable buttons
        self.disable_buttons()
        self.progress_var.set("Checking balances...")
        self.progress_bar.start()
        
        # Run in thread
        thread = threading.Thread(target=self._check_balances_thread)
        thread.daemon = True
        thread.start()
    
    def _check_balances_thread(self):
        """Check balances in thread"""
        try:
            unique_addresses = list(set(addr['address'] for addr in self.addresses))
            self.balance_results = debank_client.get_multiple_balances(unique_addresses, delay=1.0)
            self.root.after(0, self._update_balance_results)
        except Exception as e:
            self.root.after(0, lambda: self._show_error(str(e)))
        finally:
            self.root.after(0, self._enable_buttons)
    
    def save_to_database(self):
        """Save to database"""
        if not self.addresses:
            messagebox.showwarning("Warning", "No addresses to save")
            return
        
        # Disable buttons
        self.disable_buttons()
        self.progress_var.set("Saving to database...")
        self.progress_bar.start()
        
        # Run in thread
        thread = threading.Thread(target=self._save_db_thread)
        thread.daemon = True
        thread.start()
    
    def _save_db_thread(self):
        """Save to database in thread"""
        try:
            addresses_saved = db_service.save_addresses(self.addresses)
            balances_saved = False
            
            if self.balance_results:
                balances_saved = db_service.save_multiple_balances(self.balance_results)
            
            self.root.after(0, lambda: self._update_db_save_results(addresses_saved, balances_saved))
        except Exception as e:
            self.root.after(0, lambda: self._show_error(str(e)))
        finally:
            self.root.after(0, self._enable_buttons)
    
    def _update_extraction_results(self):
        """Update after extraction"""
        self.progress_bar.stop()
        self.progress_var.set(f"Found {len(self.addresses)} addresses")
        
        # Update summary and addresses
        self._update_summary()
        self._update_addresses()
        
        # Enable buttons
        if self.addresses:
            self.check_balances_button.config(state='normal')
            self.save_db_button.config(state='normal')
    
    def _update_balance_results(self):
        """Update after balance check"""
        self.progress_bar.stop()
        self.progress_var.set(f"Checked {len(self.balance_results)} balances")
        
        # Update balances tab
        self._update_balances()
        
        # Update summary
        self._update_summary()
    
    def _update_db_save_results(self, addresses_saved, balances_saved):
        """Update after database save"""
        self.progress_bar.stop()
        
        if addresses_saved:
            self.progress_var.set("✅ Saved to database")
            messagebox.showinfo("Success", "Data saved to database!")
        else:
            self.progress_var.set("❌ Database save failed")
            messagebox.showerror("Error", "Failed to save to database")
        
        # Refresh database tab
        self._update_database_info()
    
    def _update_summary(self):
        """Update summary tab"""
        self.summary_text.delete(1.0, tk.END)
        
        if not self.addresses:
            self.summary_text.insert(tk.END, "No addresses found.")
            return
        
        summary = f"EXTRACTION SUMMARY\n{'='*50}\n\n"
        summary += f"Total addresses: {len(self.addresses)}\n"
        summary += f"Wallets: {len(set(addr['wallet'] for addr in self.addresses))}\n"
        summary += f"Browsers: {', '.join(set(addr.get('browser', 'Unknown') for addr in self.addresses))}\n\n"
        
        if self.balance_results:
            total_usd = sum(
                debank_client.parse_balance_data(result.get('total_balance', {}))['total_balance_usd']
                for result in self.balance_results.values()
            )
            summary += f"Total portfolio value: ${total_usd:,.2f} USD\n\n"
        
        # Group by wallet
        wallets = {}
        for addr in self.addresses:
            wallet = addr['wallet']
            if wallet not in wallets:
                wallets[wallet] = []
            wallets[wallet].append(addr)
        
        for wallet, wallet_addresses in wallets.items():
            summary += f"👛 {wallet} ({len(wallet_addresses)} addresses):\n"
            summary += f"{'-'*40}\n"
            
            for addr in wallet_addresses:
                summary += f"  {addr['address']}\n"
                summary += f"    Browser: {addr.get('browser', 'Unknown')}\n"
                
                if addr['address'] in self.balance_results:
                    balance_data = self.balance_results[addr['address']]
                    parsed = debank_client.parse_balance_data(balance_data.get('total_balance', {}))
                    summary += f"    Balance: ${parsed['total_balance_usd']:,.2f} USD\n"
                
                summary += "\n"
        
        self.summary_text.insert(tk.END, summary)
    
    def _update_addresses(self):
        """Update addresses tab"""
        self.addresses_text.delete(1.0, tk.END)
        
        if not self.addresses:
            self.addresses_text.insert(tk.END, "No addresses found.")
            return
        
        addresses = f"ADDRESSES\n{'='*50}\n\n"
        
        for addr in self.addresses:
            addresses += f"{addr['address']}\n"
        
        self.addresses_text.insert(tk.END, addresses)
    
    def _update_balances(self):
        """Update balances tab"""
        self.balances_text.delete(1.0, tk.END)
        
        if not self.balance_results:
            self.balances_text.insert(tk.END, "No balance data available.")
            return
        
        balances = f"BALANCES\n{'='*50}\n\n"
        
        total_usd = 0
        for address, balance_data in self.balance_results.items():
            if balance_data.get('total_balance'):
                parsed = debank_client.parse_balance_data(balance_data['total_balance'])
                balance_usd = parsed['total_balance_usd']
                total_usd += balance_usd
                balances += f"{address} => ${balance_usd:,.2f}\n"
            else:
                balances += f"{address} => No balance data\n"
        
        balances += f"\n{'='*50}\n"
        balances += f"TOTAL: ${total_usd:,.2f} USD\n"
        
        self.balances_text.insert(tk.END, balances)
    
    def _update_database_info(self):
        """Update database tab"""
        try:
            summary = db_service.get_total_balance_summary()
            content = f"DATABASE SUMMARY\n{'='*50}\n\n"
            content += f"Addresses in DB: {summary.get('total_addresses', 0)}\n"
            content += f"Total value: ${summary.get('total_balance_usd', 0):,.2f} USD\n"
            content += f"Average: ${summary.get('average_balance_usd', 0):,.2f} USD\n"
            
            self.update_db_tab(content)
        except Exception as e:
            self.update_db_tab(f"❌ Database error: {e}")
    
    def update_db_tab(self, content):
        """Update database tab"""
        self.db_text.delete(1.0, tk.END)
        self.db_text.insert(tk.END, content)
    
    def disable_buttons(self):
        """Disable buttons"""
        self.extract_button.config(state='disabled')
        self.check_balances_button.config(state='disabled')
        self.save_db_button.config(state='disabled')
        self.browse_button.config(state='disabled')
    
    def _enable_buttons(self):
        """Enable buttons"""
        self.extract_button.config(state='normal')
        self.browse_button.config(state='normal')
    
    def _show_error(self, error_message):
        """Show error"""
        self.progress_bar.stop()
        self.progress_var.set("Error occurred")
        messagebox.showerror("Error", f"An error occurred:\n{error_message}")

def main():
    """Main function"""
    root = tk.Tk()
    app = EnhancedGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 