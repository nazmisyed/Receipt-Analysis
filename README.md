# Receipt Analysis

Automated receipt extraction and analysis system using Azure OpenAI and Google Drive/Sheets integration. This system uses GitHub Actions to automatically process receipt images from Google Drive, extract structured data using AI, and store results in Google Sheets.

## Features

- 🤖 **AI-Powered Extraction**: Uses Azure OpenAI (Pydantic AI) to extract receipt information from images
- 📊 **Google Sheets Integration**: Automatically appends extracted data to Google Sheets
- 📁 **Google Drive Integration**: Monitors and processes receipt images from a designated folder
- ⚡ **Concurrent Processing**: Processes multiple receipts in parallel for faster execution
- 🕐 **Scheduled Execution**: Runs automatically every Saturday at midnight
- 🔄 **Duplicate Prevention**: Tracks processed files to avoid reprocessing

## Extracted Data

The system extracts the following information from receipts:

- **Receipt Date & Time**: Transaction date and time in YYYY-MM-DD HH:MM format (supports Malaysian DD/MM/YYYY format)
- **Title**: Vendor/store name
- **Total Amount**: Final payment amount (numeric value only)
- **File Name**: Original image filename from Google Drive
- **Source**: Direct Google Drive link to the receipt image
- **Processed Date & Time**: Date and time when the receipt was processed
- **Confidence**: Extraction quality assessment (low/medium/high)

## Architecture

```
Google Drive (Receipt Images)
        ↓
GitHub Actions (Scheduled Workflow)
        ↓
Azure OpenAI (gpt-5.4-nano)
        ↓
Google Sheets (Structured Data)
```

## Prerequisites

- **GitHub Account** with Actions enabled
- **Azure Account** with Azure OpenAI or AI Foundry access
- **Google Account** with:
  - Google Drive API enabled
  - Google Sheets API enabled
  - Service account credentials
- **Python 3.11+**

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

### 3. Configure Repository Settings

Create a `repository_path.json` file with your drive folders and worksheets:

```json
[
  {
    "GOOGLE_SHEET_NAME": "Receipt Analysis",
    "GOOGLE_WORKSHEET_ID": "133169438",
    "GOOGLE_DRIVE_FOLDER_ID": "157SUisvdKbdOxqPY1ByGhbvtpt0sXiGu"
  },
  {
    "GOOGLE_SHEET_NAME": "Receipt Analysis",
    "GOOGLE_WORKSHEET_ID": "402123830",
    "GOOGLE_DRIVE_FOLDER_ID": "1W9gXk4GLmbBUyar3OBJ19Xp4BP0QrfbH"
  }
]
```

### 4. Configure Environment Variables

Create a `local.settings.json` file for local testing:

```json
{
  "IsEncrypted": false,
  "Values": {
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
    "GOOGLE_UNIVERSE_DOMAIN": "googleapis.com"
  }
}
```

### 5. Run Locally

```bash
python main.py
```

## GitHub Actions Setup

### 1. Configure GitHub Secrets

In your GitHub repository, go to **Settings → Secrets and variables → Actions** and add the following secrets:

- `OPEN_AI_KEY`
- `OPEN_AI_ENDPOINT`
- `OPEN_AI_DEPLOYMENT_NAME`
- `GOOGLE_PROJECT_ID`
- `GOOGLE_PRIVATE_KEY_ID`
- `GOOGLE_PRIVATE_KEY` (the entire private key including `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----`)
- `GOOGLE_CLIENT_EMAIL`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_X509_CERT_URL`

### 2. Workflow Configuration

The workflow is defined in [.github/workflows/receipt-ingestion.yml](.github/workflows/receipt-ingestion.yml) and will:

- Run automatically every Saturday at midnight UTC
- Can be triggered manually from the Actions tab
- Install dependencies and run the receipt processing script
- Upload logs on failure for debugging
(e.g., `gid=133169438`)

## Project Structure

```
Receipt-Analysis/
├── main.py                   # Main entry point for receipt processing
├── config.py                 # Configuration loader
├── repository_path.json      # Multiple drive/sheet configurations
├── requirements.txt          # Python dependencies
├── local.settings.json       # Local environment variables (gitignored)
├── helpers/                  # Helper modules
│   ├── __init__.py          # Package initializer
│   ├── g_drive.py           # Google Drive integration
│   ├── g_sheet.py           # Google Sheets integration
│   ├── llm.py               # Azure OpenAI/Pydantic AI agent
│   └── utils.py             # Utility functions
├── .github/
│   └── workflows/
│       └── receipt-ingestion.yml  # GitHub Actions workflow
```

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
- **Worksheet ID**: From the sheet's gid parameter (e.g., `gid=133169438`)


## Configuration

### Schedule

The workflow runs on a CRON schedule defined in [.github/workflows/receipt-ingestion.yml](.github/workflows/receipt-ingestion.yml):

```yaml
schedule:
  - cron: '0 0 * * 6'  # Every Saturday at midnight UTC
```

Modify this to change the execution frequency.

### Concurrency

Adjust concurrent processing in [main.py](main.py):

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

Add or remove formats in [helpers/g_drive.py](helpers/g_drive.py):

```python
SUPPORTED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    # Add more...
}
```

## Monitoring

View logs in:
- **Local**: Terminal output when running `python main.py`
- **GitHub Actions**: Actions tab → Receipt Ingestion workflow → View logs

## Troubleshooting

### 404 Model Not Found
- Verify `OPEN_AI_DEPLOYMENT_NAME` matches your Azure deployment
- Check endpoint URL is correct

### Google API Errors
- Ensure service account has access to Drive folder and Sheet
- Verify `GOOGLE_PRIVATE_KEY` contains `\n` (newlines)

### Rate Limiting
- Decrease concurrency level in [main.py](main.py)
- Add delays between batches
- Check Azure OpenAI quota

## Dependencies

- `openai` - OpenAI client for Azure integration
- `pydantic-ai` - AI agent framework with structured output
- `google-api-python-client` - Google Drive API
- `gspread` - Google Sheets API wrapper
- `oauth2client` - Google authentication
- `python-dotenv` - Environment variable loading

## Author

Nazmi Tarmizi
