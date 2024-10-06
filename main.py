# main.py

import sys
import tkinter as tk
from frontend.gui import ZugaCloudGUI
from PIL import Image, ImageTk
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    root = tk.Tk()
    root.title("ZugaCloud - Infinite Video Storage")
    root.geometry('1200x800')
    root.resizable(False, False)  # Fixed window size for consistent UI

    # Set the window and taskbar icon
    icon_path = os.path.join('frontend', 'assets', 'zugacloud_icon.png')  # Updated icon path
    if os.path.exists(icon_path):
        try:
            icon_image = Image.open(icon_path)
            icon_photo = ImageTk.PhotoImage(icon_image)
            root.iconphoto(False, icon_photo)
        except Exception as e:
            logger.error(f"Error setting window icon: {e}")
    else:
        logger.warning(f"Icon file not found at {icon_path}. Using default icon.")

    app = ZugaCloudGUI(root)
    app.run()

if __name__ == "__main__":
    main()
