# Wallet Address Extractor

A comprehensive tool for extracting Ethereum wallet addresses from browser data, checking balances via DeBank API, and storing information in PostgreSQL database.

## 🚀 Features

- **Multi-Wallet Support**: Currently supports MetaMask, easily extensible for other wallets
- **Multi-Browser Support**: Works with Chrome, Firefox, Brave, Edge, Opera, Safari
- **Balance Checking**: Integrates with DeBank API to fetch real-time balances
- **Database Storage**: PostgreSQL database for persistent data storage
- **User-Friendly GUI**: Tkinter-based interface with real-time progress updates
- **Export Functionality**: Export results to JSON format
- **Scalable Architecture**: Modular design for easy extension

## 📁 Project Structure

```
wallet_extractor/
├── __init__.py              # Package initialization
├── config.py                # Configuration management
├── models.py                # Database models and connection
├── extractors.py            # Wallet extraction logic
├── api_client.py            # DeBank API integration
├── database_service.py      # Database operations
├── gui.py                   # Main GUI application
├── main.py                  # Application entry point
├── setup.py                 # Setup and installation script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.7 or higher
- PostgreSQL database
- DeBank API access key

### Quick Setup

1. **Clone or download the project**

2. **Create configuration file**
   Create `config.env` in the project root:

   ```env
   DEBANK_ACCESS_KEY=YOUR_DEBANK_ACCESS_KEY
   DATABASE_URL=postgres://username:password@host:port/database?sslmode=require
   ```

3. **Run setup script**

   ```bash
   python wallet_extractor/setup.py
   ```

4. **Launch application**
   ```bash
   python wallet_extractor/main.py
   ```

### Manual Installation

1. **Install dependencies**

   ```bash
   pip install -r wallet_extractor/requirements.txt
   ```

2. **Create database tables**
   ```python
   from wallet_extractor.models import db_manager
   db_manager.create_tables()
   ```

## 🎯 Usage

### GUI Application

1. **Launch the application**

   ```bash
   python wallet_extractor/main.py
   ```

2. **Select folder path**

   - Click "Browse" to select a folder containing browser data
   - Example: `C:\Users\Username\AppData\Local\Google\Chrome\User Data\Default\Local Extension Settings`

3. **Extract addresses**

   - Click "Extract Addresses" to scan for wallet data
   - View results in the Summary, Addresses, and Balances tabs

4. **Check balances**

   - Click "Check Balances" to fetch current balances from DeBank
   - Balances are displayed in simple format: `address => $value`

5. **Save to database**

   - Click "Save to Database" to persist data
   - Data is preserved across application runs

6. **Export results**
   - Click "Export Results" to save data as JSON file

### Programmatic Usage

```python
from wallet_extractor.extractors import WalletProcessor
from wallet_extractor.api_client import DeBankClient
from wallet_extractor.database_service import db_service

# Extract addresses
processor = WalletProcessor()
addresses = processor.process_folder("path/to/browser/data")

# Check balances
debank_client = DeBankClient()
balance_results = debank_client.get_multiple_balances([addr['address'] for addr in addresses])

# Save to database
db_service.save_addresses(addresses)
db_service.save_balances(balance_results)
```

## 🔧 Configuration

### Supported Wallets

Currently supported wallet types:

- **MetaMask**: Extension ID `nkbihfbeogaeaoehlefnkodbefgpgknn`

### Supported Browsers

- Chrome
- Firefox
- Brave
- Edge
- Opera
- Safari

### Database Schema

#### Addresses Table

- `address`: Ethereum address (primary key)
- `account_id`: Wallet account identifier
- `wallet_type`: Type of wallet (e.g., "MetaMask")
- `browser`: Browser name
- `source`: Data source (e.g., "internalAccounts.accounts")
- `file_name`: Source file name
- `file_path`: Full file path
- `address_metadata`: JSON metadata

#### Balances Table

- `address`: Ethereum address (foreign key)
- `total_balance_usd`: Total balance in USD
- `last_updated`: Last update timestamp
- `is_valid`: Balance validity flag
- `error_message`: Error message if any

#### Extraction Sessions Table

- `session_id`: Unique session identifier
- `folder_path`: Processed folder path
- `total_addresses`: Number of addresses found
- `wallets_found`: Number of wallets detected
- `browsers_found`: Number of browsers detected
- `started_at`: Session start time
- `completed_at`: Session completion time
- `status`: Session status

## 🔌 API Integration

### DeBank API

The application integrates with DeBank API to fetch wallet balances:

- **Endpoint**: `https://pro-openapi.debank.com/v1/user/total_balance`
- **Authentication**: Access key in request header
- **Rate Limiting**: Built-in delays between requests
- **Error Handling**: Comprehensive error handling and retry logic

### Special Cases

The application handles known API limitations:

- **Hyperliquid positions**: Special handling for address `0x3b2834037a6b404315729cbe89d4a6bb55b87cc5`
- **Missing protocol data**: Estimation logic for incomplete API responses

## 🏗️ Architecture

### Modular Design

The application follows a modular architecture:

1. **Configuration Layer** (`config.py`)

   - Environment variable management
   - Application settings

2. **Data Layer** (`models.py`, `database_service.py`)

   - Database models and connections
   - Data persistence operations

3. **Business Logic Layer** (`extractors.py`, `api_client.py`)

   - Wallet data extraction
   - API integration

4. **Presentation Layer** (`gui.py`)
   - User interface
   - User interaction handling

### Extensibility

Adding new wallet support:

1. **Create new extractor class**

   ```python
   class NewWalletExtractor(WalletExtractor):
       def get_wallet_name(self) -> str:
           return "NewWallet"

       def extract_from_log_file(self, file_path: str) -> List[Dict]:
           # Implementation for log files
           pass

       def extract_from_ldb_file(self, file_path: str) -> List[Dict]:
           # Implementation for LDB files
           pass
   ```

2. **Register in configuration**

   ```python
   SUPPORTED_WALLETS = {
       'metamask': 'nkbihfbeogaeaoehlefnkodbefgpgknn',
       'newwallet': 'new_wallet_extension_id'
   }
   ```

3. **Add to processor**
   ```python
   self.extractors = {
       Config.SUPPORTED_WALLETS['metamask']: MetaMaskExtractor(),
       Config.SUPPORTED_WALLETS['newwallet']: NewWalletExtractor()
   }
   ```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**

   - Verify `DATABASE_URL` in `config.env`
   - Ensure PostgreSQL server is running
   - Check network connectivity

2. **DeBank API Error**

   - Verify `DEBANK_ACCESS_KEY` in `config.env`
   - Check API key validity
   - Ensure internet connectivity

3. **No Addresses Found**

   - Verify folder path contains browser data
   - Check for wallet extension folders
   - Ensure file permissions

4. **Import Errors**
   - Run `python wallet_extractor/setup.py`
   - Verify Python version (3.7+)
   - Check virtual environment activation

### Debug Mode

Enable debug logging by modifying `config.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 License

This project is provided as-is for educational and research purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the code comments
3. Create an issue with detailed information

---

**Note**: This tool is designed for legitimate wallet management and research purposes. Always respect privacy and security best practices when handling wallet data.
