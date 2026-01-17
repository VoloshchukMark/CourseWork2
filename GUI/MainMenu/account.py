import io, os, sys
import tkinter as tk
from tkinter import simpledialog, messagebox # Для вікон вводу
import base64
from PIL import Image, ImageTk

from Authentication.login import LoginView
from Utils import session
from Utils import mongodb_functions
from GUI.MainMenu.my_orders import MyOrdersView
from GUI.MainMenu.orders_history import OrdersHistoryWindow
# Припускаємо, що у вас є функція оновлення БД
# from Utils import mongodb_functions 

class AccountView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white") # Білий фон для чистоти
        self.controller = controller
        
        # 1. Завантажуємо дані з сесії
        self.load_user_data()
        
        # 2. Завантажуємо іконку
        self.user_icon = self.import_user_icon()
        
        # Словник для зберігання лейблів, які ми будемо оновлювати (email, phone)
        self.dynamic_labels = {} 

        self.create_widgets()

    def load_user_data(self):
        # Дефолтні значення
        self.login = "Unknown"
        self.username = "Unknown"
        self.email = "Not set"
        self.number = "Not set"
        self.access = "guest"
        self.address = "Not set"

        if session.current_user:
             self.login = getattr(session.current_user, 'login', "Unknown")
             self.username = getattr(session.current_user, 'username', "Unknown")
             self.email = getattr(session.current_user, 'email', "Not set")
             # Перетворюємо число в рядок, якщо треба
             self.number = str(getattr(session.current_user, 'number', "Not set"))
             raw_access = getattr(session.current_user, 'access', None)
             self.access = raw_access if raw_access else "user"
             self.address = getattr(session.current_user, 'address', "Not set")

    def create_widgets(self):
        # Головний контейнер з відступами, щоб все не липло до країв
        main_container = tk.Frame(self, bg="white")
        main_container.pack(fill="both", expand=True, padx=40, pady=20)

        # --- 1. USER HEADER FRAME (Іконка + Імена) ---
        self.create_user_header(main_container)
        
        # Розділювач (Лінія)
        tk.Frame(main_container, height=2, bg="#f0f0f0").pack(fill="x", pady=20)

        # --- 2. ACCOUNT INFO FRAME (Деталі + Кнопки Change) ---
        self.create_account_details(main_container)

        # Розділювач
        tk.Frame(main_container, height=2, bg="#f0f0f0").pack(fill="x", pady=20)

        # --- 3. ORDERS FRAME (Текстові кнопки) ---
        self.create_orders_section(main_container)

        btn_logout = tk.Button(self, text="Log Out", font=("Arial", 12, "bold"), 
                               fg="white", bg="#99707e", # Червоний колір
                               relief="flat", cursor="hand2",
                               command=self.logout)
        btn_logout.pack(side="bottom", fill="x", pady=0, ipady=10)

    def create_user_header(self, parent):
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill="x", anchor="w")

        # --- ЛІВА ЧАСТИНА: ІКОНКА ---
        icon_lbl = tk.Label(header_frame, bg="white")
        if self.user_icon:
            icon_lbl.config(image=self.user_icon)
            icon_lbl.image = self.user_icon # type: ignore
        else:
            icon_lbl.config(text="No\nPhoto", bg="#eee", width=10, height=5)
        
        icon_lbl.pack(side="left", padx=(0, 20))

        # --- ПРАВА ЧАСТИНА: ТЕКСТИ ---
        text_frame = tk.Frame(header_frame, bg="white")
        text_frame.pack(side="left", fill="y")

        # 1. РЯДОК З ІМЕНЕМ ТА КНОПКОЮ (НОВЕ)
        username_row = tk.Frame(text_frame, bg="white")
        username_row.pack(anchor="w", fill="x")

        # Лейбл імені
        username_lbl = tk.Label(username_row, text=self.username, font=("Arial", 20, "bold"), 
                                bg="white", fg="#333")
        username_lbl.pack(side="left")
        
        # ВАЖЛИВО: Реєструємо лейбл, щоб він оновлювався при зміні
        self.dynamic_labels["username"] = username_lbl 

        # Маленька кнопка редагування (олівець або текст "edit")
        btn_edit_name = tk.Button(username_row, text="✎", font=("Arial", 12), 
                                  bg="white", fg="gray", bd=0, cursor="hand2",
                                  activebackground="white", activeforeground="black",
                                  command=lambda: self.change_data_popup("username"))
        btn_edit_name.pack(side="left", padx=10, pady=5)

        # 2. LOGIN (залишається як був)
        tk.Label(text_frame, text=f"@{self.login}", font=("Arial", 14), 
                 bg="white", fg="gray").pack(anchor="w")
        
        # 3. ACCESS (залишається як був)
        access_color = "#d8b6f8" if self.access == "admin" else "gray"
        tk.Label(text_frame, text=self.access.upper(), font=("Arial", 10, "bold"), 
                 bg="white", fg=access_color).pack(anchor="w", pady=(5,0))
    def create_account_details(self, parent):
        info_frame = tk.Frame(parent, bg="white")
        info_frame.pack(fill="x", anchor="w")

        # Заголовок
        tk.Label(info_frame, text="Account Info", font=("Arial", 16, "bold"), 
                 bg="white", fg="#333").pack(anchor="w", pady=(0, 15))

        # Сітка для вирівнювання (Label | Value | Button)
        grid_frame = tk.Frame(info_frame, bg="white")
        grid_frame.pack(fill="x", anchor="w")
        grid_frame.columnconfigure(1, weight=1) # Друга колонка розтягується

        # Створюємо рядки
        self.create_info_row(grid_frame, 0, "Email:", self.email, "email")
        self.create_info_row(grid_frame, 1, "Phone:", self.number, "number")
        self.create_info_row(grid_frame, 2, "Address:", self.address, "address")
        
        # Рядок Access без кнопки зміни (бо це права доступу)
        tk.Label(grid_frame, text="Access:", font=("Arial", 12, "bold"), bg="white", fg="#555").grid(row=3, column=0, sticky="w", pady=5)
        tk.Label(grid_frame, text=self.access, font=("Arial", 12), bg="white").grid(row=3, column=1, sticky="w", padx=10)
        
    def create_info_row(self, parent, row, label_text, value_text, field_key):
        """Допоміжна функція для створення рядка з кнопкою Change"""
        # 1. Назва поля
        tk.Label(parent, text=label_text, font=("Arial", 12, "bold"), bg="white", fg="#555").grid(row=row, column=0, sticky="w", pady=8)
        
        # 2. Значення (Зберігаємо лейбл у словник, щоб потім оновити текст)
        val_lbl = tk.Label(parent, text=value_text, font=("Arial", 12), bg="white", fg="black")
        val_lbl.grid(row=row, column=1, sticky="w", padx=10)
        self.dynamic_labels[field_key] = val_lbl

        # 3. Кнопка Change-----------------------------------------------------------------
        btn = tk.Button(parent, text="Change", font=("Arial", 9), 
                        bg="#e0e0e0", activebackground="#d0d0d0", relief="groove",
                        command=lambda: self.change_data_popup(field_key))
        btn.grid(row=row, column=2, sticky="e")

    def create_orders_section(self, parent):
        orders_frame = tk.Frame(parent, bg="white")
        orders_frame.pack(fill="x", anchor="w")

        tk.Label(orders_frame, text="Orders", font=("Arial", 16, "bold"), 
                 bg="white", fg="#333").pack(anchor="w", pady=(0, 10))

        # Кнопки-посилання
        self.create_link_button(orders_frame, "  My Orders", lambda: self.main_view.switch_content(MyOrdersView)) #type: ignore
        self.create_link_button(orders_frame, "  Orders History", self.open_history_window)

    def create_link_button(self, parent, text, command):
        """Створює кнопку, схожу на текст (без рамок)"""
        btn = tk.Button(parent, text=text, font=("Arial", 12), 
                        bg="white", fg="#007bff", # Синій колір як у посилань
                        activebackground="white", activeforeground="#0056b3",
                        bd=0, relief="flat", cursor="hand2", # Курсор руки
                        anchor="w", command=command)
        btn.pack(fill="x", pady=2)
        
        # Ефект підкреслення при наведенні (опціонально)
        btn.bind("<Enter>", lambda e: btn.config(font=("Arial", 12, "underline")))
        btn.bind("<Leave>", lambda e: btn.config(font=("Arial", 12)))

    def change_data_popup(self, field_key):
        """Викликає вікно вводу і зберігає зміни в БД та Сесії"""
        
        # 1. Отримуємо старе значення
        current_val = self.dynamic_labels[field_key].cget("text")
        
        # 2. Запитуємо нове
        new_val = simpledialog.askstring(
            f"Change {field_key}", 
            f"Enter new {field_key}:", 
            initialvalue=current_val, 
            parent=self
        )
        
        # 3. Якщо значення валідне і змінилося
        if new_val and new_val != current_val:
            
            # --- А. Оновлюємо Інтерфейс (UI) ---
            self.dynamic_labels[field_key].config(text=new_val)
            
            # --- Б. Оновлюємо Глобальну Сесію ---
            if session.current_user:
                # setattr дозволяє оновити атрибут за його назвою (строкою)
                setattr(session.current_user, field_key, new_val)
                
                # Якщо змінили username, треба оновити і self.username для коректності
                if field_key == "username":
                    self.username = new_val

            # --- В. Оновлюємо Базу Даних (MongoDB) ---
            # self.login ми отримали ще при ініціалізації класу з сесії
            success = mongodb_functions.update_user_field(self.login, field_key, new_val)
            
            if success:
                messagebox.showinfo("Success", f"{field_key} updated successfully!")
            else:
                messagebox.showwarning("Warning", "Saved locally, but database update failed.")

    def logout(self):
        """Логіка виходу"""
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            session.current_user = None # Очищаємо сесію
            # Припускаємо, що у вас є такий метод у контролері або треба перезапустити App
            # self.controller.show_login_screen() 
            print("Logged out")
            session.current_user = None
            self.controller.switch_frame(LoginView)

    def import_user_icon(self):
        # Тут ваш код, я лише додав try/except
        path = "Data/Images/user_icon" # Перевірте розширення
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as text_file:
                base64_string = text_file.read()
            binary_data = base64.b64decode(base64_string)
            image_stream = io.BytesIO(binary_data)
            pil_image = Image.open(image_stream)
            pil_image.thumbnail((100, 100)) # Трохи більше для профілю
            return ImageTk.PhotoImage(pil_image)
        except Exception as e:
            print(f"Icon error: {e}")
            return None
        
    def open_history_window(self):
        OrdersHistoryWindow(self, self.controller)