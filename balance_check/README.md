# Multi-Address Balance Checker

A FastAPI-based web application for checking balances of multiple wallet addresses simultaneously using the DeBank API.

## 🚀 Features

- **Concurrent Balance Checking**: Check hundreds of addresses simultaneously
- **Modern Web UI**: Clean, responsive interface that works on all devices
- **Real-time Progress**: Live progress tracking during balance checks
- **Export Results**: Download results in JSON format
- **Error Handling**: Robust error handling for failed requests
- **Summary Statistics**: Overview of total addresses, successful/failed checks, and total balance

## 📋 Requirements

- Python 3.8+
- DeBank API key

## 🛠️ Installation

### Option 1: Standard Installation (Recommended)

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Simple Installation (Windows Compatible)

If you encounter installation issues on Windows, use the simple version:

1. **Install minimal dependencies**:
   ```bash
   pip install -r requirements_simple.txt
   ```
2. **Use the simple version**:

   ```bash
   python main_simple.py
   ```

3. **Set up your DeBank API key**:

   - Get your API key from [DeBank Pro](https://pro.debank.com/)
   - Set it as an environment variable:

     ```bash
     # Windows
     set DEBANK_API_KEY=your_api_key_here

     # Linux/Mac
     export DEBANK_API_KEY=your_api_key_here
     ```

## 🚀 Running the Application

### Development Mode

```bash
python main.py
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The application will be available at: `http://localhost:8000`

## 📖 Usage

1. **Open the web interface** in your browser
2. **Enter wallet addresses** (one per line) in the text area
3. **Click "Check Balances"** to start the process
4. **Monitor progress** in real-time
5. **View results** in the organized table
6. **Export results** if needed

### Address Format

```
# Comments start with #
0x1234567890abcdef1234567890abcdef12345678
0xabcdef1234567890abcdef1234567890abcdef12
0x9876543210fedcba9876543210fedcba98765432
```

## 🌐 API Endpoints

### Web Interface

- `GET /` - Main web interface
- `GET /health` - Health check endpoint

### API Endpoints

- `POST /check-balances` - Check balances for multiple addresses

#### Request Format

```json
{
  "addresses": "0x1234...\n0x5678...\n0x9abc..."
}
```

#### Response Format

```json
{
  "success": true,
  "results": {
    "0x1234...": {
      "success": true,
      "balance_usd": 1234.56,
      "error": null
    }
  },
  "summary": {
    "total_addresses": 1,
    "successful": 1,
    "failed": 0,
    "total_balance_usd": 1234.56
  },
  "timestamp": "2023-11-15T10:30:00"
}
```

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment Options

#### Heroku

1. Create a `Procfile`:

   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set DEBANK_API_KEY=your_api_key
   git push heroku main
   ```

#### Railway

1. Connect your GitHub repository
2. Set environment variable: `DEBANK_API_KEY`
3. Deploy automatically

#### VPS/Server

1. Install dependencies
2. Set up environment variables
3. Use systemd or supervisor for process management
4. Set up nginx as reverse proxy (optional)

## 🔧 Configuration

### Environment Variables

- `DEBANK_API_KEY`: Your DeBank API key (required)
- `PORT`: Port to run the server on (default: 8000)
- `HOST`: Host to bind to (default: 0.0.0.0)

### Rate Limiting

The application includes built-in rate limiting to respect DeBank API limits:

- Concurrent requests are limited to avoid overwhelming the API
- Automatic retry logic for failed requests
- Graceful error handling

## 📊 Performance

- **Concurrent Processing**: Uses asyncio for efficient concurrent API calls
- **Memory Efficient**: Processes results in streams to handle large datasets
- **Fast Response**: Optimized for quick balance checking of 100+ addresses

## 🔒 Security

- Input validation for wallet addresses
- Error handling to prevent information leakage
- Rate limiting to prevent API abuse
- CORS configuration for web security

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**

   - Ensure `DEBANK_API_KEY` is set correctly
   - Verify the API key is valid and has proper permissions

2. **Connection Errors**

   - Check internet connectivity
   - Verify DeBank API is accessible
   - Check firewall settings

3. **Performance Issues**
   - Reduce the number of concurrent addresses
   - Check server resources
   - Monitor API rate limits

### Logs

The application logs important events to help with debugging:

- API request/response logs
- Error details
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the logs for error details
3. Create an issue with detailed information

## 🔄 Updates

Stay updated with the latest features and improvements by:

- Following the repository
- Checking for new releases
- Reading the changelog
