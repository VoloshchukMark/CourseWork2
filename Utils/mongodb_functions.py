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
        print("The password is not secure enough.")
        return False
    if mongodb_connection.users_collection.find_one({"login": login}) == login:
        print("User is already exists!")
        return False
    key_doc = {
        "_id": get_next_sequence("key_id"),
        "login": login,
        "password": hash_password(password),
        "access_right": "user"
    }
    user_doc = {
        "_id": get_next_sequence("user_id"),
        "login": login,
        "username": "User",
        "email": "Unknown",
        "number": 0000000000,
        "access": "user"
    }
    try:
        mongodb_connection.keys_collection.insert_one(key_doc)
        mongodb_connection.users_collection.insert_one(user_doc)
        print(f"The user {login} info has been saved successfuly in MongoDB.")
        return True  
    except Exception as e:
        print(f"Error: {e}")
        return False

def get_all_keys_connection():
    try:
        keys_connection = list(mongodb_connection.keys_collection.find())
        return keys_connection
    except Exception as e:
        print(f"Error: {e}")
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
    try:
        mongodb_connection.db[collection].insert_one(doc)
        messagebox.showinfo("Success", f"The {collection} information has been added to the database.")
        return True
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to insert info: {e}")
        return False
    
        
def get_documents_paginated(collection_name, query=None, sort=None, skip=0, limit=12, projection=None):
    """
    Отримує документи з фільтрацією та сортуванням.
    
    :param collection_name: Назва колекції ("models" або "fabrics")
    :param query: Словник фільтрів MongoDB (наприклад, {"price": {"$gt": 100}})
    :param sort: Список кортежів для сортування (наприклад, [("price", 1)])
    :param skip: Скільки пропустити
    :param limit: Скільки взяти
    :param projection: Які поля повертати
    """
    try:
        collection = mongodb_connection.db[collection_name] 

        if query is None:
            query = {}
        
        # Створюємо курсор із запитом
        cursor = collection.find(query, projection)

        # Застосовуємо сортування, якщо воно є
        if sort:
            cursor = cursor.sort(sort)
        
        # Застосовуємо пагінацію
        cursor = cursor.skip(skip).limit(limit)
        
        return list(cursor)
    except Exception as e:
        print(f"Error fetching filtered data: {e}")
        return []

def get_user_info(login):
    try:
        user_info = mongodb_connection.users_collection.find_one({"login": login})
        return user_info
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def update_user_field(login, field_name, new_value):
    """
    Оновлює одне поле користувача в базі даних.
    """
    try:
        result = mongodb_connection.users_collection.update_one(
            {"login": login},             # Фільтр (кого шукаємо)
            {"$set": {field_name: new_value}} # Оновлення (що міняємо)
        )
        
        if result.modified_count > 0:
            print(f"Successfully updated {field_name} for {login}")
            return True
        else:
            print("No document updated (maybe value was the same?)")
            return False
            
    except Exception as e:
        print(f"Error updating user: {e}")
        return False

def delete_document(collection_name, doc_id):
    try:
        collection = mongodb_connection.db[collection_name]
        # Перетворюємо на ObjectId, якщо потрібно, або залишаємо як є, якщо у вас int
        collection.delete_one({"_id": doc_id})
        return True
    except Exception as e:
        print(f"Delete error: {e}")
        return False

def update_document(collection_name, doc_id, new_data):
    try:
        collection = mongodb_connection.db[collection_name]
        # Видаляємо _id з new_data, щоб не намагатися його змінити (це заборонено)
        if "_id" in new_data:
            del new_data["_id"]
            
        collection.update_one({"_id": doc_id}, {"$set": new_data})
        return True
    except Exception as e:
        print(f"Update error: {e}")
        return False

def get_fabric_supply_amount_(fabric_supplier_id):
    try:
        amount_of_supply = list(mongodb_connection.fabric_collection.find_many({"fabric_supplier_id": fabric_supplier_id})).count
        return amount_of_supply
    except Exception as e:
        print(f"Error!: {e}")
        return None

def get_suppliers_paginated(skip, limit):
    """
    Повертає список виробників з пагінацією + підрахованою кількістю тканин.
    """
    pipeline = [
        # 1. Сортування (бажано, щоб порядок не стрибав при пагінації)
        {"$sort": {"_id": 1}},
        
        # 2. Пагінація (СПОЧАТКУ обрізаємо, потім рахуємо - це набагато швидше)
        {"$skip": skip},
        {"$limit": limit},

        # 3. З'єднання з тканинами (Lookup)
        {
            "$lookup": {
                "from": "fabrics",                # НАЗВА КОЛЕКЦІЇ ТКАНИН У БД
                "localField": "_id",              # ID виробника
                "foreignField": "fabric_supplier_id", # Поле зв'язку в тканинах
                "as": "related_fabrics"           # Тимчасовий масив
            }
        },

        # 4. Проекція (залишаємо потрібні поля і рахуємо довжину масиву)
        {
            "$project": {
                "_id": 1,
                "name": 1,
                "number": 1,
                "fabric_supply_amount": {"$size": "$related_fabrics"} # Рахуємо кількість
            }
        }
    ]
    
    return list(mongodb_connection.suppliers_collection.aggregate(pipeline))

def increment_supplier_fabric_count(supplier_id):
    """
    Знаходить виробника за _id і збільшує його поле fabric_supply_amount на 1.
    """
    try:
        # Увага: перевірте назву колекції ("tailors" або "suppliers")
        # У ваших файлах ви використовували "tailors" для постачальників.
        collection_name = "tailors" 
        
        result = mongodb_connection.suppliers_collection.update_one(
            {"_id": supplier_id},       # Умова пошуку
            {"$inc": {"fabric_supply_amount": 1}} # Оператор $inc збільшує значення
        )
        
        if result.modified_count > 0:
            print(f"Updated supplier {supplier_id} supply count.")
        else:
            print(f"Supplier {supplier_id} not found or count not updated.")
            
    except Exception as e:
        print(f"Error updating supplier count: {e}")