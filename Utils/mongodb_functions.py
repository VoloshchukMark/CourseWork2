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

# ==========================================
# USER & AUTH FUNCTIONS
# ==========================================

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
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$"
    if re.match(pattern, password):
        return True
    else:
        return False
    
def hash_password(password):
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

def get_user_info(login):
    try:
        user_info = mongodb_connection.users_collection.find_one({"login": login})
        return user_info
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def update_user_field(login, field_name, new_value):
    try:
        result = mongodb_connection.users_collection.update_one(
            {"login": login},             
            {"$set": {field_name: new_value}} 
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

# ==========================================
# GENERAL DATABASE FUNCTIONS
# ==========================================

def upload_to_db(collection_name, doc):
    try:
        mongodb_connection.db[collection_name].insert_one(doc)
        return True
    except Exception as e:
        print(f"Database Insert Error: {e}")
        return False

# !!! ВИПРАВЛЕНО: Змінив назву на get_all_documents (як у MyOrdersView) і виправив помилку find()
def get_all_documents(collection_name):
    try:
        # Раніше тут було .find(collection_name), що викликало помилку "filter must be dict"
        documents = list(mongodb_connection.db[collection_name].find({})) 
        print(f"Successfully retrieved {len(documents)} documents from {collection_name}")
        return documents
    except Exception as e:
        print(f"Database Fetch Error: {e}")
        return []
    
def get_documents_paginated(collection_name, query=None, sort=None, skip=0, limit=12, projection=None):
    try:
        collection = mongodb_connection.db[collection_name] 

        if query is None:
            query = {}
        
        cursor = collection.find(query, projection)

        if sort:
            cursor = cursor.sort(sort)
        
        cursor = cursor.skip(skip).limit(limit)
        
        return list(cursor)
    except Exception as e:
        print(f"Error fetching filtered data: {e}")
        return []

def delete_document(collection_name, doc_id):
    try:
        collection = mongodb_connection.db[collection_name]
        collection.delete_one({"_id": doc_id})
        return True
    except Exception as e:
        print(f"Delete error: {e}")
        return False

# !!! ВАЖЛИВО: ОНОВЛЕНА ФУНКЦІЯ !!!
def update_document(collection_name, query, update_data):
    """
    Оновлює документ у колекції. Безпечна версія.
    """
    try:
        collection = mongodb_connection.db[collection_name]
        
        # 1. Перевірка: чи query це словник? (Це виправляло твою помилку)
        if not isinstance(query, dict):
            print(f"UPDATE ERROR: 'query' must be a dictionary (e.g. {{'_id': ...}}), but got {type(query)}")
            return False

        # 2. Перевірка: чи update_data це словник?
        if not isinstance(update_data, dict):
             print(f"UPDATE ERROR: 'update_data' must be a dictionary (e.g. {{'$set': ...}})")
             return False

        # 3. Виконання запиту
        result = collection.update_one(query, update_data)
        
        if result.matched_count > 0:
            return True
        else:
            print(f"No document found matching query: {query}")
            return False

    except Exception as e:
        print(f"Database Update Exception: {e}")
        return False

# ==========================================
# SPECIFIC LOGIC (Suppliers, etc)
# ==========================================

def get_fabric_supply_amount_(fabric_supplier_id):
    try:
        # Увага: count тут - це властивість, а не метод у старих версіях, але count_documents краще
        count = mongodb_connection.fabric_collection.count_documents({"fabric_supplier_id": fabric_supplier_id})
        return count
    except Exception as e:
        print(f"Error!: {e}")
        return 0

def get_suppliers_paginated(skip, limit):
    pipeline = [
        {"$sort": {"_id": 1}},
        {"$skip": skip},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "fabrics",                
                "localField": "_id",              
                "foreignField": "fabric_supplier_id", 
                "as": "related_fabrics"           
            }
        },
        {
            "$project": {
                "_id": 1,
                "name": 1,
                "number": 1,
                "fabric_supply_amount": {"$size": "$related_fabrics"} 
            }
        }
    ]
    return list(mongodb_connection.suppliers_collection.aggregate(pipeline))

def increment_supplier_fabric_count(supplier_id):
    try:
        result = mongodb_connection.suppliers_collection.update_one(
            {"_id": supplier_id},       
            {"$inc": {"fabric_supply_amount": 1}} 
        )
        if result.modified_count > 0:
            print(f"Updated supplier {supplier_id} supply count.")
        else:
            print(f"Supplier {supplier_id} not found or count not updated.")   
    except Exception as e:
        print(f"Error updating supplier count: {e}")

def get_orders_by_login(user_login):
    """Отримує всі замовлення для конкретного логіна користувача"""
    try:
        # Сортуємо: спочатку новіші (за _id, бо він містить час створення)
        cursor = mongodb_connection.orders_collection.find(
            {"customer_login": user_login}
        ).sort("_id", -1)
        
        return list(cursor)
    except Exception as e:
        print(f"Error getting user orders: {e}")
        return []

def process_fabric_usage(fabric_names_list):
    """
    Зменшує метраж тканин на 1.
    Якщо метраж стає <= 0, змінює статус in_stock на False.
    """
    collection = mongodb_connection.db["fabrics"]
    
    count_updated = 0
    
    for name in fabric_names_list:
        try:
            # 1. Знаходимо тканину за назвою (шукаємо по всіх можливих полях)
            query = {
                "$or": [
                    {"fabric_name": name},
                    {"name": name},
                    {"title": name}
                ]
            }
            fabric = collection.find_one(query)
            
            if fabric:
                # Отримуємо поточний метраж (безпечно конвертуємо в float)
                current_width = float(fabric.get("width_in_meters", 0) or 0)
                
                # Віднімаємо 1 метр (або стільки, скільки треба на 1 виріб)
                new_width = current_width - 1
                
                # Формуємо оновлення
                update_fields = {"width_in_meters": new_width}
                
                # Якщо тканини не лишилося - ставимо статус "Немає в наявності"
                if new_width <= 0:
                    update_fields["in_stock"] = False
                    print(f"DEBUG: Fabric '{name}' is now OUT OF STOCK.")
                
                # Записуємо в БД
                collection.update_one({"_id": fabric["_id"]}, {"$set": update_fields})
                count_updated += 1
                
        except Exception as e:
            print(f"Error processing fabric '{name}': {e}")
            
    print(f"DEBUG: Processed usage for {count_updated} fabrics.")
    return True