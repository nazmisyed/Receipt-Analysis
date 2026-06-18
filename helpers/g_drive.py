
import io
from typing import Any
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from config import (GOOGLE_TYPE,
                    GOOGLE_PROJECT_ID,
                    GOOGLE_PRIVATE_KEY_ID,
                    GOOGLE_PRIVATE_KEY,
                    GOOGLE_CLIENT_EMAIL,
                    GOOGLE_CLIENT_ID,
                    GOOGLE_AUTH_URI,
                    GOOGLE_TOKEN_URI,
                    GOOGLE_AUTH_PROVIDER_X509_CERT_URL,
                    GOOGLE_CLIENT_X509_CERT_URL,
                    GOOGLE_UNIVERSE_DOMAIN,
                    logger)


GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPES = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',
"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
SUPPORTED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/bmp",
    "image/tiff",
    "image/heic",
    "image/heif",
}

CREDS_DICT = {
    "type": GOOGLE_TYPE,
    "project_id": GOOGLE_PROJECT_ID,
    "private_key_id": GOOGLE_PRIVATE_KEY_ID,
    "private_key": GOOGLE_PRIVATE_KEY,
    "client_email": GOOGLE_CLIENT_EMAIL,
    "client_id": GOOGLE_CLIENT_ID,
    "auth_uri": GOOGLE_AUTH_URI,
    "token_uri": GOOGLE_TOKEN_URI,
    "auth_provider_x509_cert_url": GOOGLE_AUTH_PROVIDER_X509_CERT_URL,
    "client_x509_cert_url": GOOGLE_CLIENT_X509_CERT_URL,
    "universe_domain": GOOGLE_UNIVERSE_DOMAIN
}

DRIVE_ID = ""

#https://developers.google.com/workspace/drive/api/quickstart/python?authuser=1
# https://googleapis.dev/python/google-auth/latest/reference/google.oauth2.credentials.html
def get_drive_service() -> Any:
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(CREDS_DICT, GOOGLE_SCOPES)
        service = build('drive', 'v3', credentials=creds)
        logger.info("Google Drive service created successfully.")
        return service
    except Exception as e:
        logger.error(f"Error creating Google Drive service: {e}")
        return None
    
def get_list_of_files(service: Any, folder_id: str) -> list:
    try:
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])
        logger.info(f"Retrieved {len(files)} files from folder ID {folder_id}.")
        return files
    except Exception as e:
        logger.error(f"Error retrieving files from Google Drive: {e}")
        return []



def download_file_as_binary(service: Any, file_id: str) -> bytes:
    try:
        request = service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        logger.error(f"Error downloading file ID {file_id} as binary: {e}")
        return b""






