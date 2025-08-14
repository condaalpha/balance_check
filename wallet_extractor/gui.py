"""
Main GUI application for Wallet Extractor
Provides user interface for wallet address extraction and balance checking
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
from datetime import datetime
from pathlib import Path

from wallet_extractor.config import Config
from wallet_extractor.extractors import WalletProcessor
from wallet_extractor.api_client import DeBankClient
# Temporarily disabled for faster startup
# from wallet_extractor.database_service import db_service
# from wallet_extractor.models import db_manager
from wallet_extractor.wallet_config import WalletConfig

class ModernTheme:
    """Modern dark theme colors and styles"""
    
    # Color palette
    BG_PRIMARY = "#1e1e1e"      # Main background
    BG_SECONDARY = "#2d2d2d"    # Secondary background
    BG_TERTIARY = "#3c3c3c"     # Tertiary background
    FG_PRIMARY = "#ffffff"      # Primary text
    FG_SECONDARY = "#b0b0b0"    # Secondary text
    ACCENT_PRIMARY = "#007acc"  # Primary accent (blue)
    ACCENT_SECONDARY = "#4ec9b0" # Secondary accent (teal)
    SUCCESS = "#4caf50"         # Success green
    WARNING = "#ff9800"         # Warning orange
    ERROR = "#f44336"           # Error red
    BORDER = "#404040"          # Border color
    
    @classmethod
    def apply_theme(cls, root):
        """Apply modern dark theme to the application"""
        style = ttk.Style()
        
        # Configure the root window
        root.configure(bg=cls.BG_PRIMARY)
        
        # Configure ttk styles
        style.theme_use('clam')  # Use clam as base theme
        
        # Configure common styles
        style.configure('TFrame', background=cls.BG_PRIMARY)
        style.configure('TLabel', background=cls.BG_PRIMARY, foreground=cls.FG_PRIMARY)
        style.configure('TButton', 
                       background=cls.ACCENT_PRIMARY, 
                       foreground=cls.FG_PRIMARY,
                       borderwidth=0,
                       focuscolor=cls.ACCENT_PRIMARY)
        style.map('TButton',
                 background=[('active', cls.ACCENT_SECONDARY),
                           ('pressed', cls.BG_TERTIARY)])
        
        # Configure entry style
        style.configure('TEntry',
                       fieldbackground=cls.BG_SECONDARY,
                       foreground=cls.FG_PRIMARY,
                       borderwidth=1,
                       bordercolor=cls.BORDER)
        
        # Configure progress bar style
        style.configure('TProgressbar',
                       background=cls.ACCENT_PRIMARY,
                       troughcolor=cls.BG_SECONDARY,
                       borderwidth=0)
        
        # Configure notebook style
        style.configure('TNotebook',
                       background=cls.BG_PRIMARY,
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=cls.BG_SECONDARY,
                       foreground=cls.FG_SECONDARY,
                       padding=[10, 5],
                       borderwidth=0)
        style.map('TNotebook.Tab',
                 background=[('selected', cls.ACCENT_PRIMARY),
                           ('active', cls.BG_TERTIARY)])
        
        # Configure scrollbar style
        style.configure('TScrollbar',
                       background=cls.BG_SECONDARY,
                       troughcolor=cls.BG_PRIMARY,
                       borderwidth=0,
                       arrowcolor=cls.FG_SECONDARY)

class WalletExtractorGUI:
    """Main GUI application for Wallet Extractor"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Wallet Address Extractor")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Apply modern dark theme
        ModernTheme.apply_theme(root)
        
        # Data storage
        self.addresses = []
        self.balance_results = {}
        
        # Initialize components
        self.wallet_processor = WalletProcessor()
        self.debank_client = DeBankClient()
        
        # Create GUI
        self.create_widgets()
        self.add_button_hover_effects()
        
        # Temporarily disable database initialization for faster startup
        # self.initialize_database()
        
        # Initialize wallet dropdown
        self.initialize_wallet_dropdown()
    
    def create_widgets(self):
        """Create GUI widgets with modern styling"""
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)  # Updated row number
        
        # Title with modern styling
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 30))
        title_frame.columnconfigure(0, weight=1)
        
        title_label = tk.Label(title_frame, 
                              text="🔍 Wallet Address Extractor", 
                              font=("Segoe UI", 24, "bold"),
                              fg=ModernTheme.FG_PRIMARY,
                              bg=ModernTheme.BG_PRIMARY)
        title_label.grid(row=0, column=0)
        
        subtitle_label = tk.Label(title_frame,
                                 text="Extract, analyze, and manage wallet addresses from browser data",
                                 font=("Segoe UI", 12),
                                 fg=ModernTheme.FG_SECONDARY,
                                 bg=ModernTheme.BG_PRIMARY)
        subtitle_label.grid(row=1, column=0, pady=(5, 0))
        
        # Folder input section
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        input_frame.columnconfigure(1, weight=1)
        
        # Folder label
        folder_label = tk.Label(input_frame, 
                               text="📁 Folder Path:", 
                               font=("Segoe UI", 11, "bold"),
                               fg=ModernTheme.FG_PRIMARY,
                               bg=ModernTheme.BG_PRIMARY)
        folder_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Folder entry with modern styling
        self.folder_path_var = tk.StringVar()
        self.folder_entry = tk.Entry(input_frame, 
                                    textvariable=self.folder_path_var,
                                    font=("Segoe UI", 10),
                                    bg=ModernTheme.BG_SECONDARY,
                                    fg=ModernTheme.FG_PRIMARY,
                                    insertbackground=ModernTheme.FG_PRIMARY,
                                    relief="flat",
                                    bd=0,
                                    highlightthickness=1,
                                    highlightbackground=ModernTheme.BORDER,
                                    highlightcolor=ModernTheme.ACCENT_PRIMARY)
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        
        # Browse button with modern styling
        self.browse_button = tk.Button(input_frame, 
                                      text="Browse", 
                                      command=self.browse_folder,
                                      font=("Segoe UI", 10, "bold"),
                                      bg=ModernTheme.ACCENT_PRIMARY,
                                      fg=ModernTheme.FG_PRIMARY,
                                      relief="flat",
                                      bd=0,
                                      padx=20,
                                      pady=8,
                                      cursor="hand2")
        self.browse_button.grid(row=0, column=2, pady=5)
        
        # Wallet selection section
        wallet_frame = ttk.Frame(main_frame)
        wallet_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        wallet_frame.columnconfigure(1, weight=1)
        
        # Wallet label
        wallet_label = tk.Label(wallet_frame, 
                               text="👛 Wallet Type:", 
                               font=("Segoe UI", 11, "bold"),
                               fg=ModernTheme.FG_PRIMARY,
                               bg=ModernTheme.BG_PRIMARY)
        wallet_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Wallet dropdown
        self.wallet_var = tk.StringVar()
        self.wallet_dropdown = ttk.Combobox(wallet_frame, 
                                           textvariable=self.wallet_var,
                                           font=("Segoe UI", 10),
                                           state="readonly")
        self.wallet_dropdown.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        
        # Detect wallets button
        self.detect_button = tk.Button(wallet_frame, 
                                      text="🔍 Detect Wallets", 
                                      command=self.detect_wallets,
                                      font=("Segoe UI", 10, "bold"),
                                      bg=ModernTheme.ACCENT_SECONDARY,
                                      fg=ModernTheme.FG_PRIMARY,
                                      relief="flat",
                                      bd=0,
                                      padx=20,
                                      pady=8,
                                      cursor="hand2")
        self.detect_button.grid(row=0, column=2, pady=5)
        
        # Wallet info label
        self.wallet_info_var = tk.StringVar(value="Select a folder and detect wallets")
        self.wallet_info_label = tk.Label(wallet_frame,
                                         textvariable=self.wallet_info_var,
                                         font=("Segoe UI", 9),
                                         fg=ModernTheme.FG_SECONDARY,
                                         bg=ModernTheme.BG_PRIMARY)
        self.wallet_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Action buttons section
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Modern button styling
        button_style = {
            'font': ("Segoe UI", 10, "bold"),
            'bg': ModernTheme.ACCENT_PRIMARY,
            'fg': ModernTheme.FG_PRIMARY,
            'relief': "flat",
            'bd': 0,
            'padx': 20,
            'pady': 10,
            'cursor': "hand2"
        }
        
        self.extract_button = tk.Button(buttons_frame, 
                                       text="🔍 Extract Addresses", 
                                       command=self.extract_addresses,
                                       **button_style)
        self.extract_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.check_balances_button = tk.Button(buttons_frame, 
                                              text="💰 Check Balances", 
                                              command=self.check_balances, 
                                              state='disabled',
                                              **button_style)
        self.check_balances_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Temporarily disabled for faster startup
        # self.save_db_button = tk.Button(buttons_frame, 
        #                                text="💾 Save to Database", 
        #                                command=self.save_to_database, 
        #                                state='disabled',
        #                                **button_style)
        # self.save_db_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_button = tk.Button(buttons_frame, 
                                      text="📤 Export Results", 
                                      command=self.export_results, 
                                      state='disabled',
                                      **button_style)
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = tk.Button(buttons_frame, 
                                     text="🔄 Clear Results", 
                                     command=self.clear_results,
                                     font=("Segoe UI", 10, "bold"),
                                     bg=ModernTheme.WARNING,
                                     fg=ModernTheme.FG_PRIMARY,
                                     relief="flat",
                                     bd=0,
                                     padx=20,
                                     pady=10,
                                     cursor="hand2")
        self.clear_button.pack(side=tk.LEFT)
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress label
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = tk.Label(progress_frame, 
                                      textvariable=self.progress_var,
                                      font=("Segoe UI", 10),
                                      fg=ModernTheme.FG_SECONDARY,
                                      bg=ModernTheme.BG_PRIMARY)
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Progress bar with modern styling
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           mode='determinate', 
                                           maximum=100,
                                           length=400)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results notebook with modern styling
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Create tabs with modern text widgets
        self.create_tabs()
    
    def create_tabs(self):
        """Create modern styled tabs"""
        
        # Summary tab
        self.summary_text = self.create_modern_text_widget(self.notebook, "📊 Summary")
        
        # Addresses tab
        self.addresses_frame = self.create_addresses_tab()
        
        # Balances tab
        self.balances_text = self.create_modern_text_widget(self.notebook, "💰 Balances")
        
        # Manual Input tab
        self.manual_input_frame = self.create_manual_input_tab()
        
        # Database tab - temporarily disabled for faster startup
        # self.db_text = self.create_modern_text_widget(self.notebook, "🗄️ Database")
    
    def create_modern_text_widget(self, parent, tab_name):
        """Create a modern styled text widget"""
        # Create frame for the tab
        frame = ttk.Frame(parent)
        parent.add(frame, text=tab_name)
        
        # Create text widget with modern styling
        text_widget = tk.Text(frame, 
                             height=20, 
                             width=80,
                             font=("Consolas", 10),
                             bg=ModernTheme.BG_SECONDARY,
                             fg=ModernTheme.FG_PRIMARY,
                             insertbackground=ModernTheme.FG_PRIMARY,
                             selectbackground=ModernTheme.ACCENT_PRIMARY,
                             selectforeground=ModernTheme.FG_PRIMARY,
                             relief="flat",
                             bd=0,
                             padx=10,
                             pady=10)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure weights
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        return text_widget
    
    def create_addresses_tab(self):
        """Create addresses tab with copy button"""
        # Create frame for the tab
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📍 Addresses")
        
        # Create button frame at the top
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        button_frame.columnconfigure(1, weight=1)
        
        # Copy button with modern styling
        self.copy_addresses_button = tk.Button(button_frame, 
                                              text="📋 Copy Addresses", 
                                              command=self.copy_addresses,
                                              font=("Segoe UI", 10, "bold"),
                                              bg=ModernTheme.ACCENT_SECONDARY,
                                              fg=ModernTheme.FG_PRIMARY,
                                              relief="flat",
                                              bd=0,
                                              padx=20,
                                              pady=8,
                                              cursor="hand2",
                                              state='disabled')
        self.copy_addresses_button.grid(row=0, column=0, padx=(10, 10))
        
        # Address count label
        self.address_count_var = tk.StringVar(value="No addresses found")
        self.address_count_label = tk.Label(button_frame,
                                           textvariable=self.address_count_var,
                                           font=("Segoe UI", 10),
                                           fg=ModernTheme.FG_SECONDARY,
                                           bg=ModernTheme.BG_PRIMARY)
        self.address_count_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 10))
        
        # Create text widget with modern styling
        self.addresses_text = tk.Text(frame, 
                                     height=20, 
                                     width=80,
                                     font=("Consolas", 10),
                                     bg=ModernTheme.BG_SECONDARY,
                                     fg=ModernTheme.FG_PRIMARY,
                                     insertbackground=ModernTheme.FG_PRIMARY,
                                     selectbackground=ModernTheme.ACCENT_PRIMARY,
                                     selectforeground=ModernTheme.FG_PRIMARY,
                                     relief="flat",
                                     bd=0,
                                     padx=10,
                                     pady=10)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.addresses_text.yview)
        self.addresses_text.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.addresses_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S), pady=(0, 10))
        
        # Configure weights
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        return frame
    
    def create_manual_input_tab(self):
        """Create a tab for manual address input and balance checking"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="👤 Manual Input")

        # Manual Input Frame
        manual_input_frame = ttk.Frame(frame)
        manual_input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        manual_input_frame.columnconfigure(1, weight=1)

        # Address Input (Multiple addresses)
        address_label = tk.Label(manual_input_frame, text="Addresses:", font=("Segoe UI", 10, "bold"), fg=ModernTheme.FG_PRIMARY, bg=ModernTheme.BG_PRIMARY)
        address_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Text area for multiple addresses
        self.manual_addresses_text = tk.Text(manual_input_frame, height=4, width=50, font=("Consolas", 9), 
                                            bg=ModernTheme.BG_SECONDARY, fg=ModernTheme.FG_PRIMARY, 
                                            insertbackground=ModernTheme.FG_PRIMARY, relief="flat", bd=0)
        self.manual_addresses_text.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)
        
        # Add placeholder text
        self.manual_addresses_text.insert(tk.END, "# Enter addresses (one per line)\n# Example:\n# 0x1234567890abcdef...\n# 0xabcdef1234567890...")

        # Wallet Type Input
        wallet_label = tk.Label(manual_input_frame, text="Wallet Type:", font=("Segoe UI", 10, "bold"), fg=ModernTheme.FG_PRIMARY, bg=ModernTheme.BG_PRIMARY)
        wallet_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.manual_wallet_var = tk.StringVar()
        self.manual_wallet_dropdown = ttk.Combobox(manual_input_frame, textvariable=self.manual_wallet_var, font=("Segoe UI", 10), state="readonly")
        self.manual_wallet_dropdown.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 10), pady=5)

        # Buttons Frame
        buttons_frame = ttk.Frame(manual_input_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Balance Check Button
        self.check_manual_balance_button = tk.Button(buttons_frame, text="💰 Check Balances", command=self.check_manual_balances, 
                                                   font=("Segoe UI", 10, "bold"), bg=ModernTheme.ACCENT_SECONDARY, 
                                                   fg=ModernTheme.FG_PRIMARY, relief="flat", bd=0, padx=20, pady=8, cursor="hand2")
        self.check_manual_balance_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear Results Button
        self.clear_manual_results_button = tk.Button(buttons_frame, text="🔄 Clear Results", command=self.clear_manual_results, 
                                                   font=("Segoe UI", 10, "bold"), bg=ModernTheme.WARNING, 
                                                   fg=ModernTheme.FG_PRIMARY, relief="flat", bd=0, padx=20, pady=8, cursor="hand2")
        self.clear_manual_results_button.pack(side=tk.LEFT)

        # Results Display
        self.manual_balance_text = tk.Text(frame, height=15, width=80, font=("Consolas", 10), bg=ModernTheme.BG_SECONDARY, 
                                          fg=ModernTheme.FG_PRIMARY, insertbackground=ModernTheme.FG_PRIMARY, 
                                          selectbackground=ModernTheme.ACCENT_PRIMARY, selectforeground=ModernTheme.FG_PRIMARY, 
                                          relief="flat", bd=0, padx=10, pady=10)
        self.manual_balance_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))

        # Configure weights
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        return frame

    def copy_addresses(self):
        """Copy all addresses to clipboard"""
        if not self.addresses:
            messagebox.showwarning("Warning", "No addresses to copy")
            return
        
        try:
            # Get all addresses
            address_list = [addr['address'] for addr in self.addresses]
            addresses_text = '\n'.join(address_list)
            
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(addresses_text)
            
            # Show success message
            messagebox.showinfo("Success", f"Copied {len(address_list)} addresses to clipboard!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy addresses: {e}")
    
    def add_button_hover_effects(self):
        """Add hover effects to buttons"""
        def on_enter(event):
            if event.widget['state'] != 'disabled':
                if event.widget == self.clear_button:
                    event.widget.config(bg=ModernTheme.ERROR)
                elif event.widget == self.copy_addresses_button:
                    event.widget.config(bg=ModernTheme.SUCCESS)
                else:
                    event.widget.config(bg=ModernTheme.ACCENT_SECONDARY)
        
        def on_leave(event):
            if event.widget['state'] != 'disabled':
                if event.widget == self.clear_button:
                    event.widget.config(bg=ModernTheme.WARNING)
                elif event.widget == self.copy_addresses_button:
                    event.widget.config(bg=ModernTheme.ACCENT_SECONDARY)
                else:
                    event.widget.config(bg=ModernTheme.ACCENT_PRIMARY)
        
        # Add hover effects to all buttons
        for button in [self.extract_button, self.check_balances_button, 
                      # self.save_db_button,  # Temporarily disabled
                      self.export_button, self.browse_button, self.clear_button, 
                      self.detect_button, self.copy_addresses_button]:
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
    
    def initialize_database(self):
        """Initialize database connection - temporarily disabled for faster startup"""
        # Temporarily disabled for faster startup
        pass
        # try:
        #     # Validate configuration
        #     Config.validate_config()
        #     
        #     # Check existing tables
        #     tables_exist = db_manager.check_tables_exist()
        #     table_info = db_manager.get_table_info()
        #     
        #     # Create tables if needed
        #     db_manager.create_tables()
        #     
        #     # Show status
        #     status = "✅ Database initialized successfully\n\n"
        #     status += "📊 Tables status:\n"
        #     for table_name, info in table_info.items():
        #         status += f"  ✅ {table_name}: {info['column_count']} columns\n"
        #     
        #     status += "\n💾 Data will be preserved across application runs"
        #     
        #     self.update_db_tab(status)
        #     
        # except Exception as e:
        #     self.update_db_tab(f"❌ Database error: {e}")
    
    def initialize_wallet_dropdown(self):
        """Initialize wallet dropdown with available wallets"""
        wallet_names = WalletConfig.get_wallet_names()
        self.wallet_dropdown['values'] = wallet_names
        if wallet_names:
            self.wallet_dropdown.set(wallet_names[0])  # Set first wallet as default
        # Initialize manual wallet dropdown
        self.manual_wallet_dropdown['values'] = wallet_names
        if wallet_names:
            self.manual_wallet_dropdown.set(wallet_names[0])
        else:
            # If no wallets detected, use all supported wallets
            all_wallets = WalletConfig.get_wallet_names()
            self.manual_wallet_dropdown['values'] = all_wallets
            if all_wallets:
                self.manual_wallet_dropdown.set(all_wallets[0])
    
    def browse_folder(self):
        """Browse for folder"""
        folder_path = filedialog.askdirectory(title="Select Wallet Folder")
        if folder_path:
            self.folder_path_var.set(folder_path)
    
    def detect_wallets(self):
        """Detect wallet types from selected folder"""
        folder_path = self.folder_path_var.get().strip()
        
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder path")
            return
        
        if not Path(folder_path).exists():
            messagebox.showerror("Error", "Selected folder does not exist")
            return
        
        # Disable buttons and start progress
        self.disable_buttons()
        self.reset_progress()
        self.progress_var.set("Detecting wallets...")
        
        # Run detection in thread
        thread = threading.Thread(target=self._detect_wallets_thread, args=(folder_path,))
        thread.daemon = True
        thread.start()
    
    def _detect_wallets_thread(self, folder_path):
        """Detect wallets in background thread"""
        try:
            # Get selected wallet type
            wallet_type = self.wallet_var.get()
            
            # Create a progress callback
            def progress_callback(current, total, message):
                if total > 0:
                    percentage = int((current / total) * 100)
                    self.root.after(0, lambda: self.update_progress(percentage, message))
                else:
                    self.root.after(0, lambda: self.update_progress(0, message))
            
            # Detect wallets with progress tracking
            detected_wallets = self.wallet_processor.detect_wallets_in_folder(folder_path, wallet_type, progress_callback)
            
            # Update GUI in main thread
            self.root.after(0, lambda: self._update_wallet_detection_results(detected_wallets))
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Wallet detection error: {e}"))
    
    def extract_addresses(self):
        """Extract addresses from selected folder"""
        folder_path = self.folder_path_var.get().strip()
        selected_wallet = self.wallet_var.get()
        
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder path")
            return
        
        if not Path(folder_path).exists():
            messagebox.showerror("Error", "Selected folder does not exist")
            return
        
        if not selected_wallet:
            messagebox.showerror("Error", "Please select a wallet type")
            return
        
        # Disable buttons and start progress
        self.disable_buttons()
        self.reset_progress()
        self.progress_var.set(f"Extracting addresses from {selected_wallet}...")
        
        # Run extraction in thread
        thread = threading.Thread(target=self._extract_thread, args=(folder_path, selected_wallet))
        thread.daemon = True
        thread.start()
    
    def _extract_thread(self, folder_path, selected_wallet):
        """Extract addresses in background thread"""
        try:
            # Create a progress callback
            def progress_callback(current, total, message):
                if total > 0:
                    percentage = int((current / total) * 100)
                    self.root.after(0, lambda: self.update_progress(percentage, message))
                else:
                    self.root.after(0, lambda: self.update_progress(0, message))
            
            # Extract addresses with progress tracking and selected wallet
            self.addresses = self.wallet_processor.process_folder_with_progress(folder_path, selected_wallet, progress_callback)
            
            # Update GUI in main thread
            self.root.after(0, self._update_extraction_results)
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Extraction error: {e}"))
    
    def check_balances(self):
        """Check balances for extracted addresses"""
        if not self.addresses:
            messagebox.showerror("Error", "No addresses to check")
            return
        
        # Disable buttons and start progress
        self.disable_buttons()
        self.reset_progress()
        self.progress_var.set("Checking balances...")
        
        # Run balance checking in thread
        thread = threading.Thread(target=self._check_balances_thread)
        thread.daemon = True
        thread.start()
    
    def _check_balances_thread(self):
        """Check balances in background thread"""
        try:
            # Get addresses
            address_list = [addr['address'] for addr in self.addresses]
            
            # Create a progress callback
            def progress_callback(current, total, message):
                percentage = int((current / total) * 100) if total > 0 else 0
                self.root.after(0, lambda: self.update_progress(percentage, message))
            
            # Fetch balances with progress tracking
            self.balance_results = self.debank_client.get_multiple_balances_with_progress(address_list, progress_callback)
            
            # Update GUI in main thread
            self.root.after(0, self._update_balance_results)
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Balance checking error: {e}"))
    
    def save_to_database(self):
        """Save data to database - temporarily disabled for faster startup"""
        messagebox.showinfo("Database Disabled", "Database functionality is temporarily disabled for faster startup.")
        # Temporarily disabled for faster startup
        # if not self.addresses:
        #     messagebox.showerror("Error", "No addresses to save")
        #     return
        # 
        # # Disable buttons and start progress
        # self.disable_buttons()
        # self.reset_progress()
        # self.progress_var.set("Saving to database...")
        # 
        # # Run database save in thread
        # thread = threading.Thread(target=self._save_db_thread)
        # thread.daemon = True
        # thread.start()
    
    def _save_db_thread(self):
        """Save to database in background thread - temporarily disabled for faster startup"""
        # Temporarily disabled for faster startup
        pass
        # try:
        #     # Save addresses
        #     addresses_saved = db_service.save_addresses(self.addresses)
        #     
        #     # Save balances if available
        #     balances_saved = 0
        #     if self.balance_results:
        #         balances_saved = db_service.save_balances(self.balance_results)
        #     
        #     # Update GUI in main thread
        #     self.root.after(0, lambda: self._update_db_save_results(addresses_saved, balances_saved))
        #     
        # except Exception as e:
        #     self.root.after(0, lambda: self._show_error(f"Database save error: {e}"))
    
    def export_results(self):
        """Export results to file"""
        if not self.addresses:
            messagebox.showerror("Error", "No data to export")
            return
        
        # Ask for file path
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Prepare export data
                export_data = {
                    'extraction_info': {
                        'timestamp': datetime.now().isoformat(),
                        'total_addresses': len(self.addresses),
                        'wallets_detected': len(set(addr['wallet'] for addr in self.addresses)),
                        'browsers_found': list(set(addr.get('browser', 'Unknown') for addr in self.addresses))
                    },
                    'addresses': self.addresses,
                    'balances': self.balance_results
                }
                
                # Write to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Results exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {e}")
    
    def clear_results(self):
        """Clear all results and reset the application state"""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all results? This will allow you to work with a new folder."):
            # Clear data
            self.addresses = []
            self.balance_results = {}
            
            # Clear all text widgets
            self.summary_text.delete(1.0, tk.END)
            self.addresses_text.delete(1.0, tk.END)
            self.balances_text.delete(1.0, tk.END)
            # self.db_text.delete(1.0, tk.END)  # Temporarily disabled
            
            # Reset address count and copy button
            self.address_count_var.set("No addresses found")
            self.copy_addresses_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)
            
            # Reset progress
            self.reset_progress()
            self.progress_var.set("Ready")
            
            # Reset button states
            self._enable_buttons()
            self.check_balances_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)
            # self.save_db_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)  # Temporarily disabled
            self.export_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)
            
            # Clear folder path
            self.folder_path_var.set("")
            
            messagebox.showinfo("Success", "Results cleared! You can now select a new folder.")
    
    def _update_extraction_results(self):
        """Update GUI after extraction"""
        self.complete_progress(f"Found {len(self.addresses)} addresses")
        
        # Update tabs
        self._update_summary()
        self._update_addresses()
        
        # Enable buttons
        if self.addresses:
            self.enable_action_buttons()
    
    def _update_balance_results(self):
        """Update GUI after balance checking"""
        self.complete_progress("Balance checking completed")
        
        # Update tabs
        self._update_balances()
        self._update_summary()
    
    def _update_wallet_detection_results(self, detected_wallets):
        """Update GUI after wallet detection"""
        self.complete_progress("Wallet detection completed")
        
        if detected_wallets:
            # Update wallet info label
            self.wallet_info_var.set(f"✅ Detected {len(detected_wallets)} wallet(s): {', '.join(detected_wallets)}")
            
            # Enable extract button
            self.extract_button.config(state='normal', bg=ModernTheme.ACCENT_PRIMARY)
        else:
            # Update wallet info label
            self.wallet_info_var.set("❌ No wallets detected in the selected folder")
            
            # Disable extract button
            self.extract_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)
        
        # Enable buttons
        self._enable_buttons()
    
    def _update_db_save_results(self, addresses_saved, balances_saved):
        """Update GUI after database save - temporarily disabled for faster startup"""
        # Temporarily disabled for faster startup
        pass
        # self.complete_progress("Database save completed")
        # 
        # # Update database tab
        # self._update_database_info()
    
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
                self.debank_client.parse_balance_data(result.get('total_balance', {}))['total_balance_usd']
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
                summary += f"    File: {addr.get('file', 'Unknown')}\n"
                summary += f"    Path: {addr.get('file_path', 'Unknown')}\n"
                
                if addr['address'] in self.balance_results:
                    balance_data = self.balance_results[addr['address']]
                    parsed = self.debank_client.parse_balance_data(balance_data.get('total_balance', {}))
                    summary += f"    Balance: ${parsed['total_balance_usd']:,.2f} USD\n"
                
                summary += "\n"
        
        self.summary_text.insert(tk.END, summary)
    
    def _update_addresses(self):
        """Update addresses tab"""
        self.addresses_text.delete(1.0, tk.END)
        
        if not self.addresses:
            self.addresses_text.insert(tk.END, "No addresses found.")
            self.address_count_var.set("No addresses found")
            self.copy_addresses_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)
            return
        
        addresses = f"ADDRESSES\n{'='*50}\n\n"
        
        for addr in self.addresses:
            addresses += f"{addr['address']}\n"
        
        self.addresses_text.insert(tk.END, addresses)
        
        # Update address count and enable copy button
        self.address_count_var.set(f"{len(self.addresses)} addresses found")
        self.copy_addresses_button.config(state='normal', bg=ModernTheme.ACCENT_SECONDARY)
    
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
                parsed = self.debank_client.parse_balance_data(balance_data['total_balance'])
                balance_usd = parsed['total_balance_usd']
                total_usd += balance_usd
                balances += f"{address} => ${balance_usd:,.2f}\n"
            else:
                balances += f"{address} => No balance data\n"
        
        balances += f"\n{'='*50}\n"
        balances += f"TOTAL: ${total_usd:,.2f} USD\n"
        
        self.balances_text.insert(tk.END, balances)
    
    def _update_database_info(self):
        """Update database tab - temporarily disabled for faster startup"""
        # Temporarily disabled for faster startup
        pass
        # try:
        #     summary = db_service.get_total_balance_summary()
        #     content = f"DATABASE SUMMARY\n{'='*50}\n\n"
        #     content += f"Addresses in DB: {summary.get('total_addresses', 0)}\n"
        #     content += f"Total value: ${summary.get('total_balance_usd', 0):,.2f} USD\n"
        #     content += f"Average: ${summary.get('average_balance_usd', 0):,.2f} USD\n"
        #     
        #     self.update_db_tab(content)
        # except Exception as e:
        #     self.update_db_tab(f"❌ Database error: {e}")
    
    def update_db_tab(self, content):
        """Update database tab - temporarily disabled for faster startup"""
        # Temporarily disabled for faster startup
        pass
        # self.db_text.delete(1.0, tk.END)
        # self.db_text.insert(tk.END, content)
    
    def disable_buttons(self):
        """Disable buttons during operations"""
        self.extract_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)
        self.check_balances_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)
        # self.save_db_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)  # Temporarily disabled
        self.export_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)
        self.browse_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)
        self.detect_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)
        self.copy_addresses_button.config(state='disabled', bg=ModernTheme.BG_TERTIARY)
        # Keep clear button enabled
        self.clear_button.config(state='normal', bg=ModernTheme.WARNING)
    
    def _enable_buttons(self):
        """Enable buttons after operations"""
        self.extract_button.config(state='normal', bg=ModernTheme.ACCENT_PRIMARY)
        self.browse_button.config(state='normal', bg=ModernTheme.ACCENT_PRIMARY)
        self.detect_button.config(state='normal', bg=ModernTheme.ACCENT_SECONDARY)
        self.clear_button.config(state='normal', bg=ModernTheme.WARNING)
        # Copy button state will be managed by _update_addresses
    
    def enable_action_buttons(self):
        """Enable action buttons when addresses are found"""
        self.check_balances_button.config(state='normal', bg=ModernTheme.ACCENT_PRIMARY)
        # self.save_db_button.config(state='normal', bg=ModernTheme.ACCENT_PRIMARY)  # Temporarily disabled
        self.export_button.config(state='normal', bg=ModernTheme.ACCENT_PRIMARY)
    
    def reset_progress(self):
        """Reset progress bar"""
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = 100
    
    def update_progress(self, percentage, message):
        """Update progress bar and message"""
        self.progress_bar['value'] = percentage
        self.progress_var.set(f"{message} ({percentage}%)")
        self.root.update_idletasks()
    
    def complete_progress(self, message):
        """Complete progress with final message"""
        self.progress_bar['value'] = 100
        self.progress_var.set(message)
        self.root.update_idletasks()
    
    def _show_error(self, error_message):
        """Show error message"""
        self.progress_bar['value'] = 0
        self.progress_var.set("Error occurred")
        self._enable_buttons()
        messagebox.showerror("Error", error_message)

    def update_tabs(self):
        """Update all tabs with current data"""
        self._update_summary()
        self._update_addresses()
        self._update_balances()
        # self._update_database_info()  # Temporarily disabled

    def check_manual_balances(self):
        """Check balances for multiple manual addresses"""
        # Get addresses from text area
        addresses_text = self.manual_addresses_text.get(1.0, tk.END).strip()
        wallet_type = self.manual_wallet_var.get()

        if not addresses_text or addresses_text.startswith("#"):
            messagebox.showwarning("Warning", "Please enter addresses to check.")
            return

        if not wallet_type:
            messagebox.showwarning("Warning", "Please select a wallet type.")
            return

        # Parse addresses (one per line, ignore comments)
        addresses = []
        for line in addresses_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                addresses.append(line)

        if not addresses:
            messagebox.showwarning("Warning", "No valid addresses found.")
            return

        # Disable buttons and start progress
        self.disable_buttons()
        self.reset_progress()
        self.progress_var.set(f"Checking balances for {len(addresses)} addresses...")

        # Run balance checking in thread
        thread = threading.Thread(target=self._check_manual_balances_thread, args=(addresses, wallet_type))
        thread.daemon = True
        thread.start()

    def clear_manual_results(self):
        """Clear manual balance results"""
        self.manual_balance_text.delete(1.0, tk.END)
        self.manual_addresses_text.delete(1.0, tk.END)
        self.manual_addresses_text.insert(tk.END, "# Enter addresses (one per line)\n# Example:\n# 0x1234567890abcdef...\n# 0xabcdef1234567890...")

    def _check_manual_balances_thread(self, addresses, wallet_type):
        """Check balances for multiple addresses in background thread"""
        try:
            results = {}
            total_balance = 0.0
            valid_addresses = 0
            
            for i, address in enumerate(addresses, 1):
                # Update progress
                percentage = int((i / len(addresses)) * 100)
                self.root.after(0, lambda p=percentage, addr=address: self.update_progress(p, f"Fetching balance for {addr}..."))
                
                # Fetch balance
                balance_data = self.debank_client.get_total_balance(address)
                
                if balance_data:
                    parsed = self.debank_client.parse_balance_data(balance_data)
                    balance_usd = parsed['total_balance_usd']
                    total_balance += balance_usd
                    valid_addresses += 1
                    
                    results[address] = {
                        'balance_data': balance_data,
                        'parsed': parsed,
                        'success': True
                    }
                else:
                    results[address] = {
                        'balance_data': None,
                        'parsed': None,
                        'success': False
                    }
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.5)
            
            # Update GUI in main thread
            self.root.after(0, self._update_manual_balances_results, addresses, results, total_balance, valid_addresses, wallet_type)
            
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Manual balance checking error: {e}"))

    def _update_manual_balances_results(self, addresses, results, total_balance, valid_addresses, wallet_type):
        """Update GUI after manual balance checking for multiple addresses"""
        self.complete_progress("Manual balance checking completed")
        
        # Update manual balance text
        self.manual_balance_text.delete(1.0, tk.END)
        
        # Header
        self.manual_balance_text.insert(tk.END, f"📊 MANUAL BALANCE CHECK RESULTS\n")
        self.manual_balance_text.insert(tk.END, f"{'='*60}\n\n")
        
        # Summary
        self.manual_balance_text.insert(tk.END, f"Wallet Type: {wallet_type}\n")
        self.manual_balance_text.insert(tk.END, f"Total Addresses: {len(addresses)}\n")
        self.manual_balance_text.insert(tk.END, f"Valid Addresses: {valid_addresses}\n")
        self.manual_balance_text.insert(tk.END, f"Failed Addresses: {len(addresses) - valid_addresses}\n")
        self.manual_balance_text.insert(tk.END, f"TOTAL BALANCE: ${total_balance:,.2f} USD\n\n")
        
        # Individual results
        self.manual_balance_text.insert(tk.END, f"INDIVIDUAL ADDRESS RESULTS:\n")
        self.manual_balance_text.insert(tk.END, f"{'-'*60}\n")
        
        for address in addresses:
            result = results.get(address, {})
            self.manual_balance_text.insert(tk.END, f"\n📍 Address: {address}\n")
            
            if result.get('success'):
                parsed = result['parsed']
                balance_usd = parsed['total_balance_usd']
                self.manual_balance_text.insert(tk.END, f"   💰 Balance: ${balance_usd:,.2f} USD\n")
                self.manual_balance_text.insert(tk.END, f"   ✅ Status: Valid\n")
            else:
                self.manual_balance_text.insert(tk.END, f"   ❌ Balance: No data available\n")
                self.manual_balance_text.insert(tk.END, f"   ❌ Status: Failed to fetch\n")
        
        # Footer
        self.manual_balance_text.insert(tk.END, f"\n{'-'*60}\n")
        self.manual_balance_text.insert(tk.END, f"✅ Manual balance checking completed successfully!\n")
        
        # Enable buttons
        self._enable_buttons()

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = WalletExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 