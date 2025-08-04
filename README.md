# Enhanced Wallet Address Extractor

A comprehensive tool for extracting wallet addresses from browser data, checking balances via DeBank API, and storing results in PostgreSQL database.

## 🚀 Features

### ✅ **Address Extraction**

- **Multi-browser support**: Chrome, Firefox, Brave, Edge, Opera, Safari
- **Flexible folder structure**: Automatically finds MetaMask folders in any browser structure
- **Multiple file types**: Processes `.log` and `.ldb` files
- **Duplicate removal**: Automatically removes duplicate addresses
- **Browser detection**: Identifies which browser each address came from

### ✅ **Balance Checking**

- **DeBank API integration**: Fetches real-time balance information
- **Multi-chain support**: Gets balances across different blockchain networks
- **Rate limiting**: Built-in rate limiting to respect API limits
- **Error handling**: Graceful handling of API errors and network issues

### ✅ **Database Storage**

- **PostgreSQL integration**: Secure, reliable database storage
- **Structured data**: Organized tables for addresses, balances, and sessions
- **Data integrity**: ACID compliance for financial data
- **Query capabilities**: Powerful SQL queries for analysis

### ✅ **User Interface**

- **Modern GUI**: Clean, intuitive interface with tkinter
- **Real-time progress**: Progress bars and status updates
- **Multi-tab results**: Summary, Balances, Database, and JSON views
- **Export options**: JSON and CSV export capabilities

## 📋 Requirements

- Python 3.7+
- PostgreSQL database (Aiven Cloud PostgreSQL)
- DeBank API access key
- Internet connection for balance checking

## 🛠️ Installation

### 1. **Clone or Download**

Download all files to your working directory.

### 2. **Configure Environment**

Create a `config.env` file with your credentials:

```env
# DeBank API Configuration
DEBANK_ACCESS_KEY=YOUR_ACCESSKEY

# PostgreSQL Database Configuration
DATABASE_URL=postgres://avnadmin:DB_PASSWORD@pg-88017f3-balance-check.d.aivencloud.com:11287/defaultdb?sslmode=require
```

**Important**: Replace `YOUR_ACCESSKEY` with your actual DeBank API key.

### 3. **Run Setup**

```bash
python setup.py
```

This will:

- Install required Python packages
- Test database connection
- Test DeBank API connection
- Create database tables

### 4. **Start the Application**

```bash
# Enhanced GUI (with balance checking and database)
python enhanced_gui.py

# Basic GUI (address extraction only)
python gui_wallet_extractor.py
```

## 📁 File Structure

```
Balance Check/
├── config.env                    # Configuration file (create this)
├── setup.py                      # Setup script
├── requirements.txt              # Python dependencies
├── README.md                     # This file
│
├── Core Extraction
├── wallet_address_extractor.py   # Main extraction logic
├── gui_wallet_extractor.py       # Basic GUI
│
├── Enhanced Features
├── enhanced_gui.py               # Enhanced GUI with balance checking
├── debank_client.py              # DeBank API client
├── database_models.py            # Database models
├── database_service.py           # Database operations
│
└── Example Files
├── example_other_wallet.py       # Example for adding new wallets
└── 1753899738919_446363.log      # Sample log file
```

## 🎯 Usage

### **Basic Usage (Address Extraction Only)**

1. **Run Basic GUI**:

   ```bash
   python gui_wallet_extractor.py
   ```

2. **Select Folder**: Browse to your wallet data folder (e.g., `64_Duxs-MacBook-Pro.local`)

3. **Extract Addresses**: Click "Extract Addresses" to find wallet addresses

4. **View Results**: Check the tabs for different views of extracted data

### **Enhanced Usage (With Balance Checking & Database)**

1. **Run Enhanced GUI**:

   ```bash
   python enhanced_gui.py
   ```

2. **Extract Addresses**: Same as basic usage

3. **Check Balances**: Click "Check Balances" to fetch balance information from DeBank

