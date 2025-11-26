import sys
import os
import tkinter as tk
from tkinter import messagebox

# Ваші утиліти
from Utils import mongodb_functions
from Utils import tkinter_general
from GUI.Authentication import registration 
from GUI.Authentication import forgot_password 
from GUI.MainMenu import main_frame
from Utils import session
from Actors.User import User

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)


class LoginView(tk.Frame):
    def __init__(self, parent, controller):
        # Ініціалізуємо фрейм і задаємо фоновий колір
        super().__init__(parent, bg="#e6ccff")
        self.controller = controller
        
        # Налаштовуємо параметри ГОЛОВНОГО вікна через контролер
        self.controller.title("Login")
        self.controller.resizable(False, False)
        # Центруємо вікно (якщо у вас є ця функція)
        tkinter_general.center_window(self.controller, 500, 700)

        # Запускаємо створення інтерфейсу
        self.create_widgets()
        self.setup_bindings()

    def create_widgets(self):
        # 1. Заголовок (кріпиться до self, тобто до цього фрейму)
        self.title_Label = tk.Label(self, text="Login Screen", font=("Arial", 16), bg="#e6ccff", fg="purple")
        self.title_Label.pack(pady=20)

        # 2. Фрейм вводу
        self.login_input_Frame = tk.Frame(self, width=400, height=600, bg="white")
        self.login_input_Frame.pack_propagate(False) # Важливо: pack_propagate
        self.login_input_Frame.pack()

        # Елементи всередині фрейму
        self.login_Label = tk.Label(self.login_input_Frame, text="Login", bg="white", font=("Arial", 12))
        self.login_Entry = tk.Entry(self.login_input_Frame, font=("Arial", 12))
        
        self.password_Label = tk.Label(self.login_input_Frame, text="Password", bg="white", font=("Arial", 12))
        self.password_Entry = tk.Entry(self.login_input_Frame, show="*", font=("Arial", 12))
        
        self.hint_Label = tk.Label(self.login_input_Frame, 
                                   text="*password must contain at least 8 characters, one small and one capital letter, one digit", 
                                   bg="white", font=("Arial", 8), fg="white", 
                                   justify="left", wraplength=300)

        self.enter_Button = tk.Button(self.login_input_Frame, text="Enter", justify=tk.CENTER, 
                                      width=20, font=("Arial", 14), bg="#b366ff", fg="white", 
                                      activebackground="#cc80ff", activeforeground="white", 
                                      command=self.handle_login)

        # Розміщення елементів (pack)
        self.login_Label.pack(anchor='w', padx=20, pady=(20, 0))
        self.login_Entry.pack(padx=20, pady=(0, 20), fill=tk.X)
        self.password_Label.pack(anchor='w', padx=20, pady=(0, 0))
        self.password_Entry.pack(padx=20, pady=(0, 0), fill=tk.X)
        self.hint_Label.pack(anchor='w', padx=20, pady=(0, 20))
        self.enter_Button.pack()

        # 3. Footer (Підвал)
        self.footer_Frame = tk.Frame(self.login_input_Frame, bg="white")
        self.footer_Frame.pack(pady=(0, 0))

        self.forgotPassword_Button = tk.Button(self.footer_Frame, text="Forgot Password?", justify=tk.CENTER, 
                                               width=20, font=("Arial", 10), bg="white", fg="#a6a6a6", 
                                               borderwidth=0, highlightthickness=0, activebackground="white", 
                                               activeforeground="#737373", command=self.handle_forgot_password)
        self.forgotPassword_Button.pack(side=tk.TOP, pady=(0, 10))

        self.not_signed_up_Label = tk.Label(self.footer_Frame, text="Don't have an account?", 
                                            bg="white", font=("Arial", 10), fg="#a6a6a6")
        self.not_signed_up_Label.pack(side=tk.LEFT)

        self.not_signed_up_Button = tk.Button(self.footer_Frame, text="Make an account", justify=tk.CENTER, 
                                              width=20, font=("Arial", 10), bg="white", fg="#d280ff", 
                                              borderwidth=0, highlightthickness=0, activebackground="white", 
                                              activeforeground="#a600ff", command=self.handle_registration)
        self.not_signed_up_Button.pack(side=tk.RIGHT)

    def setup_bindings(self):
        # Прив'язуємо події фокусу
        self.password_Entry.bind("<FocusOut>", self.on_focus_out)
        self.password_Entry.bind("<FocusIn>", self.on_focus_in)
        self.password_Entry.bind("<Return>", self.on_enter_button_press)

        self.login_Entry.bind("<Return>", self.on_enter_button_press)
        
        self.login_Entry.bind("<Button-1>", self.keep_focus)
        self.password_Entry.bind("<Button-1>", self.keep_focus)

        # Прив'язуємо скидання фокусу (звертаємось до self та self.controller)
        self.login_input_Frame.bind("<Button-1>", self.dismiss_focus)
        
        # Біндимо на сам фрейм сторінки
        self.bind("<Button-1>", self.dismiss_focus)
        
        self.login_Label.bind("<Button-1>", self.dismiss_focus)
        self.password_Label.bind("<Button-1>", self.dismiss_focus)
        self.hint_Label.bind("<Button-1>", self.dismiss_focus)

    # --- ЛОГІКА ---

    def handle_login(self):
        entered_login = self.login_Entry.get()
        entered_password = self.password_Entry.get()
        
        if mongodb_functions.verify_password(entered_login, entered_password):
            active_user = User(login=entered_login, access="user")
            active_user.import_info()
            session.current_user = active_user
            messagebox.showinfo("Успіх", "Вхід успішний!")
            self.controller.switch_frame(main_frame.MainFrameView)
        else:
            messagebox.showerror("Помилка", "Невірний логін або пароль.")

    def handle_registration(self):
        self.controller.switch_frame(registration.RegisterView)

    def handle_forgot_password(self):
        self.controller.switch_frame(forgot_password.ForgotPasswordView)

    def on_focus_out(self, event):
        password = self.password_Entry.get()
        if not password:
             return 

        if mongodb_functions.is_password_valid(password):
            self.hint_Label.config(fg="white") 
            self.enter_Button.config(state="normal", bg="#b366ff")
        else:
            self.hint_Label.config(fg="red")
            self.enter_Button.config(state="disabled", bg="grey")

    def on_focus_in(self, event):
        self.hint_Label.config(fg="white")

    def keep_focus(self, event):
        event.widget.focus_set()
        return "break"

    def dismiss_focus(self, event):
        # Фокус переводимо на ГОЛОВНЕ вікно
        self.controller.focus_set()
    
    def on_enter_button_press(self, event):
        print(f"Кнопку натиснуто у віджеті")
        if event.widget == self.login_Entry:
            self.password_Entry.focus_set()
        elif event.widget == self.password_Entry:
            self.handle_login()

    