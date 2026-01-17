import os, sys
import tkinter as tk
from GUI.Editor.base_info_creator_frame import BaseItemCreatorFrame
from Utils import mongodb_functions
from Utils import mongodb_connection

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class SupplierInfoCreatorFrame(BaseItemCreatorFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, 
                         collection_name="suppliers",  # [ВАЖЛИВО] Пишемо в колекцію "suppliers"
                         title_text="New Supplier Registration", 
                         has_image=False)

    def create_specific_widgets(self):
        self.entry_name = self.create_field("Name:", "entry")
        self.entry_address = self.create_field("Address:", "entry")
        self.entry_number = self.create_field("Phone Number:", "entry")

    def get_data_dict(self):
        # Отримуємо дані з полів
        name = self.entry_name.get().strip() #type: ignore
        address = self.entry_address.get().strip() #type: ignore
        number = self.entry_number.get().strip() #type: ignore

        # Валідація
        if not name or not number:
            from tkinter import messagebox
            messagebox.showwarning("Warning", "Name and Number are required!")
            return None

        # Формуємо документ для БД
        return {
            # Генеруємо унікальний ID для "supplier_id"
            "_id": mongodb_functions.get_next_sequence("supplier_id"), 
            "name": name,
            "address": address,
            "number": number,
            "fabric_supply_amount": 0 # Початкове значення
        }

    def clear_specific_fields(self):
        # [ВИПРАВЛЕНО] Очищаємо тільки існуючі поля
        self.entry_name.delete(0, tk.END) #type: ignore
        self.entry_address.delete(0, tk.END) #type: ignore
        self.entry_number.delete(0, tk.END) #type: ignore

    def fill_specific_fields(self, data):
        self.clear_specific_fields()
        
        self.entry_name.insert(0, data.get("name", "")) #type: ignore
        self.entry_address.insert(0, data.get("address", "")) #type: ignore
        self.entry_number.insert(0, str(data.get("number", ""))) #type: ignore