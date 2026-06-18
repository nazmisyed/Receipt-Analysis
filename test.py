from helpers.g_drive import get_drive_service, get_list_of_files
from helpers.g_sheet import get_g_worksheet,append_row_to_worksheet
from config import GOOGLE_DRIVE_FOLDER_ID, GOOGLE_SHEET_NAME, GOOGLE_WORKSHEET_ID,logger


if __name__ == "__main__":
    drive = get_drive_service()
    if drive:
        files = get_list_of_files(drive, GOOGLE_DRIVE_FOLDER_ID)
        print(files)
        ws = get_g_worksheet(GOOGLE_SHEET_NAME, GOOGLE_WORKSHEET_ID)
        if ws:
            success = append_row_to_worksheet(ws, ["Test", "Data", "123","2024-06-01", "https://example.com/receipt.jpg","AI Analysis Result"])
            if success:
                print("Row appended successfully.")
            else:
                print("Failed to append row.")
    