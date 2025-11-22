import sys
import os
import pymongo
from pymongo import MongoClient

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Підключення (Ваш рядок з паролем)
# Використовуємо try-except для безпеки, щоб код не падав, якщо нема інтернету
try:
    cluster = MongoClient("mongodb+srv://voloshchukmark:cipmbinjBINJ228@courseproject.xogedrt.mongodb.net/")

    db = cluster["mongodbVSCodePlaygroundDB"]

    keys_collection = db["keys"]
    counters_collection = db["counters"]
    
    print("Підключення до БД успішне!")
except Exception as e:
    print(f"Помилка підключення: {e}")

