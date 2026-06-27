"""
Main entry point for receipt ingestion workflow.
Runs as a standalone script for GitHub Actions.
"""
import asyncio
from typing import Any

from config import REPOSITORY_CONFIGS, logger
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


DEFAULT_SHEET_COLUMNS = [
    "Receipt_Date_Time",
    "Title",
    "Total_Amount",
    "File_Name",
    "Source",
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


async def _process_single_file(
    drive_service: Any,
    worksheet: Any,
    file_item: dict[str, Any],
    existing_names: set[str],
    semaphore: asyncio.Semaphore,
) -> tuple[bool, str]:
    """Process a single file and return (success, filename)."""
    file_id = file_item.get("id")
    file_name = file_item.get("name", "")
    mime_type = file_item.get("mimeType", "")
    normalized_name = _normalized_filename(file_name)

    if not file_id or not file_name:
        logger.warning("Skipping invalid file item: %s", file_item)
        return False, file_name

    if normalized_name in existing_names:
        logger.info("Skipping existing file in sheet: %s", file_name)
        return False, file_name

    if mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
        logger.info("Skipping unsupported mime type for file %s: %s", file_name, mime_type)
        return False, file_name

    file_bytes = download_file_as_binary(drive_service, file_id)
    if not file_bytes:
        logger.warning("Skipping file due to empty binary download: %s", file_name)
        return False, file_name

    try:
        async with semaphore:  # Limit concurrent LLM calls
            llm_result = await extract_receipt_info(file_bytes, media_type=mime_type)
        
        llm_result = dict(llm_result)
        llm_result["File_Name"] = file_name
        llm_result["Source"] = f"https://drive.google.com/file/d/{file_id}/view"

        row_data = _sheet_row_from_result(worksheet, llm_result)
        appended = append_row_to_worksheet(worksheet, row_data)
        
        if appended:
            existing_names.add(normalized_name)
            logger.info("Processed and appended file: %s", file_name)
            return True, file_name
        else:
            logger.error("Failed to append row for file: %s", file_name)
            return False, file_name
    except Exception as e:
        logger.error("Error processing file %s: %s", file_name, e)
        return False, file_name


async def _process_single_repository(
    drive_service: Any,
    config: dict[str, Any],
    config_index: int,
) -> int:
    """Process a single repository configuration."""
    sheet_name = config.get("GOOGLE_SHEET_NAME")
    worksheet_id = config.get("GOOGLE_WORKSHEET_ID")
    folder_id = config.get("GOOGLE_DRIVE_FOLDER_ID")
    
    if not all([sheet_name, worksheet_id, folder_id]):
        logger.error("Config #%d: Missing required fields. Skipping.", config_index)
        return 0
    
    logger.info(
        "Config #%d: Processing folder_id=%s, sheet=%s, worksheet_id=%s",
        config_index, folder_id, sheet_name, worksheet_id
    )
    
    worksheet = get_g_worksheet(sheet_name, worksheet_id)
    if not worksheet:
        logger.error("Config #%d: Worksheet is unavailable. Skipping.", config_index)
        return 0

    drive_files = get_list_of_files(drive_service, folder_id)
    sheet_records = get_all_records_from_worksheet(worksheet)
    existing_names = _existing_file_names(sheet_records)
    logger.info(
        "Config #%d: Found %s files in Drive and %s existing sheet records.",
        config_index, len(drive_files), len(sheet_records)
    )

    # Process up to 5 files concurrently (adjust based on rate limits)
    semaphore = asyncio.Semaphore(5)
    
    # Create tasks for all files
    tasks = [
        _process_single_file(drive_service, worksheet, file_item, existing_names, semaphore)
        for file_item in drive_files
    ]
    
    # Process all files concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Count successful processes
    processed_count = sum(1 for result in results if isinstance(result, tuple) and result[0])
    logger.info("Config #%d: Processed %d new receipts.", config_index, processed_count)
    
    return processed_count


async def run_receipt_ingestion() -> int:
    """Process all repository configurations."""
    if not REPOSITORY_CONFIGS:
        logger.error("No repository configurations found. Skipping run.")
        return 0
    
    drive_service = get_drive_service()
    if not drive_service:
        logger.error("Drive service is unavailable. Skipping run.")
        return 0

    logger.info("Processing %d repository configuration(s).", len(REPOSITORY_CONFIGS))
    
    total_processed = 0
    for idx, config in enumerate(REPOSITORY_CONFIGS, start=1):
        try:
            count = await _process_single_repository(drive_service, config, idx)
            total_processed += count
        except Exception as e:
            logger.error("Config #%d: Failed to process: %s", idx, e)
            continue
    
    return total_processed


async def main():
    """Main entry point."""
    try:
        logger.info("Receipt ingestion run started.")
        processed_count = await run_receipt_ingestion()
        logger.info("Receipt ingestion run completed. New receipts processed: %s", processed_count)
        return processed_count
    except Exception:
        logger.exception("Receipt ingestion run failed.")
        raise


if __name__ == "__main__":
    asyncio.run(main())
