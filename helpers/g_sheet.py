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


# # 4. Open the Google Sheet by its title
# # (Note: The service account MUST be shared on this file)
# spreadsheet = client.open("Name of Your Google Sheet")
# worksheet = spreadsheet.sheet1  # Grabs the first tab/worksheet

# # ==========================================
# # --- READ DATA ---
# # ==========================================

# # get_all_records() returns a list of dictionaries. 
# # It intelligently assumes your first row contains your headers.
# data = worksheet.get_all_records()

# # PRO TIP: Immediately pass the data into a Pandas DataFrame for easy analysis
# df = pd.DataFrame(data)
# print("Data from Sheet:")
# print(df.head())

# # ==========================================
# # --- WRITE DATA ---
# # ==========================================

# # Append a single row to the bottom of the data
# new_row = ["Jane Doe", "jane.doe@example.com", "Engineer", 85000]
# worksheet.append_row(new_row)
# print("\nNew row appended successfully!")