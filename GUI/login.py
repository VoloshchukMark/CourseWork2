import sys
import os

from Utils import mongodb_functions
from Utils import tkinter_general
from GUI import collection
from GUI import registration

import tkinter as tk
from tkinter import messagebox, filedialog, ttk


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

login_window = tk.Tk()

def open_login_window():
    def handle_login():
        entered_login = login_Entry.get()
        entered_password = password_Entry.get()
        
        if mongodb_functions.verify_password(entered_login, entered_password):
            messagebox.showinfo("Успіх", "Вхід успішний!")
            login_window.destroy()
            collection.open_collection_window()
        else:
            messagebox.showerror("Помилка", "Невірний логін або пароль.")

    def handle_registration():
        is_registered = registration.open_registration_window(login_window)
        if is_registered:
            messagebox.showinfo("Успіх", "Реєстрація успішна!")
            login_window.destroy()
            collection.open_collection_window()


    def on_focus_out(event):
        password = password_Entry.get()
        if not password:
             return 

        if mongodb_functions.is_password_valid(password):
            hint_Label.config(fg="white") 
            enter_Button.config(state="normal", bg="#b366ff")
        else:
            hint_Label.config(fg="red")
            enter_Button.config(state="disabled", bg="grey")

    def on_focus_in(event):
        hint_Label.config(fg="white")
    
    login_window.title("Login")
    tkinter_general.center_window(login_window, 500, 700)
    login_window.configure(bg="#e6ccff")
    login_window.resizable(False, False)

    title_Label = tk.Label(login_window, text="Login Screen", font=("Arial", 16), bg="#e6ccff", fg="purple")

    login_input_Frame = tk.Frame(login_window, width=400, height=600, bg="white")
    login_input_Frame.propagate(False)
    login_Label = tk.Label(login_input_Frame, text="Login", bg="white", font=("Arial", 12))
    login_Entry = tk.Entry(login_input_Frame, font=("Arial", 12))
    password_Label = tk.Label(login_input_Frame, text="Password", bg="white", font=("Arial", 12))

    password_Entry = tk.Entry(login_input_Frame, show="*", font=("Arial", 12))
    password_Entry.bind("<FocusOut>", on_focus_out)
    password_Entry.bind("<FocusIn>", on_focus_in)

    hint_Label = tk.Label(login_input_Frame, text="*password must contain at least 8 characters, one small and one capital letter, one digit", bg="white", font=("Arial", 8), fg="white", justify="left", wraplength=300)
    enter_Button = tk.Button(login_input_Frame, text="Enter", justify=tk.CENTER, width=20, font=("Arial", 14), bg="#b366ff", fg="white", activebackground="#cc80ff", activeforeground="white", command=handle_login)

    footer_Frame = tk.Frame(login_input_Frame, bg="white")
    forgotPassword_Button = tk.Button(footer_Frame, text="Forgot Password?", justify=tk.CENTER, width=20, font=("Arial", 10), bg="white", fg="#a6a6a6", borderwidth=0, highlightthickness=0, activebackground="white", activeforeground="#737373")
    not_signed_up_Label = tk.Label(footer_Frame, text="Don't have an account?", bg="white", font=("Arial", 10), fg="#a6a6a6")
    not_signed_up_Button = tk.Button(footer_Frame, text="Make an account", justify=tk.CENTER, width=20, font=("Arial", 10), bg="white", fg="#d280ff", borderwidth=0, highlightthickness=0, activebackground="white", activeforeground="#a600ff", command=handle_registration)

    title_Label.pack(pady=20)
    login_input_Frame.pack()
    login_Label.pack(anchor='w', padx=20, pady=(20, 0))
    login_Entry.pack(padx=20, pady=(0, 20), fill=tk.X)
    password_Label.pack(anchor='w', padx=20, pady=(0, 0))
    password_Entry.pack(padx=20, pady=(0, 0), fill=tk.X)
    hint_Label.pack(anchor='w', padx=20, pady=(0, 20))
    enter_Button.pack()

    footer_Frame.pack()
    forgotPassword_Button.pack(side=tk.BOTTOM, pady=(0, 10))
    not_signed_up_Label.pack(side=tk.LEFT)
    not_signed_up_Button.pack(side=tk.RIGHT)

    def keep_focus(event):
        event.widget.focus_set()
        return "break"
    
    login_Entry.bind("<Button-1>", keep_focus)
    password_Entry.bind("<Button-1>", keep_focus)

    def dismiss_focus(event):
        login_window.focus_set()

    login_input_Frame.bind("<Button-1>", dismiss_focus) 
    login_window.bind("<Button-1>", dismiss_focus)
    
    login_Label.bind("<Button-1>", dismiss_focus)
    password_Label.bind("<Button-1>", dismiss_focus)
    hint_Label.bind("<Button-1>", dismiss_focus)

    login_window.mainloop()