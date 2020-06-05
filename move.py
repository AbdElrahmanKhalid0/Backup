import time
import shutil
import os
import stat
from watch_files import watch

_folderignore = ['node_modules']

PROJECTS_PATH = r'SOURCE'
BACKUP_PATH = r'DISTINATION'

def on_rm_error( func, path, exc_info):
    # path contains the path of the file that couldn't be removed so it will make it writable and change
    # its read-only state and remove it
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )

if os.path.isdir(BACKUP_PATH):
    shutil.rmtree(BACKUP_PATH, onerror = on_rm_error )

os.mkdir(BACKUP_PATH)

os.chdir(PROJECTS_PATH)

folders = [folder for folder in os.listdir() if os.path.isdir(rf'{PROJECTS_PATH}\{folder}')]
files = [folder for folder in os.listdir() if os.path.isfile(rf'{PROJECTS_PATH}\{folder}')]

# moving all the files
for file in files:
    shutil.copy(file, BACKUP_PATH)
    
# moving all the folders
for folder in folders:
    # this gets the subfolders of a specific folder with the walk method => it gets all the descendant
    # files or folders and returns them like this (PATH,FOLDERS_LIST,FILES_LIST) so the first one is
    # the direct childrens of this folder
    folder_subfolders = list(os.walk(rf'{PROJECTS_PATH}\{folder}'))[0][1]
    

    # checking if the folder has any of the _folderignore folders in it so they don't get copied
    # and that is by getting the intersection or the common values between the two lists
    if [folder for folder in _folderignore if folder in folder_subfolders]:
        os.chdir(rf'{PROJECTS_PATH}\{folder}')
        if not os.path.isdir(rf'{BACKUP_PATH}\{folder}'):
            os.mkdir(rf'{BACKUP_PATH}\{folder}')

        # first, coping the files
        folder_files = list(os.walk(rf'{PROJECTS_PATH}\{folder}'))[0][2]
        for file in folder_files:
            shutil.copy(file, rf'{BACKUP_PATH}\{folder}')

        # second, coping the folders that aren't of the _folderignore
        for subfolder in folder_subfolders:
            if subfolder not in _folderignore:
                shutil.copytree(rf'{PROJECTS_PATH}\{folder}\{subfolder}',rf'{BACKUP_PATH}\{folder}\{subfolder}')
                    
    # if it doesn't have any of them it will copy the whole file
    else:
        shutil.copytree(rf'{PROJECTS_PATH}\{folder}',rf'{BACKUP_PATH}\{folder}')


def delete_file(file_path):
    os.remove(file_path)

def copy_file(file_path, final_path):
    shutil.copy(file_path, final_path)

def update_file(file_path, final_path):
    delete_file(final_path)
    copy_file(file_path, final_path)

def rename_item(file_path, final_path):
    os.rename(final_path, file_path)

def remove_folder(folder_path):
    shutil.rmtree(folder_path, onerror = on_rm_error )

def copy_folder(folder_path, final_path):
    if os.path.isdir(final_path):
        remove_folder(final_path)
    shutil.copytree(folder_path, final_path)

# watching the files for changes
print('Watching Files For Changes...')
while True:
    changed_files = watch(PROJECTS_PATH)
    for file, changeMethod in changed_files:
        FILE_BACKUP_PATH = file.replace(PROJECTS_PATH, BACKUP_PATH)

        # in here I check the FILE_BACKUP_PATH and the file because the file may be deleted or created
        # so it will be false in every situation if it wasn't like this
        print(f"'{file}' {'Renamed To' if changeMethod == 'Renamed from something' else '' if changeMethod == 'Renamed to something' else changeMethod}")
        if os.path.isdir(FILE_BACKUP_PATH) or os.path.isdir(file):
            if changeMethod == "Created":
                copy_folder(file, FILE_BACKUP_PATH)
            elif changeMethod == "Deleted":
                remove_folder(FILE_BACKUP_PATH)
            elif changeMethod == "Renamed from something":
                rename_item(changed_files[1][0].replace(PROJECTS_PATH, BACKUP_PATH), FILE_BACKUP_PATH)

        elif os.path.isfile(FILE_BACKUP_PATH) or os.path.isfile(file):
            if changeMethod == "Created":
                copy_file(file, FILE_BACKUP_PATH)
            elif changeMethod == "Deleted":
                delete_file(FILE_BACKUP_PATH)
            elif changeMethod == "Updated":
                update_file(file, FILE_BACKUP_PATH)
            elif changeMethod == "Renamed from something":
                rename_item(changed_files[1][0].replace(PROJECTS_PATH, BACKUP_PATH), FILE_BACKUP_PATH)
        
    time.sleep(.5)
