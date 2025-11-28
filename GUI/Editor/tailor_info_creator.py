import os, sys
import tkinter as tk
from GUI.Editor.base_info_creator_frame import BaseItemCreatorFrame
from Utils import mongodb_functions

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

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
        self.entry_annual_salary = self.create_field("Annual Salary:", "entry")
        self.entry_monthy_salary = self.create_field("Monthy Salary:", "entry")
        self.entry_quarterly_salary = self.create_field("Quarterly Salary:", "entry")
        
        # Можна додати ще поля, якщо треба (наприклад, спеціалізація)
        # self.entry_specialty = self.create_field("Specialty:", "entry")

    def get_data_dict(self):
        name = self.entry_name.get().strip() #type: ignore
        number = self.entry_number.get().strip() #type: ignore
        annual_salary = self.entry_annual_salary.get().strip() #type: ignore
        monthy_salary = self.entry_monthy_salary.get().strip() #type: ignore
        quarterly_salary = self.entry_quarterly_salary.get().strip() #type: ignore

        if not name or not number:
            from tkinter import messagebox
            messagebox.showwarning("Warning", "Name and Number are required!")
            return None

        return {
            "_id": mongodb_functions.get_next_sequence("tailor_id"),
            "name": name,
            "number": number,
            "annual_salary": annual_salary,
            "monthy_salary": monthy_salary,
            "quarterly_salary": quarterly_salary
        }

    def clear_specific_fields(self):
        self.entry_name.delete(0, tk.END) #type: ignore
        self.entry_number.delete(0, tk.END) #type: ignore
        self.entry_annual_salary.delete(0, tk.END) #type: ignore
        self.entry_monthy_salary.delete(0, tk.END) #type: ignore
        self.entry_quarterly_salary.delete(0, tk.END) #type: ignore

    def fill_specific_fields(self, data):
        self.clear_specific_fields()
        
        self.entry_name.insert(0, data.get("name", "")) #type: ignore
        self.entry_number.insert(0, str(data.get("number", ""))) #type: ignore
        self.entry_annual_salary.insert(0, data.get("annual_salary", "")) #type: ignore
        self.entry_monthy_salary.insert(0, data.get("monthy_salary", "")) #type: ignore
        self.entry_quarterly_salary.insert(0, data.get("quarterly_salary", "")) #type: ignore
        