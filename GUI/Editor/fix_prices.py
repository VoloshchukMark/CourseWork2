import pymongo
# Імпортуйте ваші налаштування підключення, якщо треба
from Utils import mongodb_connection 


collection = mongodb_connection.db["models"]

# Знаходимо всі документи, де price - це рядок (type 2 in MongoDB BSON)
cursor = collection.find({"price": {"$type": "string"}})

count = 0
for doc in cursor:
    try:
        # Беремо старе значення (рядок)
        str_price = doc["price"]
        # Робимо число
        float_price = float(str_price)
        
        # Оновлюємо документ
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"price": float_price}}
        )
        count += 1
        print(f"Виправлено модель: {doc.get('model_name')}")
    except ValueError:
        print(f"Не вдалося конвертувати ціну для: {doc.get('model_name')}")

print(f"Всього оновлено {count} документів.")