import sys
import os
import io
import base64  
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk 

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) 

sys.path.append(project_root)


# --- Фрейми контенту ---

class AboutUsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        
        # 1. ЗАВАНТАЖЕННЯ ТА ВІДОБРАЖЕННЯ ВЕЛИКОЇ КАРТИНКИ
        # Формуємо шлях до файлу
        image_path = "Data/Images/Atelier_logo_big"
        
        # Завантажуємо
        self.banner_img = self.load_image_from_binary(image_path)
        
        # Якщо картинка є - показуємо її найпершою
        if self.banner_img:
            tk.Label(self, image=self.banner_img, bg="white").pack(pady=(20, 10))

        # 2. ЗАГОЛОВОК І ТЕКСТ
        tk.Label(self, text="About Us", font=("Arial", 24, "bold"), bg="white").pack(pady=10)
        
        about_text = (
            "Welcome to Atelier Management System.\n"
            "We provide high-quality tailoring services and fabric management.\n\n"
            "Our goal is to make fashion accessible and organized."
        )
        tk.Label(self, text=about_text, font=("Arial", 14), bg="white", justify="center").pack(pady=10)

    def load_image_from_binary(self, path):
        """Універсальний метод завантаження (Base64 або Binary)"""
        if not os.path.exists(path):
            print(f"Картинку не знайдено: {path}")
            return None
        
        try:
            with open(path, 'rb') as f:
                file_data = f.read()
            
            # Пробуємо декодувати Base64
            try:
                image_bytes = base64.b64decode(file_data)
            except Exception:
                image_bytes = file_data
            
            # Створюємо картинку
            data_stream = io.BytesIO(image_bytes)
            pil_image = Image.open(data_stream)
            
            # --- РЕСАЙЗ ДЛЯ БАНЕРА ---
            # Робимо картинку висотою 300 пікселів, ширина підлаштується автоматично
            base_height = 150
            # Обчислюємо відсоток зменшення (h_new / h_old)
            w_percent = (base_height / float(pil_image.size[1]))
            w_size = int((float(pil_image.size[0]) * float(w_percent)))
            
            pil_image = pil_image.resize((w_size, base_height), Image.LANCZOS) # type: ignore
            # -------------------------
            
            return ImageTk.PhotoImage(pil_image)
            
        except Exception as e:
            print(f"Помилка AboutUs зображення: {e}")
            return None


class SuppliersView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="Our Suppliers", font=("Arial", 24, "bold"), bg="white").pack(pady=20)
        tk.Label(self, text="List of trusted fabric suppliers will be here.", font=("Arial", 12), bg="white").pack()

class TailorsListView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        tk.Label(self, text="Our Master Tailors", font=("Arial", 24, "bold"), bg="white").pack(pady=20)
        tk.Label(self, text="Meet our professional team.", font=("Arial", 12), bg="white").pack()


# --- Головний фрейм Info ---

class InfoFrameView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        # 1. Головний контейнер
        self.container = tk.Frame(self, bg="white")
        self.container.pack(fill="both", expand=True)

        # 2. Створюємо структуру
        self.create_sidebar()
        
        self.content_area = tk.Frame(self.container, bg="white")
        self.content_area.pack(side=tk.LEFT, fill="both", expand=True)

        # 3. Відкриваємо сторінку за замовчуванням
        self.open_page(AboutUsView)

    def create_sidebar(self):
        sidebar_frame = tk.Frame(self.container, bg="#f0f0f0", width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_frame.pack_propagate(False)

        tk.Label(sidebar_frame, text="Information", font=("Arial", 16, "bold"), 
                bg="#f0f0f0", fg="#333").pack(side=tk.TOP, padx=20, pady=30, anchor="w")

        # --- Кнопки навігації ---
        self.create_nav_button(sidebar_frame, "ℹ About Us", lambda: self.open_page(AboutUsView))
        self.create_nav_button(sidebar_frame, "Suppliers", lambda: self.open_page(SuppliersView))
        self.create_nav_button(sidebar_frame, "Tailors", lambda: self.open_page(TailorsListView))

        # --- Розділ EXTRA ---
        tk.Label(sidebar_frame, text="EXTRA", font=("Arial", 10, "bold"), 
                 bg="#f0f0f0", fg="gray").pack(anchor="w", padx=20, pady=(30, 5))

    def create_nav_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, font=("Arial", 12), 
                        bg="#f0f0f0", fg="#333",
                        activebackground="#e0e0e0", activeforeground="black",
                        bd=0, relief="flat", cursor="hand2", anchor="w",
                        command=command)
        btn.pack(side=tk.TOP, fill=tk.X, padx=10, pady=2, ipady=5)
        
        btn.bind("<Enter>", lambda e: btn.config(bg="#e0e0e0"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#f0f0f0"))

    def open_page(self, frame_class):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        new_frame = frame_class(self.content_area, self.controller)
        new_frame.pack(fill="both", expand=True, padx=40, pady=40)