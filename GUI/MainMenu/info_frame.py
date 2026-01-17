import sys
import os
import io
import base64
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading

# Імпорти ваших утиліт
from Utils import mongodb_functions 

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# --- Базовий клас для таблиць (щоб не дублювати код) ---
class BaseListView(tk.Frame):
    def __init__(self, parent, title, collection_name, columns):
        super().__init__(parent, bg="white")
        self.collection_name = collection_name
        self.columns = columns # Список кортежів: ("code", "Display Name", width)
        
        # Заголовок
        tk.Label(self, text=title, font=("Arial", 24, "bold"), bg="white", fg="#4a148c").pack(pady=20)

        # Контейнер для таблиці
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Скролбар
        scroll = ttk.Scrollbar(table_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Таблиця
        # Витягуємо коди колонок для Treeview
        col_names = [col[0] for col in columns]
        self.tree = ttk.Treeview(table_frame, columns=col_names, show="headings", yscrollcommand=scroll.set)
        
        scroll.config(command=self.tree.yview)
        
        # Налаштування колонок
        for col_code, col_title, col_width in columns:
            self.tree.heading(col_code, text=col_title)
            self.tree.column(col_code, width=col_width, anchor="w")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Стиль для смугастих рядків
        self.tree.tag_configure('odd', background='white')
        self.tree.tag_configure('even', background='#f2f2f2')

        # Завантаження даних
        self.load_data()

    def load_data(self):
        # Запускаємо потік
        threading.Thread(target=self._fetch_data, daemon=True).start()

    def _fetch_data(self):
        try:
            # Використовуємо існуючу функцію з пагінацією, але ставимо великий ліміт
            # Сортування по _id (1 = зростання)
            data = mongodb_functions.get_documents_paginated(
                collection_name=self.collection_name,
                query={},
                sort=[("_id", 1)], 
                limit=1000 # Завантажуємо багато, бо це просто інфо-список
            )
        except Exception as e:
            print(f"Error loading {self.collection_name}: {e}")
            data = []
        
        self.after(0, self._update_ui, data)

    def _update_ui(self, data):
        if not self.winfo_exists():
            return
            
        # Очищення таблиці
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заповнення
        for i, item in enumerate(data):
            values = []
            for col_code, _, _ in self.columns:
                # Отримуємо значення, якщо немає - прочерк
                val = item.get(col_code, "-")
                values.append(val)
            
            # Чергування кольорів
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=values, tags=(tag,))


# --- Реалізація конкретних видів ---

class AboutUsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        
        # 1. ЗАВАНТАЖЕННЯ БАНЕРА
        image_path = "Data/Images/Atelier_logo_big"
        self.banner_img = self.load_image_from_binary(image_path)
        
        if self.banner_img:
            tk.Label(self, image=self.banner_img, bg="white").pack(pady=(20, 10))

        # 2. ТЕКСТ
        tk.Label(self, text="About Us", font=("Arial", 24, "bold"), bg="white", fg="#4a148c").pack(pady=10)
        
        about_text = (
            "Welcome to Atelier Management System.\n"
            "We provide high-quality tailoring services and fabric management.\n\n"
            "Our goal is to make fashion accessible and organized."
        )
        tk.Label(self, text=about_text, font=("Arial", 14), bg="white", justify="center").pack(pady=10)

    def load_image_from_binary(self, path):
        if not os.path.exists(path): return None
        try:
            with open(path, 'rb') as f:
                file_data = f.read()
            try: image_bytes = base64.b64decode(file_data)
            except: image_bytes = file_data
            
            pil_image = Image.open(io.BytesIO(image_bytes))
            base_height = 150
            w_percent = (base_height / float(pil_image.size[1]))
            w_size = int((float(pil_image.size[0]) * float(w_percent)))
            pil_image = pil_image.resize((w_size, base_height), Image.LANCZOS) # type:ignore
            return ImageTk.PhotoImage(pil_image)
        except Exception: return None


class SuppliersListView(BaseListView):
    def __init__(self, parent, controller):
        # Налаштування колонок: (ключ_в_бд, назва_в_шапці, ширина)
        cols = [
            ("_id", "ID", 20),
            ("name", "Supplier Name", 100),
            ("number", "Phone Number", 80),
            ("address", "Address", 100),
            ("fabric_supply_amount", "Fabrics Supplied", 20)
        ]
        # Переконайтеся, що назва колекції в БД саме "suppliers"
        super().__init__(parent, "Our Trusted Suppliers", "suppliers", cols)


class TailorsListView(BaseListView):
    def __init__(self, parent, controller):
        # Налаштування колонок: (ключ_в_бд, назва_в_шапці, ширина)
        cols = [
            ("_id", "ID", 20),
            ("name", "Master Name", 100),
            ("number", "Phone Number", 80),
            ("annual_salary", "Annual Salary", 50),
            ("quarterly_salary", "Quarterly Salary", 50),
            ("monthy_salary", "Monthy Salary", 50),
            
        ]
        
        # [ВАЖЛИВО] Переконайтеся, що колекція в БД називається "tailors".
        # Якщо кравці зберігаються в колекції "users" з access="tailor", 
        # то тут треба буде змінити логіку завантаження (фільтрацію).
        # Але поки залишаємо окрему колекцію "tailors", як було в редакторі.
        super().__init__(parent, "Our Master Tailors", "tailors", cols)


# --- Головний фрейм Info ---

class InfoFrameView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        self.container = tk.Frame(self, bg="white")
        self.container.pack(fill="both", expand=True)

        self.create_sidebar()
        
        self.content_area = tk.Frame(self.container, bg="white")
        self.content_area.pack(side=tk.LEFT, fill="both", expand=True)

        self.open_page(AboutUsView)

    def create_sidebar(self):
        sidebar_frame = tk.Frame(self.container, bg="#f0f0f0", width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        sidebar_frame.pack_propagate(False)

        tk.Label(sidebar_frame, text="Information", font=("Arial", 16, "bold"), 
                bg="#f0f0f0", fg="#333").pack(side=tk.TOP, padx=20, pady=30, anchor="w")

        # --- Кнопки навігації ---
        self.create_nav_button(sidebar_frame, "ℹ About Us", lambda: self.open_page(AboutUsView))
        self.create_nav_button(sidebar_frame, "Suppliers", lambda: self.open_page(SuppliersListView)) # Виправлено назву класу
        self.create_nav_button(sidebar_frame, "Tailors", lambda: self.open_page(TailorsListView))

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