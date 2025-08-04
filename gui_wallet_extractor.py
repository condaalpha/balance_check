#!/usr/bin/env python3
"""
GUI Wallet Address Extractor
Tkinter-based interface for processing wallet folders.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from wallet_address_extractor import WalletProcessor
from pathlib import Path
import threading
import json
from datetime import datetime

class WalletExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Wallet Address Extractor")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Initialize processor
        self.processor = WalletProcessor()
        self.addresses = []
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Wallet Address Extractor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Folder path input
        ttk.Label(main_frame, text="Folder Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.folder_path_var = tk.StringVar()
        self.folder_entry = ttk.Entry(main_frame, textvariable=self.folder_path_var, width=50)
        self.folder_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        
        self.browse_button = ttk.Button(main_frame, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=1, column=2, pady=5)
        
        # Process button
        self.process_button = ttk.Button(main_frame, text="Extract Addresses", 
                                        command=self.process_folder)
        self.process_button.grid(row=2, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="5")
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Summary tab
        self.summary_text = scrolledtext.ScrolledText(self.notebook, height=15, width=80)
        self.notebook.add(self.summary_text, text="Summary")
        
        # Details tab
        self.details_text = scrolledtext.ScrolledText(self.notebook, height=15, width=80)
        self.notebook.add(self.details_text, text="Details")
        
        # JSON tab
        self.json_text = scrolledtext.ScrolledText(self.notebook, height=15, width=80)
        self.notebook.add(self.json_text, text="JSON")
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=3, pady=(10, 0))
        
        self.save_button = ttk.Button(buttons_frame, text="Save Results", 
                                     command=self.save_results, state='disabled')
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(buttons_frame, text="Clear Results", 
                                      command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_button = ttk.Button(buttons_frame, text="Export to CSV", 
                                       command=self.export_to_csv, state='disabled')
        self.export_button.pack(side=tk.LEFT)
        
    def browse_folder(self):
        """Open folder browser dialog"""
        folder_path = filedialog.askdirectory(title="Select Wallet Folder")
        if folder_path:
            self.folder_path_var.set(folder_path)
    
    def process_folder(self):
        """Process the selected folder"""
        folder_path = self.folder_path_var.get().strip()
        
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder path")
            return
        
        if not Path(folder_path).exists():
            messagebox.showerror("Error", f"Folder not found: {folder_path}")
            return
        
        # Disable buttons during processing
        self.process_button.config(state='disabled')
        self.browse_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.export_button.config(state='disabled')
        
        # Start progress
        self.progress_var.set("Processing...")
        self.progress_bar.start()
        
        # Run processing in separate thread
        thread = threading.Thread(target=self._process_folder_thread, args=(folder_path,))
        thread.daemon = True
        thread.start()
    
    def _process_folder_thread(self, folder_path):
        """Process folder in separate thread"""
        try:
            # Process the folder
            self.addresses = self.processor.process_folder(folder_path)
            
            # Update UI in main thread
            self.root.after(0, self._update_results)
            
        except Exception as e:
            # Show error in main thread
            self.root.after(0, lambda: self._show_error(str(e)))
        finally:
            # Re-enable buttons in main thread
            self.root.after(0, self._enable_buttons)
    
    def _update_results(self):
        """Update results display"""
        # Stop progress
        self.progress_bar.stop()
        self.progress_var.set(f"Found {len(self.addresses)} addresses")
        
        # Update summary tab
        self._update_summary()
        
        # Update details tab
        self._update_details()
        
        # Update JSON tab
        self._update_json()
        
        # Enable save buttons
        if self.addresses:
            self.save_button.config(state='normal')
            self.export_button.config(state='normal')
    
    def _update_summary(self):
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
        summary += f"{'='*50}\n\n"
        summary += f"Total addresses found: {len(self.addresses)}\n"
        summary += f"Wallets detected: {len(wallets)}\n"
        summary += f"Extraction time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for wallet, wallet_addresses in wallets.items():
            summary += f"👛 {wallet} ({len(wallet_addresses)} addresses):\n"
            summary += f"{'-'*40}\n"
            
            for i, addr in enumerate(wallet_addresses, 1):
                summary += f"{i:2d}. {addr['address']}\n"
                summary += f"    Account ID: {addr['account_id']}\n"
                summary += f"    Browser: {addr.get('browser', 'Unknown')}\n"
                summary += f"    Source: {addr['source']}\n"
                summary += f"    File: {addr['file']}\n"
                if 'sources' in addr:
                    summary += f"    Sources: {', '.join(addr['sources'])}\n"
                summary += "\n"
        
        self.summary_text.insert(tk.END, summary)
    
    def _update_details(self):
        """Update details tab"""
        self.details_text.delete(1.0, tk.END)
        
        if not self.addresses:
            self.details_text.insert(tk.END, "No addresses found.")
            return
        
        details = f"DETAILED RESULTS\n"
        details += f"{'='*50}\n\n"
        
        for i, addr in enumerate(self.addresses, 1):
            details += f"Address {i}:\n"
            details += f"  Address: {addr['address']}\n"
            details += f"  Account ID: {addr['account_id']}\n"
            details += f"  Wallet: {addr['wallet']}\n"
            details += f"  Browser: {addr.get('browser', 'Unknown')}\n"
            details += f"  Source: {addr['source']}\n"
            details += f"  File: {addr['file']}\n"
            if 'sources' in addr:
                details += f"  Sources: {', '.join(addr['sources'])}\n"
            details += f"{'-'*30}\n\n"
        
        self.details_text.insert(tk.END, details)
    
    def _update_json(self):
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
                'wallets_detected': len(set(addr['wallet'] for addr in self.addresses))
            },
            'addresses': self.addresses
        }
        
        # Format JSON
        formatted_json = json.dumps(json_data, indent=2)
        self.json_text.insert(tk.END, formatted_json)
    
    def _show_error(self, error_message):
        """Show error message"""
        self.progress_bar.stop()
        self.progress_var.set("Error occurred")
        messagebox.showerror("Error", f"An error occurred:\n{error_message}")
    
    def _enable_buttons(self):
        """Re-enable buttons after processing"""
        self.process_button.config(state='normal')
        self.browse_button.config(state='normal')
    
    def save_results(self):
        """Save results to file"""
        if not self.addresses:
            messagebox.showwarning("Warning", "No results to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Results"
        )
        
        if file_path:
            try:
                json_data = {
                    'extraction_info': {
                        'timestamp': datetime.now().isoformat(),
                        'total_addresses': len(self.addresses),
                        'wallets_detected': len(set(addr['wallet'] for addr in self.addresses))
                    },
                    'addresses': self.addresses
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2)
                
                messagebox.showinfo("Success", f"Results saved to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
    
    def export_to_csv(self):
        """Export results to CSV"""
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
                    writer.writerow(['Address', 'Account ID', 'Wallet', 'Browser', 'Source', 'File', 'Sources'])
                    
                    # Write data
                    for addr in self.addresses:
                        sources = ', '.join(addr.get('sources', [])) if 'sources' in addr else ''
                        writer.writerow([
                            addr['address'],
                            addr['account_id'],
                            addr['wallet'],
                            addr.get('browser', 'Unknown'),
                            addr['source'],
                            addr['file'],
                            sources
                        ])
                
                messagebox.showinfo("Success", f"Results exported to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export file:\n{str(e)}")
    
    def clear_results(self):
        """Clear all results"""
        self.addresses = []
        self.summary_text.delete(1.0, tk.END)
        self.details_text.delete(1.0, tk.END)
        self.json_text.delete(1.0, tk.END)
        self.progress_var.set("Ready")
        self.save_button.config(state='disabled')
        self.export_button.config(state='disabled')

def main():
    """Main function"""
    root = tk.Tk()
    app = WalletExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 