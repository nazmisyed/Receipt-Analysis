from helpers.g_drive import get_drive_service, get_list_of_files


if __name__ == "__main__":
    DINE_OUT_FOLDER_ID = "157SUisvdKbdOxqPY1ByGhbvtpt0sXiGu"
    drive = get_drive_service()
    if drive:
        files = get_list_of_files(drive, DINE_OUT_FOLDER_ID)
        print(files)