import sys, os, io
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import base64

from Utils import tkinter_general, session
from GUI.MainMenu.catalog import CatalogView
from GUI.MainMenu.account import AccountView
from GUI.MainMenu.info_frame import InfoFrameView
from GUI.MainMenu.my_orders import MyOrdersView

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class MainFrameView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6ccff")
        self.controller = controller

        self.controller.title("Atelier")
        tkinter_general.center_window(self.controller, 1200, 800) 

        # Словник для зберігання кнопок навігації
        self.nav_buttons = {} 

        # 1. Створюємо загальний контейнер
        self.container = tk.Frame(self, bg="white")
        self.container.pack(fill="both", expand=True)

        self.editor_window = None

        # 2. Створюємо статичний Хедер
        self.create_header()

        # 3. Створюємо контейнер для динамічного контенту
        self.content_area = tk.Frame(self.container, bg="white")
        self.content_area.pack(fill="both", expand=True)

        # 4. Завантажуємо стартову сторінку (Каталог)
        self.current_content_frame = None
        self.switch_content(CatalogView)

    def create_header(self):
        header = tk.Frame(self.container, bg="white", height=60)
        header.pack(fill="x", side="top", pady=(0, 2))
        header.pack_propagate(False)

        # ЛОГОТИП
        logo_frame = tk.Frame(header, bg="white")
        logo_frame.pack(side="left", padx=20)
        tk.Label(logo_frame, text="ATELIER", font=("Georgia", 20, "bold"), fg="#4a148c", bg="white").pack()

        # НАВІГАЦІЯ (Кнопки)
        nav_frame = tk.Frame(header, bg="white")
        nav_frame.pack(side="right", padx=30, fill="y")

        # Список вкладок, які будуть у шапці
        # (MyOrdersView тут немає, бо ми заходимо в нього через акаунт, але це можна змінити)
        menu_items = [
            ("CATALOG", CatalogView),
            ("INFO", InfoFrameView),    
            ("MY ORDERS", MyOrdersView),
            ("ACCOUNT", AccountView)
        ]

        for text, view_class in menu_items:
            btn = tk.Button(nav_frame, text=text, 
                            font=("Arial", 14), 
                            bg="white", fg="#333", 
                            bd=0, cursor="hand2",
                            command=lambda vc=view_class: self.switch_content(vc))
            btn.pack(side="left", padx=15, pady=10)
            
            # Зберігаємо кнопку, щоб потім змінювати її стиль
            self.nav_buttons[view_class] = btn

        # Кнопка адмінки (якщо юзер адмін)
        if session.current_user and getattr(session.current_user, 'access', '') == 'admin':
            admin_btn = tk.Button(nav_frame, text="⚙ Editor", bg="#461680", fg="white", 
                                  font=("Arial", 12, "bold"), cursor="hand2",
                                  command=self.open_editor)
            admin_btn.pack(side="left", padx=15)

    def update_active_button_style(self, active_class):
        """
        Змінює стиль кнопок. 
        Примітка: Якщо ми перейшли на MyOrdersView (якого немає в кнопках),
        всі кнопки стануть "пасивними", що логічно.
        """
        active_bg = "#d1b3ff"
        default_bg = "white"

        for view_cls, btn in self.nav_buttons.items():
            if view_cls == active_class:
                btn.config(bg=active_bg, relief="sunken", font=("Arial", 14, "bold"))
            else:
                btn.config(bg=default_bg, relief="flat", font=("Arial", 14, "normal"))

    def switch_content(self, frame_class):
        # 1. Оновлюємо вигляд кнопок
        self.update_active_button_style(frame_class)

        # 2. Видаляємо старий контент
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # 3. Створюємо новий фрейм
        new_frame = frame_class(self.content_area, self.controller)
        
        # !!! ОСЬ ЦЬОГО РЯДКА НЕ ВИСТАЧАЄ !!!
        new_frame.main_view = self  # <--- ДОДАЙ ЦЕ
        
        new_frame.pack(fill="both", expand=True)
        
        self.current_content_frame = new_frame

    def open_editor(self):
        """Відкриває вікно редактора (тільки для адмінів)"""
        from GUI.Editor.editor_frame import EditorFrameView

        if self.editor_window is None or not self.editor_window.winfo_exists():
            self.editor_window = EditorFrameView()
        else:
            self.editor_window.lift()
            self.editor_window.focus_set()