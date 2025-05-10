import os

def check_folder(folder_path: str) -> bool:
    if not os.path.exists(folder_path):
        return False
    return True

def find_file(file_path: str) -> bool:
    if os.path.exists(file_path):
        return True
    return False
