import sys
import os
import io
import base64
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime
import threading

# Імпорти ваших утиліт
from Utils import mongodb_functions 

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# --- Базовий клас для таблиць ---
class BaseListView(tk.Frame):
    def __init__(self, parent, title, collection_name, columns, custom_loader=None):
        super().__init__(parent, bg="white")
        self.collection_name = collection_name
        self.columns = columns # Список кортежів: ("code", "Display Name", width)
        self.custom_loader = custom_loader # [НОВЕ] Функція для специфічного завантаження
        
        # Заголовок
        tk.Label(self, text=title, font=("Arial", 24, "bold"), bg="white", fg="#4a148c").pack(pady=20)

        # Контейнер для таблиці
        table_frame = tk.Frame(self, bg="white")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Скролбар
        scroll = ttk.Scrollbar(table_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Таблиця
        col_names = [col[0] for col in columns]
        self.tree = ttk.Treeview(table_frame, columns=col_names, show="headings", yscrollcommand=scroll.set)
        
        scroll.config(command=self.tree.yview)
        
        # Налаштування колонок
        for col_code, col_title, col_width in columns:
            self.tree.heading(col_code, text=col_title)
            self.tree.column(col_code, width=col_width, anchor="w")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Стиль
        self.tree.tag_configure('odd', background='white')
        self.tree.tag_configure('even', background='#f2f2f2')

        # Завантаження даних
        self.load_data()

    def load_data(self):
        # Запускаємо потік
        threading.Thread(target=self._fetch_data, daemon=True).start()

    def _fetch_data(self):
        try:
            if self.custom_loader:
                # [НОВЕ] Якщо є спец. функція (для постачальників з підрахунком)
                # Передаємо великий ліміт, щоб показати всіх
                data = self.custom_loader(skip=0, limit=1000)
            else:
                # Стандартне завантаження для інших (Кравці)
                data = mongodb_functions.get_documents_paginated(
                    collection_name=self.collection_name,
                    query={},
                    sort=[("_id", 1)], 
                    limit=1000 
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
                val = item.get(col_code, "-")
                values.append(val)
            
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=values, tags=(tag,))


# --- Реалізація конкретних видів ---

class AboutUsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        
        # БАНЕР
        image_path = "Data/Images/Atelier_logo_big"
        self.banner_img = self.load_image_from_binary(image_path)
        
        if self.banner_img:
            tk.Label(self, image=self.banner_img, bg="white").pack(pady=(20, 10))

        # ТЕКСТ
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
            pil_image = pil_image.resize((w_size, base_height), Image.LANCZOS) #type: ignore
            return ImageTk.PhotoImage(pil_image)
        except Exception: return None


class SuppliersListView(BaseListView):
    def __init__(self, parent, controller):
        cols = [
            ("_id", "ID", 50),
            ("name", "Supplier Name", 200),
            ("number", "Phone Number", 150),
            ("address", "Address", 200),
            ("fabric_supply_amount", "Fabric Count", 120) # [ЗМІНЕНО] Назва колонки
        ]
        
        # [ВАЖЛИВО] Передаємо custom_loader, щоб рахувало тканини
        super().__init__(
            parent, 
            "Our Trusted Suppliers", 
            "suppliers", 
            cols,
            custom_loader=mongodb_functions.get_suppliers_paginated
        )


class TailorsListView(BaseListView):
    def __init__(self, parent, controller):
        cols = [
            ("_id", "ID", 50),
            ("name", "Master Name", 200),
            ("number", "Phone", 150),
            ("annual_salary", "Annual Sal.", 50),
            ("quarterly_salary", "Quarterly Sal.", 50),
            ("monthy_salary", "Monthy Sal.", 50)
        ]
        # Для кравців custom_loader не потрібен (None за замовчуванням)
        super().__init__(parent, "Our Master Tailors", "tailors", cols)

class TopSuppliersView(BaseListView):
    def __init__(self, parent, controller):
        cols = [
            ("_id", "ID", 50),
            ("name", "Supplier Name", 200),
            ("number", "Phone Number", 150),
            ("address", "Address", 200),
            ("fabric_supply_amount", "Fabric Count", 120)
        ]
        
        # Тепер ми просто передаємо функцію з mongodb_functions, 
        # яка вже робить все сортування всередині бази.
        super().__init__(
            parent, 
            "Top Suppliers (By Stock)", 
            "suppliers", 
            cols,
            custom_loader=mongodb_functions.get_top_suppliers_by_amount
        )

class TopFabricsView(BaseListView):
    def __init__(self, parent, controller):
        # popularity, _id, fabric_name, fabric_color, fabric_texture, price_per_meter, width_in_meters
        cols = [
            ("popularity", "Popularity", 80),
            ("_id", "ID", 50),
            ("fabric_name", "Fabric Name", 180),
            ("fabric_color", "Color", 100),
            ("fabric_texture", "Texture", 120),
            ("price_per_meter", "Price", 80),
            ("width_in_meters", "Width", 80)
        ]
        
        super().__init__(
            parent, 
            "Fabric Popularity Rating", # Заголовок
            "fabrics", 
            cols,
            custom_loader=mongodb_functions.get_top_fabrics_by_popularity
        )
    
class AtelierRevenueView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        
        # --- Заголовок ---
        tk.Label(self, text="Atelier Revenue Analysis", font=("Arial", 24, "bold"), 
                 bg="white", fg="#4a148c").pack(pady=(20, 10))

        # --- Панель керування (Вибір року) ---
        controls_frame = tk.Frame(self, bg="white")
        controls_frame.pack(fill=tk.X, padx=40, pady=10)

        tk.Label(controls_frame, text="Select Year:", bg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        # Генеруємо список років (поточний + 4 минулих)
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year, current_year - 5, -1)]
        
        self.year_var = tk.StringVar(value=str(current_year))
        self.year_combo = ttk.Combobox(controls_frame, textvariable=self.year_var, values=years, state="readonly", width=10)
        self.year_combo.pack(side=tk.LEFT, padx=5)
        self.year_combo.bind("<<ComboboxSelected>>", self.refresh_chart)

        # --- Canvas для графіка ---
        # width=800, height=400 - розмір полотна
        self.canvas_width = 900
        self.canvas_height = 450
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)
        self.canvas.pack(pady=20)

        # Завантажуємо дані для стартового року
        self.refresh_chart()

    def refresh_chart(self, event=None):
        year = self.year_var.get()
        # 1. Отримуємо дані з БД (в окремому потоці, щоб не зависало, хоча тут це швидко)
        threading.Thread(target=self._load_and_draw, args=(year,), daemon=True).start()

    def _load_and_draw(self, year):
        data_map = mongodb_functions.get_monthly_revenue(year)
        # Передаємо оновлення UI в головний потік
        self.after(0, self.draw_graph, data_map)

    def draw_graph(self, data_map):
        self.canvas.delete("all") # Очищаємо полотно

        # --- Налаштування відступів ---
        margin_left = 60
        margin_bottom = 50
        margin_top = 40
        graph_width = self.canvas_width - margin_left - 20
        graph_height = self.canvas_height - margin_bottom - margin_top

        # --- Підготовка даних ---
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        values = [data_map.get(i, 0) for i in range(1, 13)] # Список сум по місяцях (0 якщо немає)
        
        max_val = max(values)
        if max_val == 0: max_val = 100 # Щоб не ділити на нуль, якщо даних немає

        # --- 1. Малюємо осі ---
        # Вертикальна лінія (Y)
        self.canvas.create_line(margin_left, margin_top, margin_left, self.canvas_height - margin_bottom, width=2, fill="gray")
        # Горизонтальна лінія (X)
        self.canvas.create_line(margin_left, self.canvas_height - margin_bottom, self.canvas_width - 20, self.canvas_height - margin_bottom, width=2, fill="gray")

        # --- 2. Малюємо стовпчики ---
        bar_width = graph_width / 12 * 0.6 # Ширина стовпчика (60% від доступного місця)
        step_x = graph_width / 12          # Крок між центрами місяців

        for i, val in enumerate(values):
            # Координати X
            center_x = margin_left + (i * step_x) + (step_x / 2)
            x0 = center_x - (bar_width / 2)
            x1 = center_x + (bar_width / 2)

            # Координати Y (висота стовпчика)
            # Формула: (значення / макс) * доступна_висота
            bar_height = (val / max_val) * graph_height
            y1 = self.canvas_height - margin_bottom # Низ (на осі X)
            y0 = y1 - bar_height                    # Верх

            # Колір стовпчика (градієнт або просто колір)
            color = "#7c4dff" if val > 0 else "#e0e0e0"

            # Малюємо прямокутник
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

            # Підпис місяця знизу
            self.canvas.create_text(center_x, y1 + 15, text=months[i], font=("Arial", 10))

            # Підпис суми зверху стовпчика (якщо > 0)
            if val > 0:
                self.canvas.create_text(center_x, y0 - 10, text=f"{int(val)} UAH", font=("Arial", 9, "bold"), fill="#333")

        # --- 3. Підпис осі Y (Максимум) ---
        self.canvas.create_text(margin_left - 30, margin_top, text=f"{int(max_val)} UAH", font=("Arial", 10), anchor="e")
        # self.canvas.create_text(margin_left - 30, self.canvas_height - margin_bottom, text="0 UAH", font=("Arial", 10), anchor="e")