4. **Save to Database**: Click "Save to DB" to store results in PostgreSQL

5. **View Database**: Check the "Database" tab for stored data summary

## 🔧 Configuration

### **DeBank API Key**

Get your API key from [DeBank Pro](https://pro.debank.com/)

### **Database Connection**

The system is configured to use Aiven Cloud PostgreSQL. You can modify the connection in `config.env`.

### **Rate Limiting**

Default rate limiting is 1 second between API calls. Modify in `debank_client.py` if needed.

## 📊 Database Schema

### **Tables Created**

#### `addresses`

- `id`: Primary key
- `address`: Ethereum address (unique)
- `account_id`: Wallet account identifier
- `wallet_type`: MetaMask, Phantom, etc.
- `browser`: Chrome, Firefox, etc.
- `source`: internalAccounts, identities, etc.
- `file_path`: Full path to source file
- `file_name`: Source filename
- `metadata`: JSON with additional data
- `extracted_at`: Timestamp

#### `balances`

- `id`: Primary key
- `address`: Ethereum address
- `total_balance_usd`: Total balance in USD
- `total_balance_eth`: Total balance in ETH
- `chain_balances`: JSON with chain-specific balances
- `last_updated`: Last update timestamp
- `is_valid`: Whether balance data is valid
- `error_message`: Error message if any

#### `extraction_sessions`

- `id`: Primary key
- `folder_path`: Path to extracted folder
- `total_addresses`: Number of addresses found
- `browsers_found`: Array of browsers detected
- `started_at`: Session start time
- `completed_at`: Session completion time
- `status`: running, completed, failed

## 🔍 Example Queries

### **Find all addresses from Chrome**

```sql
SELECT * FROM addresses WHERE browser = 'Chrome';
```

### **Get total portfolio value**

```sql
SELECT SUM(total_balance_usd) as total_value FROM balances WHERE is_valid = true;
```

### **Find addresses without balance data**

```sql
SELECT a.address FROM addresses a
LEFT JOIN balances b ON a.address = b.address
WHERE b.address IS NULL;
```

### **Recent extraction sessions**

```sql
SELECT * FROM extraction_sessions
ORDER BY started_at DESC LIMIT 10;
```

## 🚨 Important Notes

### **Security**

- Keep your `config.env` file secure and never commit it to version control
- The DeBank API key provides access to financial data
- Database credentials should be kept confidential

### **Rate Limiting**

- DeBank API has rate limits
- Default delay is 1 second between requests
- Adjust in `debank_client.py` if needed

### **Data Privacy**

- This tool processes local wallet data
- Balance information is fetched from public APIs
- Consider privacy implications when storing data

### **Backup**

- Regularly backup your PostgreSQL database
- Export important data to JSON/CSV for safekeeping

## 🐛 Troubleshooting

### **Database Connection Issues**

- Check your `config.env` file
- Verify PostgreSQL server is running
- Check network connectivity

### **DeBank API Issues**

- Verify your API key is correct
- Check API rate limits
- Ensure internet connection

### **Address Extraction Issues**

- Verify folder structure contains browser data
- Check file permissions
- Ensure MetaMask extension data is present

## 🔄 Extending the System

### **Adding New Wallets**

See `example_other_wallet.py` for how to add support for new wallet types.

### **Adding New Browsers**

Modify the browser detection logic in `wallet_address_extractor.py`.

### **Custom Balance APIs**

Extend `debank_client.py` to support other balance checking services.

## 📞 Support

For issues or questions:

1. Check the troubleshooting section
2. Verify your configuration
3. Test individual components
4. Check database logs for errors

## 📄 License

This tool is for educational and personal use. Ensure compliance with:

- DeBank API terms of service
- Database provider terms
- Local privacy laws
- Financial regulations

---

**⚠️ Disclaimer**: This tool is for educational purposes. Use responsibly and ensure compliance with all applicable laws and terms of service.
