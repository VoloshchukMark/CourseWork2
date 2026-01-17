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
                         collection_name="manufacturers", 
                         title_text="New Supplier Registration", 
                         has_image=False)

    def create_specific_widgets(self):
        self.entry_name = self.create_field("Name:", "entry")
        self.entry_address = self.create_field("Address:", "entry")
        self.entry_number = self.create_field("Phone Number:", "entry")


    def get_data_dict(self):
        name = self.entry_name.get().strip() #type: ignore
        address = self.entry_address.get().strip() #type: ignore
        number = self.entry_number.get().strip() #type: ignore

        if not name or not number:
            from tkinter import messagebox
            messagebox.showwarning("Warning", "Name and Number are required!")
            return None

        return {
            "_id": mongodb_functions.get_next_sequence("manufacturer_id"), # Або просто let MongoDB handle IDs
            "name": name,
            "address": address,
            "number": number,
            "fabric_supply_amount": 0
        }

    def clear_specific_fields(self):
        self.entry_name.delete(0, tk.END) #type: ignore
        self.entry_address.delete(0, tk.END) #type: ignore
        self.entry_number.delete(0, tk.END) #type: ignore
        self.entry_.delete(0, tk.END) #type: ignore

    def fill_specific_fields(self, data):
        self.clear_specific_fields()
        
        self.entry_name.insert(0, data.get("name", "")) #type: ignore
        self.entry_address.insert(0, data.get("address", "")) #type: ignore
        self.entry_number.insert(0, str(data.get("number", ""))) #type: ignore

    def get_manufacturers_with_counts(self):
        pipeline = [
            # 1. З'єднуємо колекцію tailors (виробники) з колекцією fabrics
            {
                "$lookup": {
                    "from": "fabrics",                # Увага: перевірте точну назву вашої колекції тканин у MongoDB!
                    "localField": "_id",              # ID у колекції tailors
                    "foreignField": "fabric_manufacturer_id", # Поле посилання у колекції fabrics
                    "as": "matched_fabrics"           # Тимчасове поле з масивом тканин
                }
            },
            # 2. Формуємо результат, замінюючи масив на його довжину
            {
                "$project": {
                    "name": 1,
                    "address": 1,
                    "number": 1,
                    "fabric_supply_amount": { "$size": "$matched_fabrics" }
                }
            }
        ]
        
        return list(mongodb_connection.suppliers_collection.aggregate(pipeline))