class AtelierOrdersCountView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        
        # --- Заголовок ---
        tk.Label(self, text="Monthly Orders Count", font=("Arial", 24, "bold"), 
                 bg="white", fg="#e65100").pack(pady=(20, 10))

        # --- Панель керування ---
        controls_frame = tk.Frame(self, bg="white")
        controls_frame.pack(fill=tk.X, padx=40, pady=10)

        tk.Label(controls_frame, text="Select Year:", bg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year, current_year - 5, -1)]
        
        self.year_var = tk.StringVar(value=str(current_year))
        self.year_combo = ttk.Combobox(controls_frame, textvariable=self.year_var, values=years, state="readonly", width=10)
        self.year_combo.pack(side=tk.LEFT, padx=5)
        self.year_combo.bind("<<ComboboxSelected>>", self.refresh_chart)

        # --- Canvas ---
        self.canvas_width = 900
        self.canvas_height = 450
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white", highlightthickness=0)
        self.canvas.pack(pady=20)

        self.refresh_chart()

    def refresh_chart(self, event=None):
        year = self.year_var.get()
        # Викликаємо функцію підрахунку кількості
        threading.Thread(target=self._load_and_draw, args=(year,), daemon=True).start()

    def _load_and_draw(self, year):
        # [ЗМІНА] Використовуємо нову функцію
        data_map = mongodb_functions.get_monthly_orders_count(year)
        self.after(0, self.draw_graph, data_map)

    def draw_graph(self, data_map):
        self.canvas.delete("all")

        margin_left = 60
        margin_bottom = 50
        margin_top = 40
        graph_width = self.canvas_width - margin_left - 20
        graph_height = self.canvas_height - margin_bottom - margin_top

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        values = [data_map.get(i, 0) for i in range(1, 13)]
        
        max_val = max(values)
        if max_val == 0: max_val = 10 # Мінімальний масштаб, якщо пусто

        # Осі
        self.canvas.create_line(margin_left, margin_top, margin_left, self.canvas_height - margin_bottom, width=2, fill="gray")
        self.canvas.create_line(margin_left, self.canvas_height - margin_bottom, self.canvas_width - 20, self.canvas_height - margin_bottom, width=2, fill="gray")

        # Стовпчики
        bar_width = graph_width / 12 * 0.6
        step_x = graph_width / 12

        for i, val in enumerate(values):
            center_x = margin_left + (i * step_x) + (step_x / 2)
            x0 = center_x - (bar_width / 2)
            x1 = center_x + (bar_width / 2)

            bar_height = (val / max_val) * graph_height
            y1 = self.canvas_height - margin_bottom
            y0 = y1 - bar_height

            color = "#7c4dff" if val > 0 else "#e0e0e0"

            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            self.canvas.create_text(center_x, y1 + 15, text=months[i], font=("Arial", 10))

            if val > 0:
                # [ЗМІНА] Просто число (кількість)
                self.canvas.create_text(center_x, y0 - 10, text=f"{int(val)}", font=("Arial", 9, "bold"), fill="#333")

        # Підписи осі Y
        self.canvas.create_text(margin_left - 30, margin_top, text=f"{int(max_val)}", font=("Arial", 10), anchor="e")
        self.canvas.create_text(margin_left - 30, self.canvas_height - margin_bottom, text="0", font=("Arial", 10), anchor="e")


