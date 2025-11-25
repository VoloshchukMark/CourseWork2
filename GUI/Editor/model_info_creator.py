import tkinter as tk
from tkinter import messagebox
import sys
import os
import io
from PIL import Image, ImageTk
from bson.binary import Binary
from tkinter import messagebox, filedialog
from Utils import mongodb_functions

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class ModelInfoCreatorFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller

        self.current_file_path = None

        self.create_widgets()
        

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1) 

        picture_Frame = tk.Frame(self, bg="#ffffff")
        picture_Frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

        self.btn_select = tk.Button(picture_Frame, text="📂 Choose the file", command=self.select_file, height=2)
        self.btn_select.pack(pady=10)

        self.lbl_path_text = tk.Label(picture_Frame, text="File is not selected", fg="blue")
        self.lbl_path_text.pack()

        self.lbl_preview = tk.Label(picture_Frame, text="Place for a preview", bg="#ddd", padx=5, pady=5)
        self.lbl_preview.pack()
        
        
        self.fields_Frame = tk.Frame(self, bg="#ffffff")
        self.fields_Frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)

        tk.Label(self.fields_Frame, text="Model's parameters", font=("Arial", 16), 
                bg="#FFFFFF", fg="black").pack(side=tk.TOP, padx=20, pady=5)
        self.entry_model_name = self.create_field(self.fields_Frame, "Model Name:", "entry")
        self.text_description = self.create_field(self.fields_Frame, "Description:", "text")
        self.text_entry_recomended_fabric = self.create_field(self.fields_Frame, "Recommended Fabric:", "text")
        self.text_recomended_accessories = self.create_field(self.fields_Frame, "Recommended Accessories:", "text")
        self.entry_model_price = self.create_field(self.fields_Frame, "Price:", "entry")
        self.check_var_in_stock = self.create_field(self.fields_Frame, "In Stock:", "checkbutton")

        self.enter_Button = tk.Button(self.fields_Frame, text="Enter Model Info", height=2, command=self.handle_enter)
        self.enter_Button.pack(pady=20)



    def select_file(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Select your picture",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            self.current_file_path = file_path
            self.lbl_path_text.config(text=f"Selected: {os.path.basename(file_path)}")
            
            self.show_preview(self.lbl_preview, file_path)
    
    def show_preview(self, widget, path):
        try:
            img = Image.open(path)
            img.thumbnail((200, 200))
            
            tk_img = ImageTk.PhotoImage(img, master=self)
            widget.config(image=tk_img, text="")

            widget.image = tk_img
            
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити картинку: {e}")

    def create_field(self, parent, label_text, widget_type):
        frame = tk.Frame(parent, bg="#ffffff")
        frame.pack(pady=10, fill=tk.X)

        label = tk.Label(frame, text=label_text, bg="#ffffff", anchor="w")
        label.pack(side=tk.LEFT, padx=5)

        if widget_type == "entry":
            entry = tk.Entry(frame, width=10)
            entry.pack(side=tk.RIGHT, padx=5, fill="x", expand=True)
            return entry
        elif widget_type == "text":
            text = tk.Text(frame, height=4, width=10)
            text.pack(side=tk.RIGHT, padx=5, fill="x", expand=True)
            return text
        elif widget_type == "checkbutton":
            var = tk.IntVar()
            checkbox = tk.Checkbutton(frame, variable=var, bg="#ffffff")
            checkbox.pack(side=tk.RIGHT, padx=5)
            return var
    
    def get_model_info(self):
        try:
            # Якщо поле пусте, ставимо 0, або видаємо помилку (за вашим вибором)
            price_val = self.entry_model_price.get() # type: ignore
            price = float(price_val) if price_val else 0.0
        except ValueError:
            messagebox.showerror("Помилка", "Ціна повинна бути числом (наприклад: 1200 або 1200.50)")
            return None
        
        image_binary = None

        if self.current_file_path and os.path.exists(self.current_file_path):
            try:
                # Відкриваємо оригінал
                img = Image.open(self.current_file_path)
                
                # Змінюємо розмір (пропорційно вписуємо в квадрат 800x800 пікселів)
                # Це значно зменшує вагу файлу для бази даних
                img.thumbnail((800, 800))

                # Якщо картинка має прозорість (PNG) або палітру, 
                # конвертуємо в RGB, щоб можна було зберегти як JPEG
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Створюємо буфер у пам'яті (віртуальний файл)
                output_buffer = io.BytesIO()
                
                # Зберігаємо зменшену картинку в буфер у форматі JPEG (оптимально для фото)
                img.save(output_buffer, format='JPEG', quality=20)
                
                # Отримуємо байти з буфера та конвертуємо в BSON Binary
                image_data = output_buffer.getvalue()
                image_binary = Binary(image_data)

            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося обробити файл зображення: {e}")
                return None
        else:
            # Якщо фото не обрано, можна вивести попередження або просто продовжити без фото
            print("Фото не обрано")

        doc = {
            "_id": mongodb_functions.get_next_sequence("model_id"),
            "model_name": self.entry_model_name.get(), # type: ignore
            "description": self.text_description.get("1.0", tk.END).strip(), # type: ignore
            "recommended_fabric": self.text_entry_recomended_fabric.get("1.0", tk.END).strip(), # type: ignore
            "recommended_accessories": self.text_recomended_accessories.get("1.0", tk.END).strip(), # type: ignore
            "price": price, # type: ignore
            "in_stock": bool(self.check_var_in_stock.get()), # type: ignore
            "image": image_binary
        }
        return doc
    
    def handle_enter(self):
        model_info = self.get_model_info()
        mongodb_functions.upload_to_db("models", model_info)
        self.clear_fields()
    
    def clear_fields(self):
        self.entry_model_name.delete(0, tk.END) # type: ignore
        self.text_description.delete("1.0", tk.END) # type: ignore
        self.text_entry_recomended_fabric.delete("1.0", tk.END) # type: ignore
        self.text_recomended_accessories.delete("1.0", tk.END) # type: ignore
        self.entry_model_price.delete(0, tk.END) # type: ignore
        self.check_var_in_stock.set(0) # type: ignore
        self.lbl_path_text.config(text="File is not selected")
        self.lbl_preview.config(image="", text="Place for a preview")
        self.current_file_path = None