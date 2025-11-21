import pymongo
from pymongo import MongoClient

# Підключення (Ваш рядок з паролем)
# Використовуємо try-except для безпеки, щоб код не падав, якщо нема інтернету
try:
    cluster = MongoClient("mongodb+srv://voloshchukmark:cipmbinjBINJ228@courseproject.xogedrt.mongodb.net/")
    db = cluster["mongodbVSCodePlaygroundDB"]
    users_collection = db["users"]
    print("Підключення до БД успішне!")
except Exception as e:
    print(f"Помилка підключення: {e}")

def add_user_to_db(name, number, done):
    user_doc = {
        "name": name,
        "number": number,
        "done": done
    }
    try:
        users_collection.insert_one(user_doc)
        print(f"Користувача {name} збережено в MongoDB.")
        return True  # Повертаємо True, якщо все ок
    except Exception as e:
        print(f"Помилка запису: {e}")
        return False

def get_all_users():
    try:
        users = list(users_collection.find())
        return users
    except Exception as e:
        print(f"Помилка читання: {e}")
        return []