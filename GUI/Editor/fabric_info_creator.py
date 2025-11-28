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
        super().__init__(parent, controller, collection_name="fabrics", title_text="Fabric's parameters", has_image=True)

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
        try:
            raw_id = self.entry_fabric_manufacturer_id.get().strip() # type: ignore
            if not raw_id:
                raise ValueError("Empty ID")
            fabric_manufacturer_id = int(raw_id) # <--- Конвертуємо в int
        except ValueError:
            messagebox.showerror("Error", "Fabric Manufacturer ID must be an integer number!")
            return None
        
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
    
    def handle_enter(self):
        """
        Цей метод спрацьовує при натисканні кнопки 'Enter Info'.
        Ми перевизначаємо його, щоб додати логіку оновлення лічильника виробника.
        """
        data = self.get_data_dict()
        if data:
            # 1. Спробуємо зберегти тканину в БД
            if mongodb_functions.upload_to_db(self.collection_name, data):
                
                # 2. ЯКЩО УСПІШНО -> Оновлюємо лічильник у виробника
                man_id = data["fabric_manufacturer_id"]
                mongodb_functions.increment_manufacturer_fabric_count(man_id)
                
                # 3. Очищаємо поля (стандартна логіка)
                self.clear_specific_fields()
                if self.has_image:
                    self.current_file_path = None
                    self.lbl_path_text.config(text="File is not selected")
                    self.lbl_preview.config(image="", text="Place for a preview")

    def clear_specific_fields(self):
        self.entry_model_name.delete(0, tk.END) # type: ignore
        self.text_description.delete("1.0", tk.END) # type: ignore
        self.entry_fabric_manufacturer_id.delete(0, tk.END) # type: ignore
        self.entry_fabric_color.delete(0, tk.END) # type: ignore
        self.entry_fabric_texture.delete(0, tk.END) # type: ignore
        self.entry_price_per_meter.delete(0, tk.END) # type: ignore
        self.width_in_meters.delete(0, tk.END) # type: ignore
        self.check_var_in_stock.set(0) # type: ignore

    def fill_specific_fields(self, data):
        self.clear_specific_fields()
        self.entry_model_name.insert(0, data.get("fabric_name", "")) # type: ignore
        self.text_description.insert("1.0", data.get("description", "")) # type: ignore
        self.entry_fabric_manufacturer_id.insert(0, str(data.get("fabric_manufacturer_id", ""))) # type: ignore
        self.entry_fabric_color.insert(0, data.get("fabric_color", "")) # type: ignore
        self.entry_fabric_texture.insert(0, data.get("fabric_texture", "")) # type: ignore
        self.entry_price_per_meter.insert(0, str(data.get("price_per_meter", 0.0))) # type: ignore
        self.width_in_meters.insert(0, str(data.get("width_in_meters", 0.0)))# type: ignore

        if data.get("in_stock"):
            self.check_var_in_stock.set(1)# type: ignore