import sys
import os
import pymongo
from pymongo import MongoClient
from bson.binary import Binary

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Підключення (Ваш рядок з паролем)
# Використовуємо try-except для безпеки, щоб код не падав, якщо нема інтернету
try:
    cluster = MongoClient("mongodb+srv://voloshchukmark:cipmbinjBINJ228@courseproject.xogedrt.mongodb.net/")

    db = cluster["atelier_fashion"]

    keys_collection = db["keys"]
    counters_collection = db["counters"]
    models_collection = db["models"]
    fabric_collection = db["fabrics"]
    images_collection = db["images"]
    
    print("Підключення до БД успішне!")
except Exception as e:
    print(f"Помилка підключення: {e}")

