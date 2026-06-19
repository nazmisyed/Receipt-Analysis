from typing import Any
from helpers.g_drive import get_creds
import gspread
from config import logger




def get_g_worksheet(sheet_id: str, worksheet_id: str) -> Any:
    try:
        creds = get_creds()
        if not creds:
            return None
        client = gspread.authorize(creds)
        sheet = client.open(sheet_id)
        worksheet = sheet.get_worksheet_by_id(worksheet_id)
        logger.info(f"Google Sheet with ID {sheet_id} and Worksheet ID {worksheet_id} opened successfully.")
        return worksheet
    except Exception as e:
        logger.error(f"Error opening Google Sheet with ID {sheet_id} and Worksheet ID {worksheet_id}: {e}")
        return None

def append_row_to_worksheet(worksheet: Any, row_data: list) -> bool:
    try:
        worksheet.append_row(row_data)
        logger.info(f"Row appended successfully to the worksheet.")
        return True
    except Exception as e:
        logger.error(f"Error appending row to the worksheet: {e}")
        return False

def get_all_records_from_worksheet(worksheet: Any) -> list:
    try:
        records = worksheet.get_all_records()
        logger.info(f"Retrieved {len(records)} records from the worksheet.")
        return records
    except Exception as e:
        logger.error(f"Error retrieving records from the worksheet: {e}")
        return []
