import tkinter as tk
from GUI.Editor.base_info_creator_frame import BaseItemCreatorFrame
from Utils import mongodb_functions

class TailorInfoCreatorFrame(BaseItemCreatorFrame):
    def __init__(self, parent, controller):
        # Вказуємо has_image=False
        super().__init__(parent, controller, 
                         collection_name="tailors", 
                         title_text="New Tailor Registration", 
                         has_image=False)

    def create_specific_widgets(self):
        self.entry_name = self.create_field("Full Name:", "entry")
        self.entry_number = self.create_field("Phone Number:", "entry")
        
        # Можна додати ще поля, якщо треба (наприклад, спеціалізація)
        # self.entry_specialty = self.create_field("Specialty:", "entry")

    def get_data_dict(self):
        name = self.entry_name.get().strip() #type: ignore
        number = self.entry_number.get().strip() #type: ignore

        if not name or not number:
            from tkinter import messagebox
            messagebox.showwarning("Warning", "Name and Number are required!")
            return None

        return {
            "_id": mongodb_functions.get_next_sequence("tailor_id"),
            "name": name,
            "number": number
        }

    def clear_specific_fields(self):
        self.entry_name.delete(0, tk.END) #type: ignore
        self.entry_number.delete(0, tk.END) #type: ignore