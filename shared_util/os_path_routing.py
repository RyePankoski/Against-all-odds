import sys
import os


def get_asset_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Running in normal Python environment (like PyCharm)
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.join(base_path, "..")

    return os.path.join(base_path, relative_path)