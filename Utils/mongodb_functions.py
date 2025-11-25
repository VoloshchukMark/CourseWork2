import sys
import os
from pymongo import MongoClient, ReturnDocument
from Utils import mongodb_connection
import re
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
ph = PasswordHasher()
from tkinter import messagebox
from bson.binary import Binary

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def add_user_to_db(login, password):
    if not is_password_valid(password):
        print("Пароль не відповідає вимогам безпеки.")
        return False
    user_doc = {
        "_id": get_next_sequence("user_id"),
        "login": login,
        "password": hash_password(password),
        "access_right": "user"
    

    }
    try:
        mongodb_connection.keys_collection.insert_one(user_doc)
        print(f"Користувача {login} збережено в MongoDB.")
        return True  
    except Exception as e:
        print(f"Помилка запису: {e}")
        return False

def get_all_keys_connection():
    try:
        keys_connection = list(mongodb_connection.keys_collection.find())
        return keys_connection
    except Exception as e:
        print(f"Помилка читання: {e}")
        return []
    
def get_next_sequence(sequence_name):

    counter = mongodb_connection.counters_collection.find_one_and_update(
        {'_id': sequence_name},        
        {'$inc': {'sequence_value': 1}}, 
        upsert=True,                
        return_document=ReturnDocument.AFTER 
    )
    
    return counter['sequence_value']

def is_password_valid(password):
    # Розшифровка регулярного виразу:
    # ^              - початок рядка
    # (?=.*[a-z])    - має бути хоча б одна маленька літера
    # (?=.*[A-Z])    - має бути хоча б одна велика літера
    # (?=.*\d)       - має бути хоча б одна цифра
    # (?=.*[@$!%*?&]) - (Опціонально) хоча б один спецсимвол
    # .{8,}          - будь-які символи, мінімум 8 штук
    # $              - кінець рядка
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    
    if re.match(pattern, password):
        return True
    else:
        return False
    
def hash_password(password):
    """
    Приймає звичайний пароль (наприклад, 'admin123').
    Повертає зашифрований рядок (хеш).
    """
    return ph.hash(password)

def verify_password(entered_login, plain_password_input):
    user_doc = mongodb_connection.keys_collection.find_one({"login": entered_login})
    if not user_doc:
        return False
    try:
        ph.verify(user_doc['password'], plain_password_input)
        
        return True
    except VerifyMismatchError:
        return False

def uptade_password(entered_login, password):
    user_doc = mongodb_connection.keys_collection.find_one({"login": entered_login})
    if not user_doc:
        return False
    try:
        hashed_password = hash_password(password)
        mongodb_connection.keys_collection.update_one({"login": entered_login}, {"$set": {"password": hashed_password}})

        return True
    except:
        return False
    
def get_user(entered_login):
    if entered_login:
        if mongodb_connection.keys_collection.find_one({"login": entered_login}):
            return True
        else:
            messagebox.showerror("Error", "No user with such Login!")
            return False

def upload_to_db(collection, doc):
    if collection and collection == "models":
        try:
            mongodb_connection.models_collection.insert_one(doc)
            messagebox.showinfo("Success", "Model information has been added to the database.")
            return True
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to insert model info: {e}")
            return False
    elif collection and collection == "fabrics":
        try:
            mongodb_connection.fabric_collection.insert_one(doc)
            messagebox.showinfo("Success", "Fabric information has been added to the database.")
            return True
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to insert fabric info: {e}")
            return False
        
def get_documents_paginated(collection_name, skip, limit, projection=None):
    """
    Отримує список документів з пагінацією.
    skip: скільки записів пропустити
    limit: скільки записів взяти
    """
    try:
        collection = mongodb_connection.db[collection_name]
        cursor = collection.find({}, projection).skip(skip).limit(limit)
        return list(cursor)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []