import os

def open_albion(game_path: str):
    os.startfile(os.path.join(game_path, "game", "Albion-Online_BE.exe"))

def close_albion():
    os.system("taskkill /f /im Albion-Online.exe")