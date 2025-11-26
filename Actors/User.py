import os, sys
from Utils import mongodb_functions
from tkinter import messagebox

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

class User:
    def __init__(self, login="Unknown", access="Unknown"):
        self.login = login
        self.username = "Unknown"
        self.email = "Unknown"
        self.number = "Unknown"
        self.access = access  # e.g., 'user', 'admin', 'operator'
    
    def edit_info(self, new_login="Unknown", new_username="Unknown", new_email="Unknown", new_number="Unknown", new_access="Unknown"):
        if new_login:
            self.login = new_login
        if new_username:
            self.username = new_username
        if new_email:
            self.email = new_email
        if new_number:
            self.number = int(new_number)
        if new_access:
            self.access = new_access

    def import_info(self):
        try:
            imported_user = mongodb_functions.get_user_info(self.login)
            if imported_user:
                self.username = imported_user.get("username", "Unknown")
                self.email = imported_user.get("email", "Unknown")
                self.number = imported_user.get("number", 0)
                self.access = imported_user.get("access", "user")
        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{e}")
            print(e)
    
    def create_user(self, login, access):
        self.user = User(login, access)

user = User