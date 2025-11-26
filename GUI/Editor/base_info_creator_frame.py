import tkinter as tk
from tkinter import messagebox, filedialog
import io, os, sys
from PIL import Image, ImageTk
from bson.binary import Binary
from Utils import mongodb_functions

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class BaseItemCreatorFrame(tk.Frame):
    def __init__(self, parent, controller, collection_name, title_text, has_image=True):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller
        self.collection_name = collection_name # "models" або "fabrics"
        self.title_text = title_text
        self.has_image = has_image
        
        self.current_file_path = None
        self.setup_ui_structure()

    def setup_ui_structure(self):
        """Створює базовий каркас"""
        self.grid_rowconfigure(0, weight=1) 

        # Логіка відображення залежно від наявності картинки
        if self.has_image:
            self.grid_columnconfigure(0, weight=2) # Для фото
            self.grid_columnconfigure(1, weight=3) # Для полів

            # --- Ліва частина (Зображення) ---
            picture_Frame = tk.Frame(self, bg="#ffffff")
            picture_Frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

            self.btn_select = tk.Button(picture_Frame, text="📂 Choose the file", command=self.select_file, height=2)
            self.btn_select.pack(pady=10)

            self.lbl_path_text = tk.Label(picture_Frame, text="File is not selected", fg="blue", bg="#ffffff")
            self.lbl_path_text.pack()

            self.lbl_preview = tk.Label(picture_Frame, text="Place for a preview", bg="#ddd", padx=5, pady=5)
            self.lbl_preview.pack()

            # Поля будуть у другій колонці
            fields_col = 1
            fields_sticky = "nsew"
            fields_colspan = 1
        else:
            # Якщо картинки немає, поля займають все місце по центру
            self.grid_columnconfigure(0, weight=1)
            fields_col = 0
            fields_sticky = "n" # Притискаємо до верху (center-top)
            fields_colspan = 2  # Займаємо всю ширину

        # --- Права частина (Поля) ---
        self.fields_Frame = tk.Frame(self, bg="#ffffff")
        self.fields_Frame.grid(row=0, column=fields_col, columnspan=fields_colspan, sticky=fields_sticky, padx=20, pady=20)

        tk.Label(self.fields_Frame, text=self.title_text, font=("Arial", 16, "bold"), 
                bg="#FFFFFF", fg="black").pack(side=tk.TOP, padx=20, pady=10)

        self.create_specific_widgets()

        self.enter_Button = tk.Button(self.fields_Frame, text="Enter Info", height=2, 
                                      bg="#e0e0e0", command=self.handle_enter)
        self.enter_Button.pack(pady=30, fill=tk.X, padx=20)
    def create_specific_widgets(self):
        """Цей метод має бути перевизначений у дочірніх класах"""
        pass

    def create_field(self, label_text, widget_type):
        """Універсальний метод створення поля"""
        frame = tk.Frame(self.fields_Frame, bg="#ffffff")
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

    def select_file(self):
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Select your picture",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            self.current_file_path = file_path
            self.lbl_path_text.config(text=f"Selected: {os.path.basename(file_path)}")
            self.show_preview(file_path)

    def show_preview(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((200, 200))
            tk_img = ImageTk.PhotoImage(img, master=self)
            self.lbl_preview.config(image=tk_img, text="")
            self.lbl_preview.image = tk_img #type: ignore
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося відкрити картинку: {e}")

    def process_image_for_db(self):
        """Обробляє поточне зображення для збереження в БД. Повертає Binary або None."""
        if self.current_file_path and os.path.exists(self.current_file_path):
            try:
                img = Image.open(self.current_file_path)
                img.thumbnail((800, 800))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                output_buffer = io.BytesIO()
                img.save(output_buffer, format='JPEG', quality=20)
                return Binary(output_buffer.getvalue())
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося обробити файл зображення: {e}")
                return None
        return None

    def validate_float(self, entry_widget, field_name):
        """Валідація числових полів (спільна для ціни, ширини тощо)"""
        try:
            raw_value = entry_widget.get()
            value = float(raw_value) if raw_value else 0.0
            return value
        except ValueError:
            messagebox.showerror("Помилка", f"{field_name} повинно бути числом.")
            return None

    def get_data_dict(self):
        """Має бути перевизначений. Повинен повертати словник для запису в БД."""
        raise NotImplementedError("Subclasses must implement get_data_dict")

    def clear_specific_fields(self):
        """Має бути перевизначений для очищення специфічних полів."""
        pass

    def handle_enter(self):
        data = self.get_data_dict()
        if data:
            if mongodb_functions.upload_to_db(self.collection_name, data):
                self.clear_specific_fields()

                if self.has_image:
                    self.current_file_path = None
                    self.lbl_path_text.config(text="File is not selected")
                    self.lbl_preview.config(image="", text="Place for a preview")