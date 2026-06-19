# Receipt Analysis

Automated receipt extraction and analysis system using Azure OpenAI and Google Drive/Sheets integration. This Azure Function automatically processes receipt images from Google Drive, extracts structured data using AI, and stores results in Google Sheets.

## Features

- 🤖 **AI-Powered Extraction**: Uses Azure OpenAI (Pydantic AI) to extract receipt information from images
- 📊 **Google Sheets Integration**: Automatically appends extracted data to Google Sheets
- 📁 **Google Drive Integration**: Monitors and processes receipt images from a designated folder
- ⚡ **Concurrent Processing**: Processes multiple receipts in parallel for faster execution
- 🕐 **Scheduled Execution**: Runs automatically every Saturday at midnight
- 🔄 **Duplicate Prevention**: Tracks processed files to avoid reprocessing

## Extracted Data

The system extracts the following information from receipts:

- **Receipt Date**: Transaction date in YYYY-MM-DD format (supports Malaysian DD/MM/YYYY format)
- **Title**: Vendor/store name
- **Total Amount**: Final payment amount (numeric value only)
- **Confidence**: Extraction quality assessment (low/medium/high)
- **File Name**: Original image filename from Google Drive
- **Processed Date**: Date when the receipt was processed

## Architecture

```
Google Drive (Receipt Images)
        ↓
Azure Function (Timer Trigger)
        ↓
Azure OpenAI (gpt-5.4-nano)
        ↓
Google Sheets (Structured Data)
```

## Prerequisites

- **Azure Account** with:
  - Azure Functions capability
  - Azure OpenAI or AI Foundry access
- **Google Account** with:
  - Google Drive API enabled
  - Google Sheets API enabled
  - Service account credentials
- **Python 3.12**

## Local Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Receipt-Analysis
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `local.settings.json` file:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "OPEN_AI_KEY": "your-azure-openai-key",
    "OPEN_AI_ENDPOINT": "https://your-foundry-endpoint.services.ai.azure.com/openai/v1",
    "OPEN_AI_DEPLOYMENT_NAME": "gpt-5.4-nano",
    "GOOGLE_TYPE": "service_account",
    "GOOGLE_PROJECT_ID": "your-project-id",
    "GOOGLE_PRIVATE_KEY_ID": "your-key-id",
    "GOOGLE_PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    "GOOGLE_CLIENT_EMAIL": "your-service-account@project.iam.gserviceaccount.com",
    "GOOGLE_CLIENT_ID": "your-client-id",
    "GOOGLE_AUTH_URI": "https://accounts.google.com/o/oauth2/auth",
    "GOOGLE_TOKEN_URI": "https://oauth2.googleapis.com/token",
    "GOOGLE_AUTH_PROVIDER_X509_CERT_URL": "https://www.googleapis.com/oauth2/v1/certs",
    "GOOGLE_CLIENT_X509_CERT_URL": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40project.iam.gserviceaccount.com",
    "GOOGLE_UNIVERSE_DOMAIN": "googleapis.com",
    "GOOGLE_SHEET_NAME": "Receipt Analysis",
    "GOOGLE_WORKSHEET_ID": "0",
    "GOOGLE_DRIVE_FOLDER_ID": "your-folder-id"
  }
}
```

### 4. Run Locally

```bash
func start
```

The function will run immediately due to `run_on_startup=True`.

## Azure Deployment

### 1. Create Azure Resources

- **Resource Group**: `rg-receipt-analysis`
- **Function App**: Python 3.12, Consumption or Premium plan
- **Recommended**: 1024 MB or higher instance size for concurrent processing

### 2. Deploy the Function

```bash
func azure functionapp publish <your-function-app-name>
```

### 3. Configure Application Settings

In the Azure Portal, add all environment variables from `local.settings.json` to your Function App's Application Settings.

## Google Cloud Setup

### 1. Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google Drive API and Google Sheets API
4. Create a Service Account with appropriate permissions
5. Generate and download JSON key file

### 2. Share Google Resources

- Share your Google Drive folder with the service account email
- Share your Google Sheet with the service account email (Editor access)

### 3. Get IDs

- **Drive Folder ID**: From the folder URL `https://drive.google.com/drive/folders/{FOLDER_ID}`
- **Worksheet ID**: From the sheet's gid parameter or use `0` for the first sheet

## Project Structure

```
Receipt-Analysis/
├── function_app.py          # Main Azure Function with timer trigger
├── config.py                # Configuration loader
├── requirements.txt         # Python dependencies
├── host.json               # Azure Functions host configuration
├── local.settings.json     # Local environment variables (gitignored)
├── helpers/
│   ├── __init__.py
│   ├── llm.py              # AI extraction logic (Pydantic AI)
│   ├── g_drive.py          # Google Drive integration
│   ├── g_sheet.py          # Google Sheets integration
│   └── utils.py            # Utility functions
└── README.md
```

## Configuration

### Schedule

The function runs on a CRON schedule defined in `function_app.py`:

```python
schedule="0 0 0 * * 6"  # Every Saturday at midnight
```

Modify this to change the execution frequency.

### Concurrency

Adjust concurrent processing in `function_app.py`:

```python
semaphore = asyncio.Semaphore(5)  # Process 5 files at once
```

Increase/decrease based on your API rate limits and memory.

### Supported Image Formats

- JPEG/JPG
- PNG
- WebP
- GIF
- BMP

## Supported Image Formats

Add or remove formats in `helpers/g_drive.py`:

```python
SUPPORTED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    # Add more...
}
```

## Monitoring

View logs in:
- **Local**: Terminal output when running `func start`
- **Azure**: Function App → Functions → receipt_ingestion → Monitor

## Troubleshooting

### 404 Model Not Found
- Verify `OPEN_AI_DEPLOYMENT_NAME` matches your Azure deployment
- Check endpoint URL is correct

### Google API Errors
- Ensure service account has access to Drive folder and Sheet
- Verify `GOOGLE_PRIVATE_KEY` contains `\n` (newlines)

### Memory Issues
- Increase Function App instance size
- Reduce concurrent processing (lower `Semaphore` value)

### Rate Limiting
- Decrease concurrency level
- Add delays between batches
- Check Azure OpenAI quota

## Dependencies

- `azure-functions` - Azure Functions runtime
- `openai` - OpenAI client for Azure integration
- `pydantic-ai` - AI agent framework with structured output
- `google-api-python-client` - Google Drive API
- `gspread` - Google Sheets API wrapper
- `oauth2client` - Google authentication
- `python-dotenv` - Environment variable loading

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Author

Nazmi Tarmizi
