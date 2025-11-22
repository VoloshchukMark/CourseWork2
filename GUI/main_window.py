import tkinter as tk
from tkinter import messagebox
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from Utils import mongodb_connection  
from Utils import mongodb_functions

def handle_click():
    if mongodb_functions.add_user_to_db(login_Entry.get(), password_Entry.get()):
        clear_entries()
        refresh_user_list()
    pass



mainWindow = tk.Tk()  
mainWindow.title("MongoDB Data Viewer")
mainWindow.geometry("1000x800")

tk.Label(mainWindow, text="Login:").pack()
login_Entry = tk.Entry(mainWindow)
login_Entry.pack()

tk.Label(mainWindow, text="Password:").pack()
password_Entry = tk.Entry(mainWindow)
password_Entry.pack()

proceed_Button = tk.Button(mainWindow, text="Confirm", command=handle_click)
proceed_Button.pack(pady=10)

summarise_Button = tk.Button(mainWindow, text="Forgot the password?")
summarise_Button.pack(pady=10)

list_Text = tk.Text(mainWindow, height=30, width=100)
list_Text.pack()



def refresh_user_list():
    keys = mongodb_functions.get_all_keys_connection()
    list_Text.delete(1.0, tk.END)  # Очищаємо текстове поле
    for key in keys:
        list_Text.insert(tk.END, f"Username: {key['username']}, Password: {key['password']}\n")

def clear_entries():
    login_Entry.delete(0, tk.END)
    password_Entry.delete(0, tk.END)

refresh_user_list()


mainWindow.mainloop()