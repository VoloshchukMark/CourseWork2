import sys
import os

from Utils import mongodb_functions
from Utils import tkinter_general

import tkinter as tk
from tkinter import messagebox, filedialog, ttk


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)


def open_registration_window(parent):
    registration_status = {"success": False}

    def handle_registration():
        mongodb_functions.add_user_to_db(username_Entry.get(), password_Entry.get())
        registration_status["success"] = True
        registration_window.destroy()
    
    def handle_back():
        registration_window.destroy()

    def on_focus_out(event):
            if event.widget == password_Entry:
                password = password_Entry.get()
                if not password:
                    return 

                if mongodb_functions.is_password_valid(password):
                    password_format_hint_Label.config(fg="white") 
                else:
                    password_format_hint_Label.config(fg="red")
            elif event.widget == repeat_password_Entry:
                password = password_Entry.get()
                repeat_password = repeat_password_Entry.get()
                if password != repeat_password:
                    password_match_hint_Label.config(fg="red")
                else:
                    password_match_hint_Label.config(fg="white") 

    def on_focus_in(event):
        if event.widget == password_Entry:
            password_format_hint_Label.config(fg="white")
        elif event.widget == repeat_password_Entry:
            password_match_hint_Label.config(fg="white")



    registration_window = tk.Toplevel(parent)
    registration_window.title("Registration")
    tkinter_general.center_window(registration_window, 500, 700)
    registration_window.configure(bg="#ccd1ff")
    registration_window.resizable(False, False)

    registration_window.grab_set()

    title_Label = tk.Label(registration_window, text="Login Screen", font=("Arial", 16), bg="#e6ccff", fg="purple")

    registration_Frame = tk.Frame(registration_window, width=400, height=600, bg="white")
    registration_Frame.propagate(False)
    username_Label = tk.Label(registration_Frame, text="Login", bg="white", font=("Arial", 12))
    username_Entry = tk.Entry(registration_Frame, font=("Arial", 12))

    password_Label = tk.Label(registration_Frame, text="Password", bg="white", font=("Arial", 12))
    password_Entry = tk.Entry(registration_Frame, show="*", font=("Arial", 12))
    password_Entry.bind("<FocusOut>", on_focus_out)
    password_Entry.bind("<FocusIn>", on_focus_in)
    password_format_hint_Label = tk.Label(registration_Frame, text="*password must contain at least 8 characters, " \
                                        "one small and one capital letter, one digit", bg="white", font=("Arial", 8),
                                        fg="white", justify="left", wraplength=300)

    repeat_password_Label = tk.Label(registration_Frame, text="Repeat Password", bg="white", font=("Arial", 12))
    repeat_password_Entry = tk.Entry(registration_Frame, show="*", font=("Arial", 12))
    repeat_password_Entry.bind("<FocusOut>", on_focus_out)
    repeat_password_Entry.bind("<FocusIn>", on_focus_in)
    password_match_hint_Label = tk.Label(registration_Frame, text="*passwords do not match!", bg="white", font=("Arial", 8),
                                        fg="white", justify="left", wraplength=300)

    enter_Button = tk.Button(registration_Frame, text="Enter", justify=tk.CENTER, width=20, font=("Arial", 14), bg="#b366ff", 
                             fg="white", activebackground="#cc80ff", activeforeground="white", command=handle_registration)

    back_Button = tk.Button(registration_Frame, text="Go back", justify=tk.CENTER, font=("Arial", 12), bg="white", 
                            fg="#a6a6a6", borderwidth=0, highlightthickness=0, activebackground="white", activeforeground="#737373", 
                            command=handle_back)

    title_Label.pack(pady=20)
    registration_Frame.pack()
    username_Label.pack(anchor='w', padx=20, pady=(20, 0))
    username_Entry.pack(padx=20, pady=(0, 20), fill=tk.X)
    password_Label.pack(anchor='w', padx=20, pady=(0, 0))
    password_Entry.pack(padx=20, pady=(0, 0), fill=tk.X)
    password_format_hint_Label.pack(anchor='w', padx=20, pady=(0, 20))
    repeat_password_Label.pack(anchor='w', padx=20, pady=(0, 0))
    repeat_password_Entry.pack(padx=20, pady=(0, 0), fill=tk.X)
    password_match_hint_Label.pack(anchor='w', padx=20, pady=(0, 20))
    enter_Button.pack()
    back_Button.pack(pady=10)

    def keep_focus(event):
        event.widget.focus_set()
        return "break"
    
    username_Entry.bind("<Button-1>", keep_focus)
    password_Entry.bind("<Button-1>", keep_focus)
    repeat_password_Entry.bind("<Button-1>", keep_focus)

    def dismiss_focus(event):
        registration_window.focus_set()

    registration_Frame.bind("<Button-1>", dismiss_focus) 
    registration_window.bind("<Button-1>", dismiss_focus)
    
    username_Label.bind("<Button-1>", dismiss_focus)
    password_Label.bind("<Button-1>", dismiss_focus)
    repeat_password_Label.bind("<Button-1>", dismiss_focus)
    password_format_hint_Label.bind("<Button-1>", dismiss_focus)
    password_match_hint_Label.bind("<Button-1>", dismiss_focus)


    registration_window.wait_window()

    return registration_status["success"]