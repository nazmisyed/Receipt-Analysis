from typing import Any

import azure.functions as func

from config import (
    GOOGLE_DRIVE_FOLDER_ID,
    GOOGLE_SHEET_NAME,
    GOOGLE_WORKSHEET_ID,
    logger,
)
from helpers.g_drive import (
    SUPPORTED_IMAGE_MIME_TYPES,
    download_file_as_binary,
    get_drive_service,
    get_list_of_files,
)
from helpers.g_sheet import (
    append_row_to_worksheet,
    get_all_records_from_worksheet,
    get_g_worksheet,
)
from helpers.llm import extract_receipt_info

app = func.FunctionApp()


DEFAULT_SHEET_COLUMNS = [
    "Receipt_Date_Time",
    "Title",
    "Total_Amount",
    "File_Name",
    "Processed_Date_Time",
    "Confidence",
]


def _normalized_filename(value: Any) -> str:
    return str(value or "").strip().lower()


def _existing_file_names(sheet_records: list[dict[str, Any]]) -> set[str]:
    existing_names = set()
    candidate_columns = ("File_Name", "file_name", "File Name", "filename", "name")
    for record in sheet_records:
        for column in candidate_columns:
            if column in record and record.get(column):
                existing_names.add(_normalized_filename(record.get(column)))
                break
    return existing_names


def _sheet_row_from_result(worksheet: Any, llm_result: dict[str, Any]) -> list[str]:
    headers = worksheet.row_values(1) if worksheet else []
    columns = headers if headers else DEFAULT_SHEET_COLUMNS
    return [str(llm_result.get(column, "")) for column in columns]


async def _run_receipt_ingestion() -> int:
    drive_service = get_drive_service()
    if not drive_service:
        logger.error("Drive service is unavailable. Skipping run.")
        return 0

    worksheet = get_g_worksheet(GOOGLE_SHEET_NAME, GOOGLE_WORKSHEET_ID)
    if not worksheet:
        logger.error("Worksheet is unavailable. Skipping run.")
        return 0

    drive_files = get_list_of_files(drive_service, GOOGLE_DRIVE_FOLDER_ID)
    sheet_records = get_all_records_from_worksheet(worksheet)
    existing_names = _existing_file_names(sheet_records)
    logger.info("Found %s files in Drive and %s existing sheet records.", len(drive_files), len(sheet_records))

    processed_count = 0

    for file_item in drive_files:
        file_id = file_item.get("id")
        file_name = file_item.get("name", "")
        mime_type = file_item.get("mimeType", "")
        normalized_name = _normalized_filename(file_name)

        if not file_id or not file_name:
            logger.warning("Skipping invalid file item: %s", file_item)
            continue

        if normalized_name in existing_names:
            logger.info("Skipping existing file in sheet: %s", file_name)
            continue

        if mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
            logger.info("Skipping unsupported mime type for file %s: %s", file_name, mime_type)
            continue

        file_bytes = download_file_as_binary(drive_service, file_id)
        if not file_bytes:
            logger.warning("Skipping file due to empty binary download: %s", file_name)
            continue

        llm_result = await extract_receipt_info(file_bytes, media_type=mime_type)
        llm_result = dict(llm_result)
        llm_result["File_Name"] = file_name

        row_data = _sheet_row_from_result(worksheet, llm_result)
        appended = append_row_to_worksheet(worksheet, row_data)
        if appended:
            existing_names.add(normalized_name)
            processed_count += 1
            logger.info("Processed and appended file: %s", file_name)
        else:
            logger.error("Failed to append row for file: %s", file_name)

    return processed_count


@app.timer_trigger(
    schedule="0 * * * * 6",
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False,
)
async def receipt_ingestion(myTimer: func.TimerRequest) -> None:
    try:
        if myTimer.past_due:
            logger.warning("Timer is running late.")

        logger.info("Receipt ingestion run started.")
        processed_count = await _run_receipt_ingestion()
        logger.info("Receipt ingestion run completed. New receipts processed: %s", processed_count)
    except Exception:
        logger.exception("Receipt ingestion run failed.")
        raise

