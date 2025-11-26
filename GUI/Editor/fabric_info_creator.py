import tkinter as tk
from tkinter import messagebox
import sys
import os
import io
from PIL import Image, ImageTk
from bson.binary import Binary
from tkinter import messagebox, filedialog

from GUI.Editor.base_info_creator_frame import BaseItemCreatorFrame
from Utils import mongodb_functions

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class FabricInfoCreatorFrame(BaseItemCreatorFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, collection_name="fabrics", title_text="Fabric's parameters")

    def create_specific_widgets(self):
        self.entry_model_name = self.create_field("Fabric Name:", "entry")
        self.text_description = self.create_field("Description:", "text")
        self.entry_fabric_manufacturer_id = self.create_field("Fabric Manufacturer ID:", "entry")
        self.entry_fabric_color = self.create_field("Fabric Color:", "entry")
        self.entry_fabric_texture = self.create_field("Fabric Texture:", "entry")
        self.entry_price_per_meter = self.create_field("Price per Meter:", "entry")
        self.width_in_meters = self.create_field("Width in Meters:", "entry")
        self.check_var_in_stock = self.create_field("In Stock:", "checkbutton")

    def get_data_dict(self):
        # Валідація
        price_per_meter = self.validate_float(self.entry_price_per_meter, "Price per Meter")
        width_in_meters = self.validate_float(self.width_in_meters, "Width in Meters")
        fabric_manufacturer_id = self.validate_float(self.entry_fabric_manufacturer_id, "Fabric Manufacturer ID")
        
        if None in (price_per_meter, width_in_meters, fabric_manufacturer_id):
            return None

        image_binary = self.process_image_for_db()

        return {
            "_id": mongodb_functions.get_next_sequence("model_id"), # Переконайтесь, що тут правильний sequence name
            "fabric_name": self.entry_model_name.get(), # type: ignore
            "description": self.text_description.get("1.0", tk.END).strip(), # type: ignore
            "fabric_color": self.entry_fabric_color.get(), # type: ignore
            "fabric_texture": self.entry_fabric_texture.get(), # type: ignore
            "fabric_manufacturer_id": fabric_manufacturer_id,
            "price_per_meter": price_per_meter,
            "width_in_meters": width_in_meters,
            "in_stock": bool(self.check_var_in_stock.get()), # type: ignore
            "full_price": None,
            "image": image_binary
        }

    def clear_specific_fields(self):
        self.entry_model_name.delete(0, tk.END) # type: ignore
        self.text_description.delete("1.0", tk.END) # type: ignore
        self.entry_fabric_manufacturer_id.delete(0, tk.END) # type: ignore
        self.entry_fabric_color.delete(0, tk.END) # type: ignore
        self.entry_fabric_texture.delete(0, tk.END) # type: ignore
        self.entry_price_per_meter.delete(0, tk.END) # type: ignore
        self.width_in_meters.delete(0, tk.END) # type: ignore
        self.check_var_in_stock.set(0) # type: ignore