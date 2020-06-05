# source http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
import os

import win32file
import win32con


def watch(path_to_watch):
    ACTIONS = {
        1: "Created",
        2: "Deleted",
        3: "Updated",
        4: "Renamed from something",
        5: "Renamed to something"
    }

    FILE_LIST_DIRECTORY = 0x0001

    hDir = win32file.CreateFile(
        path_to_watch,
        FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    results = win32file.ReadDirectoryChangesW(
        hDir,
        1024,
        True,
        win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
        win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
        win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
        win32con.FILE_NOTIFY_CHANGE_SIZE |
        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
        win32con.FILE_NOTIFY_CHANGE_SECURITY,
        None,
        None
    )

    returned_value = []

    for action, file in results:
        full_filename = os.path.join(path_to_watch, file)
        returned_value.append((full_filename, ACTIONS.get(action, "Unknown")))

    return returned_value