class SystemOverviewView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        
        # Заголовок
        tk.Label(self, text="System Overview", font=("Arial", 24, "bold"), 
                 bg="white", fg="#263238").pack(pady=(30, 20))

        # Контейнер для карток (Grid)
        self.cards_container = tk.Frame(self, bg="white")
        self.cards_container.pack(expand=True, fill="both", padx=50)

        # Запускаємо завантаження даних
        threading.Thread(target=self.load_stats, daemon=True).start()

    def load_stats(self):
        # Отримуємо дані з БД
        n_users = mongodb_functions.get_collection_count("user")
        n_tailors = mongodb_functions.get_collection_count("tailors")
        
        # Додаткові метрики для краси
        n_fabrics = mongodb_functions.get_collection_count("fabrics")
        # Рахуємо тільки активні замовлення (не Cancelled і не Completed, наприклад)
        # Або просто всі замовлення, якщо хочете
        n_orders = mongodb_functions.get_collection_count("orders") 

        # Оновлюємо UI
        self.after(0, self.create_cards, n_users, n_tailors, n_fabrics, n_orders)

    def create_cards(self, users, tailors, fabrics, orders):
        # Створюємо 4 картки
        # (Рядок, Колонка, Заголовок, Значення, Колір)
        
        self.draw_card(0, 0, "Registered Clients", users, "#42a5f5")   # Blue
        self.draw_card(0, 1, "Master Tailors", tailors, "#66bb6a")     # Green
        self.draw_card(1, 0, "Total Fabric Types", fabrics, "#ab47bc") # Purple
        self.draw_card(1, 1, "Total Orders", orders, "#ffa726")        # Orange

        # Налаштування розтягування сітки
        self.cards_container.grid_columnconfigure(0, weight=1)
        self.cards_container.grid_columnconfigure(1, weight=1)

    def draw_card(self, row, col, title, value, color):
        # Фрейм картки (Card Look)
        card = tk.Frame(self.cards_container, bg=color, padx=20, pady=20)
        card.grid(row=row, column=col, sticky="nsew", padx=15, pady=15)

        # Значення (Велика цифра)
        tk.Label(card, text=str(value), font=("Arial", 40, "bold"), 
                 bg=color, fg="white").pack(anchor="w")

        # Назва (Підпис)
        tk.Label(card, text=title, font=("Arial", 14), 
                 bg=color, fg="white").pack(anchor="w")


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

        self.create_nav_button(sidebar_frame, "ℹ About Us", lambda: self.open_page(AboutUsView))
        self.create_nav_button(sidebar_frame, "Suppliers", lambda: self.open_page(SuppliersListView))
        self.create_nav_button(sidebar_frame, "Tailors", lambda: self.open_page(TailorsListView))

        # EXTRA
        tk.Label(sidebar_frame, text="EXTRA", font=("Arial", 10, "bold"), 
                 bg="#f0f0f0", fg="gray").pack(anchor="w", padx=20, pady=(30, 5))
        
        self.create_extra_button(sidebar_frame, "General Statistics", 
                                 lambda: self.open_page(SystemOverviewView))
        self.create_extra_button(sidebar_frame, "Sort Suppliers by fabric amount", 
                                 lambda: self.open_page(TopSuppliersView))
        self.create_extra_button(sidebar_frame, "Fabric Popularity", 
                                 lambda: self.open_page(TopFabricsView))
        self.create_extra_button(sidebar_frame, "Atelier Revenue", 
                                 lambda: self.open_page(AtelierRevenueView))
        self.create_extra_button(sidebar_frame, "Amount of Orders", 
                                 lambda: self.open_page(AtelierOrdersCountView))

    def create_nav_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, font=("Arial", 12), 
                        bg="#f0f0f0", fg="#333",
                        activebackground="#e0e0e0", activeforeground="black",
                        bd=0, relief="flat", cursor="hand2", anchor="w",
                        command=command)
        btn.pack(side=tk.TOP, fill=tk.X, padx=10, pady=2, ipady=5)
        
        btn.bind("<Enter>", lambda e: btn.config(bg="#e0e0e0"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#f0f0f0"))
    
    def create_extra_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, font=("Arial", 9), # Менший шрифт
                        bg="#f0f0f0", fg="#555", # Трохи сіріший колір
                        activebackground="#e0e0e0", activeforeground="black",
                        bd=0, relief="flat", cursor="hand2", anchor="w",
                        command=command)
        # Більший відступ зліва (padx=25), щоб показати вкладеність
        btn.pack(side=tk.TOP, fill=tk.X, padx=25, pady=1)
        
        btn.bind("<Enter>", lambda e: btn.config(fg="black")) # При наведенні стає чорним
        btn.bind("<Leave>", lambda e: btn.config(fg="#555"))

    def open_page(self, frame_class):
        for widget in self.content_area.winfo_children():
            widget.destroy()

        new_frame = frame_class(self.content_area, self.controller)
        new_frame.pack(fill="both", expand=True, padx=40, pady=40)