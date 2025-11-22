import sys
import os
import pymongo
from pymongo import MongoClient, ReturnDocument
from Utils import mongodb_connection
import re
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
ph = PasswordHasher()

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

def add_user_to_db(username, password):
    if not is_password_valid(password):
        print("Пароль не відповідає вимогам безпеки.")
        return False
    user_doc = {
        "_id": get_next_sequence("user_id"),
        "username": username,
        "password": hash_password(password),
        "access_right": "user"
    

    }
    try:
        mongodb_connection.keys_collection.insert_one(user_doc)
        print(f"Користувача {username} збережено в MongoDB.")
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
    
def hash_password(plain_password):
    """
    Приймає звичайний пароль (наприклад, 'admin123').
    Повертає зашифрований рядок (хеш).
    """
    return ph.hash(plain_password)

def verify_password(stored_hash, plain_password_input):
    """
    Перевіряє, чи підходить введений пароль до збереженого хешу.
    Повертає True, якщо пароль вірний, і False, якщо ні.
    """
    try:
        ph.verify(stored_hash, plain_password_input)
        
        return True
    except VerifyMismatchError:
        return False

