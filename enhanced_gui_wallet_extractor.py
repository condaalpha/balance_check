#!/usr/bin/env python3
"""
Enhanced GUI Wallet Address Extractor with Balance Checking and Database Integration
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

class EnhancedWalletExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Wallet Address Extractor")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Initialize components
        self.processor = WalletProcessor()
        self.addresses = []
        self.balance_results = {}
        self.extraction_session_id = None
        
        # Create GUI elements
        self.create_widgets()
        
        # Initialize database
        self.initialize_database()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Enhanced Wallet Address Extractor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Folder path input
        ttk.Label(main_frame, text="Folder Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.folder_path_var = tk.StringVar()
        self.folder_entry = ttk.Entry(main_frame, textvariable=self.folder_path_var, width=60)
        self.folder_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        self.browse_button = ttk.Button(main_frame, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, pady=5)
        
        # Action buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=20)
        
        self.extract_button = ttk.Button(buttons_frame, text="Extract Addresses", 
                                        command=self.extract_addresses)
        self.extract_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.check_balances_button = ttk.Button(buttons_frame, text="Check Balances", 
                                               command=self.check_balances, state='disabled')
        self.check_balances_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.save_to_db_button = ttk.Button(buttons_frame, text="Save to Database", 
                                           command=self.save_to_database, state='disabled')
        self.save_to_db_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.refresh_button = ttk.Button(buttons_frame, text="Refresh Summary", 
                                        command=self.refresh_summary)
        self.refresh_button.pack(side=tk.LEFT)
        
        # Progress section
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="5")
        results_frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Summary tab
        self.summary_text = scrolledtext.ScrolledText(self.notebook, height=15, width=100)
        self.notebook.add(self.summary_text, text="Summary")
        
        # Addresses tab
        self.addresses_text = scrolledtext.ScrolledText(self.notebook, height=15, width=100)
        self.notebook.add(self.addresses_text, text="Addresses")
        
        # Balances tab
        self.balances_text = scrolledtext.ScrolledText(self.notebook, height=15, width=100)
        self.notebook.add(self.balances_text, text="Balances")
        
        # Database tab
        self.database_text = scrolledtext.ScrolledText(self.notebook, height=15, width=100)
        self.notebook.add(self.database_text, text="Database")
        
        # JSON tab
        self.json_text = scrolledtext.ScrolledText(self.notebook, height=15, width=100)
        self.notebook.add(self.json_text, text="JSON")
        
        # Action buttons frame
        action_buttons_frame = ttk.Frame(main_frame)
        action_buttons_frame.grid(row=6, column=0, columnspan=4, pady=(10, 0))
        
        self.export_json_button = ttk.Button(action_buttons_frame, text="Export JSON", 
                                            command=self.export_json, state='disabled')
        self.export_json_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_csv_button = ttk.Button(action_buttons_frame, text="Export CSV", 
                                           command=self.export_csv, state='disabled')
        self.export_csv_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(action_buttons_frame, text="Clear Results", 
                                      command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT)
        
    def initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            db_manager.create_tables()
            self.update_database_tab("✅ Database initialized successfully")
        except Exception as e:
            self.update_database_tab(f"❌ Database initialization failed: {e}")
    
    def browse_folder(self):
        """Open folder browser dialog"""
        folder_path = filedialog.askdirectory(title="Select Wallet Folder")
        if folder_path:
            self.folder_path_var.set(folder_path)
    
    def extract_addresses(self):
        """Extract addresses from the selected folder"""
        folder_path = self.folder_path_var.get().strip()
        
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder path")
            return
        
        if not Path(folder_path).exists():
            messagebox.showerror("Error", f"Folder not found: {folder_path}")
            return
        
        # Disable buttons during processing
        self.disable_buttons()
        
        # Start progress
        self.progress_var.set("Extracting addresses...")
        self.progress_bar.start()
        
        # Run extraction in separate thread
        thread = threading.Thread(target=self._extract_addresses_thread, args=(folder_path,))
        thread.daemon = True
        thread.start()
    
    def _extract_addresses_thread(self, folder_path):
        """Extract addresses in separate thread"""
        try:
            # Create extraction session
            browsers_found = []
            self.extraction_session_id = db_service.create_extraction_session(
                folder_path, 0, browsers_found
            )
            
            # Process the folder
            self.addresses = self.processor.process_folder(folder_path)
            
            # Update browsers found
            browsers_found = list(set(addr.get('browser', 'Unknown') for addr in self.addresses))
            if self.extraction_session_id:
                db_service.complete_extraction_session(self.extraction_session_id)
            
            # Update UI in main thread
            self.root.after(0, self._update_extraction_results)
            
        except Exception as e:
            # Show error in main thread
            self.root.after(0, lambda: self._show_error(str(e)))
        finally:
            # Re-enable buttons in main thread
            self.root.after(0, self._enable_buttons)
    
    def check_balances(self):
        """Check balances for extracted addresses"""
        if not self.addresses:
            messagebox.showwarning("Warning", "No addresses to check balances for")
            return
        
        # Disable buttons during processing
        self.disable_buttons()
        
        # Start progress
        self.progress_var.set("Checking balances...")
        self.progress_bar.start()
        
        # Run balance checking in separate thread
        thread = threading.Thread(target=self._check_balances_thread)
        thread.daemon = True
        thread.start()
    
    def _check_balances_thread(self):
        """Check balances in separate thread"""
        try:
            # Get unique addresses
            unique_addresses = list(set(addr['address'] for addr in self.addresses))
            
            # Check balances
            self.balance_results = debank_client.get_multiple_balances(unique_addresses, delay=0)
            
            # Update UI in main thread
            self.root.after(0, self._update_balance_results)
            
        except Exception as e:
            # Show error in main thread
            self.root.after(0, lambda: self._show_error(str(e)))
        finally:
            # Re-enable buttons in main thread
            self.root.after(0, self._enable_buttons)
    
    def save_to_database(self):
        """Save addresses and balances to database"""
        if not self.addresses:
            messagebox.showwarning("Warning", "No addresses to save")
            return
        
        # Disable buttons during processing
        self.disable_buttons()
        
        # Start progress
        self.progress_var.set("Saving to database...")
        self.progress_bar.start()
        
        # Run database save in separate thread
        thread = threading.Thread(target=self._save_to_database_thread)
        thread.daemon = True
        thread.start()
    
    def _save_to_database_thread(self):
        """Save to database in separate thread"""
        try:
            # Save addresses
            addresses_saved = db_service.save_addresses(self.addresses)
            
            # Save balances if available
            balances_saved = False
            if self.balance_results:
                balances_saved = db_service.save_multiple_balances(self.balance_results)
            
            # Update UI in main thread
            self.root.after(0, lambda: self._update_database_results(addresses_saved, balances_saved))
            
        except Exception as e:
            # Show error in main thread
            self.root.after(0, lambda: self._show_error(str(e)))
        finally:
            # Re-enable buttons in main thread
            self.root.after(0, self._enable_buttons)
    
    def refresh_summary(self):
        """Refresh database summary"""
        try:
            summary = db_service.get_total_balance_summary()
            self.update_database_tab(self._format_database_summary(summary))
        except Exception as e:
            self.update_database_tab(f"❌ Error refreshing summary: {e}")
    
    def _update_extraction_results(self):
        """Update results after extraction"""
        # Stop progress
        self.progress_bar.stop()
        self.progress_var.set(f"Found {len(self.addresses)} addresses")
        
        # Update tabs
        self._update_summary_tab()
        self._update_addresses_tab()
        self._update_json_tab()
        
        # Enable buttons
        if self.addresses:
            self.check_balances_button.config(state='normal')
            self.save_to_db_button.config(state='normal')
            self.export_json_button.config(state='normal')
            self.export_csv_button.config(state='normal')
    
    def _update_balance_results(self):
        """Update results after balance checking"""
        # Stop progress
        self.progress_bar.stop()
        self.progress_var.set(f"Checked balances for {len(self.balance_results)} addresses")
        
        # Update balances tab
        self._update_balances_tab()
        
        # Update summary tab
        self._update_summary_tab()
    
    def _update_database_results(self, addresses_saved, balances_saved):
        """Update results after database save"""
        # Stop progress
        self.progress_bar.stop()
        
        if addresses_saved:
            self.progress_var.set("✅ Data saved to database successfully")
            messagebox.showinfo("Success", "Data saved to database successfully!")
        else:
            self.progress_var.set("❌ Error saving to database")
            messagebox.showerror("Error", "Failed to save data to database")
        
        # Refresh database tab
        self.refresh_summary()
    
    def _update_summary_tab(self):
        """Update summary tab"""
        self.summary_text.delete(1.0, tk.END)
        
        if not self.addresses:
            self.summary_text.insert(tk.END, "No addresses found.")
            return
        
        # Group by wallet
        wallets = {}
        for addr in self.addresses:
            wallet = addr['wallet']
            if wallet not in wallets:
                wallets[wallet] = []
            wallets[wallet].append(addr)
        
        summary = f"EXTRACTION SUMMARY\n"
        summary += f"{'='*60}\n\n"
        summary += f"Total addresses found: {len(self.addresses)}\n"
        summary += f"Wallets detected: {len(wallets)}\n"
        summary += f"Extraction time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Balance summary
        if self.balance_results:
            total_usd = sum(
                debank_client.parse_balance_data(result.get('total_balance', {}))['total_balance_usd']
                for result in self.balance_results.values()
            )
            summary += f"Total balance checked: ${total_usd:,.2f} USD\n\n"
        
        for wallet, wallet_addresses in wallets.items():
            summary += f"👛 {wallet} ({len(wallet_addresses)} addresses):\n"
            summary += f"{'-'*50}\n"
            
            for i, addr in enumerate(wallet_addresses, 1):
                summary += f"{i:2d}. {addr['address']}\n"
                summary += f"    Account ID: {addr['account_id']}\n"
                summary += f"    Browser: {addr.get('browser', 'Unknown')}\n"
                summary += f"    Source: {addr['source']}\n"
                summary += f"    File: {addr['file']}\n"
                summary += f"    Path: {addr.get('file_path', 'N/A')}\n"
                
                # Add balance info if available
                if addr['address'] in self.balance_results:
                    balance_data = self.balance_results[addr['address']]
                    parsed = debank_client.parse_balance_data(balance_data.get('total_balance', {}))
                    summary += f"    Balance: ${parsed['total_balance_usd']:,.2f} USD\n"
                
                if 'sources' in addr:
                    summary += f"    Sources: {', '.join(addr['sources'])}\n"
                summary += "\n"
        
        self.summary_text.insert(tk.END, summary)
    
    def _update_addresses_tab(self):
        """Update addresses tab"""
        self.addresses_text.delete(1.0, tk.END)
        
        if not self.addresses:
            self.addresses_text.insert(tk.END, "No addresses found.")
            return
        
        addresses = f"ADDRESSES\n"
        addresses += f"{'='*60}\n\n"
        
        for addr in self.addresses:
            addresses += f"{addr['address']}\n"
        
        self.addresses_text.insert(tk.END, addresses)
    
    def _update_balances_tab(self):
        """Update balances tab"""
        self.balances_text.delete(1.0, tk.END)
        
        if not self.balance_results:
            self.balances_text.insert(tk.END, "No balance data available.")
            return
        
        balances = f"BALANCES\n"
        balances += f"{'='*60}\n\n"
        
        total_usd = 0
        for address, balance_data in self.balance_results.items():
            if balance_data.get('total_balance'):
                parsed = debank_client.parse_balance_data(balance_data['total_balance'])
                balance_usd = parsed['total_balance_usd']
                total_usd += balance_usd
                balances += f"{address} => ${balance_usd:,.2f}\n"
            else:
                balances += f"{address} => No balance data\n"
        
        balances += f"\n{'='*60}\n"
        balances += f"TOTAL: ${total_usd:,.2f} USD\n"
        
        self.balances_text.insert(tk.END, balances)
    
    def _update_json_tab(self):
        """Update JSON tab"""
        self.json_text.delete(1.0, tk.END)
        
        if not self.addresses:
            self.json_text.insert(tk.END, "No addresses found.")
            return
        
        # Create JSON structure
        json_data = {
            'extraction_info': {
                'timestamp': datetime.now().isoformat(),
                'total_addresses': len(self.addresses),
                'wallets_detected': len(set(addr['wallet'] for addr in self.addresses)),
                'browsers_found': list(set(addr.get('browser', 'Unknown') for addr in self.addresses))
            },
            'addresses': self.addresses,
            'balances': self.balance_results
        }
        
        # Format JSON
        formatted_json = json.dumps(json_data, indent=2)
        self.json_text.insert(tk.END, formatted_json)
    
    def update_database_tab(self, content):
        """Update database tab with content"""
        self.database_text.delete(1.0, tk.END)
        self.database_text.insert(tk.END, content)
    
    def _format_database_summary(self, summary):
        """Format database summary"""
        if not summary:
            return "No database summary available."
        
        content = f"DATABASE SUMMARY\n"
        content += f"{'='*60}\n\n"
        content += f"Total addresses in database: {summary.get('total_addresses', 0)}\n"
        content += f"Total portfolio value: ${summary.get('total_balance_usd', 0):,.2f} USD\n"
        content += f"Average balance per address: ${summary.get('average_balance_usd', 0):,.2f} USD\n"
        
        return content
    
    def disable_buttons(self):
        """Disable all action buttons"""
        self.extract_button.config(state='disabled')
        self.check_balances_button.config(state='disabled')
        self.save_to_db_button.config(state='disabled')
        self.browse_button.config(state='disabled')
    
    def _enable_buttons(self):
        """Re-enable buttons after processing"""
        self.extract_button.config(state='normal')
        self.browse_button.config(state='normal')
    
    def _show_error(self, error_message):
        """Show error message"""
        self.progress_bar.stop()
        self.progress_var.set("Error occurred")
        messagebox.showerror("Error", f"An error occurred:\n{error_message}")
    
    def export_json(self):
        """Export results to JSON file"""
        if not self.addresses:
            messagebox.showwarning("Warning", "No results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Results"
        )
        
        if file_path:
            try:
                json_data = {
                    'extraction_info': {
                        'timestamp': datetime.now().isoformat(),
                        'total_addresses': len(self.addresses),
                        'wallets_detected': len(set(addr['wallet'] for addr in self.addresses))
                    },
                    'addresses': self.addresses,
                    'balances': self.balance_results
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Results exported to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export file:\n{str(e)}")
    
    def export_csv(self):
        """Export results to CSV file"""
        if not self.addresses:
            messagebox.showwarning("Warning", "No results to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export to CSV"
        )
        
        if file_path:
            try:
                import csv
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow(['Address', 'Account ID', 'Wallet', 'Browser', 'Source', 'File', 'File Path', 'Balance USD'])
                    
                    # Write data
                    for addr in self.addresses:
                        balance_usd = 0
                        
                        if addr['address'] in self.balance_results:
                            balance_data = self.balance_results[addr['address']]
                            parsed = debank_client.parse_balance_data(balance_data.get('total_balance', {}))
                            balance_usd = parsed['total_balance_usd']
                        
                        writer.writerow([
                            addr['address'],
                            addr['account_id'],
                            addr['wallet'],
                            addr.get('browser', 'Unknown'),
                            addr['source'],
                            addr['file'],
                            addr.get('file_path', 'N/A'),
                            f"${balance_usd:,.2f}"
                        ])
                
                messagebox.showinfo("Success", f"Results exported to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export file:\n{str(e)}")
    
    def clear_results(self):
        """Clear all results"""
        self.addresses = []
        self.balance_results = {}
        self.extraction_session_id = None
        
        self.summary_text.delete(1.0, tk.END)
        self.addresses_text.delete(1.0, tk.END)
        self.balances_text.delete(1.0, tk.END)
        self.json_text.delete(1.0, tk.END)
        
        self.progress_var.set("Ready")
        self.check_balances_button.config(state='disabled')
        self.save_to_db_button.config(state='disabled')
        self.export_json_button.config(state='disabled')
        self.export_csv_button.config(state='disabled')

def main():
    """Main function"""
    root = tk.Tk()
    app = EnhancedWalletExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 