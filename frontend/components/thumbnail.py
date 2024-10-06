# frontend/components/thumbnail.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import logging

logger = logging.getLogger(__name__)

class ThumbnailFrame(ttk.Frame):
    def __init__(self, parent, file_name, file_type, image, on_click, on_hover=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.file_name = file_name
        self.file_type = file_type
        self.on_click = on_click
        self.on_hover = on_hover
        self.preview_window = None

        # Thumbnail Image
        self.thumbnail_label = ttk.Label(self, image=image)
        self.thumbnail_label.image = image  # Keep a reference
        self.thumbnail_label.pack()

        # File Name Label
        self.name_label = ttk.Label(self, text=file_name, wraplength=150)
        self.name_label.pack()

        # Bind click events
        self.bind_events()

    def bind_events(self):
        self.thumbnail_label.bind("<Button-1>", self.handle_click)
        self.name_label.bind("<Button-1>", self.handle_click)
        # Removed hover bindings as per requirement

    def handle_click(self, event):
        self.on_click(self.file_name, self.file_type)
