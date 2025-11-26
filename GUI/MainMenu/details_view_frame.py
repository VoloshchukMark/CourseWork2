import os
import sys
import tkinter as tk
import io
from PIL import Image, ImageTk

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class DetailsView(tk.Toplevel):
    def __init__(self, parent, item_data, item_type):
        super().__init__(parent)
        
        self.item_data = item_data
        self.item_type = item_type
        
        self.title(f"Details: {item_data.get('name', 'Unknown')}")
        self.geometry("900x600")
        self.configure(bg="white")
        
        self.transient(parent)
        self.wait_visibility()
        self.grab_set()        # Захоплює всі події миші/клавіатури
        self.focus_set()       # Переводить фокус на це вікно
        
        # --- 2. ГОЛОВНИЙ КОНТЕЙНЕР (Розподіл 50/50) ---
        self.grid_columnconfigure(0, weight=1, uniform="group1") # Ліва частина
        self.grid_columnconfigure(1, weight=1, uniform="group1") # Права частина
        self.grid_rowconfigure(0, weight=1)

        # --- ЛІВА ЧАСТИНА (Фото, Назва, Опис) ---
        self.left_frame = tk.Frame(self, bg="white", padx=20, pady=20)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # Кнопка Back
        btn_back = tk.Button(self.left_frame, text="⬅ Back", font=("Arial", 12), 
                             command=self.destroy, bg="#f0f0f0", cursor="hand2")
        btn_back.pack(anchor="w", pady=(0, 20))

        # Зображення (Велике)
        self.image_label = tk.Label(self.left_frame, bg="white")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        self.load_large_image()

        # Назва
        name_id_frame = tk.Frame(self.left_frame, bg="white")
        name_id_frame.pack(pady=(20, 10), anchor="w", fill="x")

        # 2. Назва (Зліва)
        tk.Label(name_id_frame, text=self.item_data.get('name', 'Unknown'), 
                 font=("Arial", 24, "bold"), bg="white").pack(side="left")

        # 3. ID (Справа від назви, сірим кольором)
        item_id = self.item_data.get('_id', '')
        if item_id:
            tk.Label(name_id_frame, text=f"#{item_id}", 
                     font=("Arial", 16), fg="gray", bg="white").pack(side="left", padx=10, anchor="sw", pady=5)

        # Опис
        desc_text = item_data.get('description', 'No description available.')
        desc_lbl = tk.Label(self.left_frame, text=desc_text, font=("Arial", 12), 
                            bg="white", justify="left", wraplength=400, anchor="w")
        desc_lbl.pack(fill=tk.X, anchor="w")


        # --- ПРАВА ЧАСТИНА (Деталі) ---
        self.right_frame = tk.Frame(self, bg="#f9f9f9", padx=30, pady=50)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # Ціна та Наявність
        self.create_detail_row("Price:", f"{item_data.get('price', 0)} UAH")
        
        in_stock = item_data.get('in_stock', False)
        stock_text = "In Stock" if in_stock else "Out of Stock"
        stock_color = "green" if in_stock else "red"
        self.create_detail_row("Availability:", stock_text, value_color=stock_color)

        # Специфічні поля залежно від типу
        tk.Frame(self.right_frame, height=2, bg="#ddd").pack(fill=tk.X, pady=20) # Розділювач

        if self.item_type == "model":
            self.create_detail_row("Recommended Fabric:", item_data.get('recommended_fabric', '-'))
            self.create_detail_row("Recomended accessories:", item_data.get('recommended_accessories', '-'))
        else: # Fabric
            self.create_detail_row("Manufacturer ID:", item_data.get('fabric_manufacturer_id', '-'))
            self.create_detail_row("Color:", item_data.get('fabric_color', '-'))
            self.create_detail_row("Texture:", item_data.get('fabric_texture', '-'))
            self.create_detail_row("Width:", item_data.get('width', '-'))

    def create_detail_row(self, label, value, value_color="black"):
        """Допоміжний метод для красивих рядків"""
        frame = tk.Frame(self.right_frame, bg="#f9f9f9")
        frame.pack(fill=tk.X, pady=10)
        
        tk.Label(frame, text=label, font=("Arial", 12, "bold"), fg="gray", bg="#f9f9f9").pack(side=tk.LEFT)
        tk.Label(frame, text=value, font=("Arial", 14), fg=value_color, bg="#f9f9f9").pack(side=tk.RIGHT)

    def load_large_image(self):
        image_binary = self.item_data.get('original_image_binary')
        
        if image_binary:
            try:
                img_data = io.BytesIO(image_binary)
                pil_img = Image.open(img_data)
                
                # Робимо картинку більшою (наприклад, 400px)
                pil_img.thumbnail((400, 400))
                
                # Якщо не в наявності - робимо ч/б
                if not self.item_data.get('in_stock', True):
                    pil_img = pil_img.convert("L")

                self.photo = ImageTk.PhotoImage(pil_img)
                self.image_label.config(image=self.photo)
            except Exception:
                self.image_label.config(text="Image Error")
        else:
            self.image_label.config(text="No Image", bg="#eee")