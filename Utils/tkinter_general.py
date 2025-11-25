import sys
import os
from bson.binary import Binary
from PIL import Image, ImageTk

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 3)
    
    window.geometry(f"{width}x{height}+{x}+{y}")