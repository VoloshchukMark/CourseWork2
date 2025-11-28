import sys
import os
import tkinter as tk
from tkinter import messagebox

from Utils import mongodb_functions
from Utils import mongodb_connection
from Utils import tkinter_general
from Utils import session
from GUI.Authentication import login
from Actors.User import User

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class RegisterView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ccd1ff")
        self.controller = controller

        # Налаштування головного вікна (змінюємо заголовок та розмір)
        self.controller.title("Registration")
        self.controller.resizable(False, False)
        tkinter_general.center_window(self.controller, 500, 700)

        self.create_widgets()
        self.setup_bindings()

    def create_widgets(self):
        # Заголовок
        self.title_Label = tk.Label(self, text="Registration Screen", font=("Arial", 16), bg="#ccd1ff", fg="purple")
        self.title_Label.pack(pady=20)

        # Основний білий фрейм
        self.registration_Frame = tk.Frame(self, width=400, height=600, bg="white")
        self.registration_Frame.pack_propagate(False) # Важливо: pack_propagate
        self.registration_Frame.pack()

        # --- Login (Username) ---
        self.username_Label = tk.Label(self.registration_Frame, text="Login", bg="white", font=("Arial", 12))
        self.username_Entry = tk.Entry(self.registration_Frame, font=("Arial", 12))

        # --- Password ---
        self.password_Label = tk.Label(self.registration_Frame, text="Password", bg="white", font=("Arial", 12))
        self.password_Entry = tk.Entry(self.registration_Frame, show="*", font=("Arial", 12))
        
        self.password_format_hint_Label = tk.Label(self.registration_Frame, 
                                                   text="*password must contain at least 8 characters, one small and one capital letter, one digit", 
                                                   bg="white", font=("Arial", 8),
                                                   fg="white", justify="left", wraplength=300)

        # --- Repeat Password ---
        self.repeat_password_Label = tk.Label(self.registration_Frame, text="Repeat Password", bg="white", font=("Arial", 12))
        self.repeat_password_Entry = tk.Entry(self.registration_Frame, show="*", font=("Arial", 12))
        
        self.password_match_hint_Label = tk.Label(self.registration_Frame, text="*passwords do not match!", 
                                                  bg="white", font=("Arial", 8),
                                                  fg="white", justify="left", wraplength=300)

        # --- Buttons ---
        self.enter_Button = tk.Button(self.registration_Frame, text="Enter", justify=tk.CENTER, width=20, 
                                      font=("Arial", 14), bg="#b366ff", fg="white", 
                                      activebackground="#cc80ff", activeforeground="white", 
                                      command=self.handle_registration)

        self.back_Button = tk.Button(self.registration_Frame, text="Go back", justify=tk.CENTER, 
                                     font=("Arial", 12), bg="white", fg="#a6a6a6", 
                                     borderwidth=0, highlightthickness=0, 
                                     activebackground="white", activeforeground="#737373", 
                                     command=self.handle_back)

        # --- Layout (Pack) ---
        self.username_Label.pack(anchor='w', padx=20, pady=(20, 0))
        self.username_Entry.pack(padx=20, pady=(0, 20), fill=tk.X)
        
        self.password_Label.pack(anchor='w', padx=20, pady=(0, 0))
        self.password_Entry.pack(padx=20, pady=(0, 0), fill=tk.X)
        self.password_format_hint_Label.pack(anchor='w', padx=20, pady=(0, 20))
        
        self.repeat_password_Label.pack(anchor='w', padx=20, pady=(0, 0))
        self.repeat_password_Entry.pack(padx=20, pady=(0, 0), fill=tk.X)
        self.password_match_hint_Label.pack(anchor='w', padx=20, pady=(0, 20))
        
        self.enter_Button.pack()
        self.back_Button.pack(pady=10)

    def setup_bindings(self):
        # Validation binds
        self.password_Entry.bind("<FocusOut>", self.check_password_format)
        self.password_Entry.bind("<FocusIn>", self.reset_format_hint)
        
        self.repeat_password_Entry.bind("<FocusOut>", self.check_password_match)
        self.repeat_password_Entry.bind("<FocusIn>", self.reset_match_hint)

        # Focus management binds
        self.username_Entry.bind("<Button-1>", self.keep_focus)
        self.password_Entry.bind("<Button-1>", self.keep_focus)
        self.repeat_password_Entry.bind("<Button-1>", self.keep_focus)

        # Dismiss focus binds (Background clicks)
        self.registration_Frame.bind("<Button-1>", self.dismiss_focus) 
        self.bind("<Button-1>", self.dismiss_focus) # self refers to the main colored frame
        
        self.username_Label.bind("<Button-1>", self.dismiss_focus)
        self.password_Label.bind("<Button-1>", self.dismiss_focus)
        self.repeat_password_Label.bind("<Button-1>", self.dismiss_focus)
        self.password_format_hint_Label.bind("<Button-1>", self.dismiss_focus)
        self.password_match_hint_Label.bind("<Button-1>", self.dismiss_focus)

    # --- LOGIC ---

    def handle_registration(self):
        login_val = self.username_Entry.get()
        pass_val = self.password_Entry.get()
        repeat_pass_val = self.repeat_password_Entry.get()

        # Можна додати додаткову перевірку перед відправкою в БД
        if not mongodb_functions.is_password_valid(pass_val):
            messagebox.showerror("Error", "Wrong password!")
            return
        
        if pass_val != repeat_pass_val:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        if mongodb_connection.keys_collection.find_one({"login": login_val}):
            messagebox.showerror("Error", "This user is already exists!")
            return

        # Додавання в БД
        mongodb_functions.add_user_to_db(login_val, pass_val)
        new_user = User(login=login_val, access="user")
        new_user.import_info()
        session.current_user = new_user
        
        messagebox.showinfo("Success", "The registration was successful! Back to Login.")
        
        # Перехід назад на Логін
        # Імпорт тут, щоб уникнути циклічної залежності
         
        self.controller.switch_frame(login.LoginView)

    def handle_back(self):
        # Повертаємось на сторінку логіну
        self.controller.switch_frame(login.LoginView)

    # --- Validation Helpers ---

    def check_password_format(self, event):
        password = self.password_Entry.get()
        if not password:
            return 
        
        if mongodb_functions.is_password_valid(password):
            self.password_format_hint_Label.config(fg="white") 
        else:
            self.password_format_hint_Label.config(fg="red")

    def check_password_match(self, event):
        password = self.password_Entry.get()
        repeat_password = self.repeat_password_Entry.get()
        
        if password != repeat_password:
            self.password_match_hint_Label.config(fg="red")
        else:
            self.password_match_hint_Label.config(fg="white") 

    def reset_format_hint(self, event):
        self.password_format_hint_Label.config(fg="white")

    def reset_match_hint(self, event):
        self.password_match_hint_Label.config(fg="white")

    # --- Focus Helpers ---

    def keep_focus(self, event):
        event.widget.focus_set()
        return "break"

    def dismiss_focus(self, event):
        self.controller.focus_set()