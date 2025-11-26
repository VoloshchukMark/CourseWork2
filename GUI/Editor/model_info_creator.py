import tkinter as tk
import os, sys
from GUI.Editor.base_info_creator_frame import BaseItemCreatorFrame 
from Utils import mongodb_functions

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class ModelInfoCreatorFrame(BaseItemCreatorFrame):
    def __init__(self, parent, controller):
        # Ініціалізуємо базовий клас з назвою колекції та заголовком
        super().__init__(parent, controller, collection_name="models", title_text="Model's parameters")

    def create_specific_widgets(self):
        # Тут створюємо ТІЛЬКИ поля, специфічні для моделі
        self.entry_model_name = self.create_field("Model Name:", "entry")
        self.text_description = self.create_field("Description:", "text")
        self.text_entry_recomended_fabric = self.create_field("Recommended Fabric:", "text")
        self.text_recomended_accessories = self.create_field("Recommended Accessories:", "text")
        self.entry_model_price = self.create_field("Price:", "entry")
        self.check_var_in_stock = self.create_field("In Stock:", "checkbutton")

    def get_data_dict(self):
        # Використовуємо спільний метод валідації
        price = self.validate_float(self.entry_model_price, "Price")
        if price is None: return None # Валідація не пройшла

        # Використовуємо спільний метод обробки фото
        image_binary = self.process_image_for_db()

        return {
            "_id": mongodb_functions.get_next_sequence("model_id"),
            "model_name": self.entry_model_name.get(), # type: ignore
            "description": self.text_description.get("1.0", tk.END).strip(), # type: ignore
            "recommended_fabric": self.text_entry_recomended_fabric.get("1.0", tk.END).strip(), # type: ignore
            "recommended_accessories": self.text_recomended_accessories.get("1.0", tk.END).strip(), # type: ignore
            "price": price,
            "in_stock": bool(self.check_var_in_stock.get()), # type: ignore
            "image": image_binary
        }

    def clear_specific_fields(self):
        self.entry_model_name.delete(0, tk.END) # type: ignore
        self.text_description.delete("1.0", tk.END) # type: ignore
        self.text_entry_recomended_fabric.delete("1.0", tk.END) # type: ignore
        self.text_recomended_accessories.delete("1.0", tk.END) # type: ignore
        self.entry_model_price.delete(0, tk.END) # type: ignore
        self.check_var_in_stock.set(0) # type: ignore