import sys
import os
import pymongo
from pymongo import MongoClient
from bson.binary import Binary

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

try:
    cluster = MongoClient("mongodb+srv://voloshchukmark:cipmbinjBINJ228@courseproject.xogedrt.mongodb.net/")

    db = cluster["atelier_fashion"]

    keys_collection = db["keys"]
    counters_collection = db["counters"]
    models_collection = db["models"]
    fabric_collection = db["fabrics"]
    images_collection = db["images"]
    users_collection = db["user"]
    orders_collection = db["orders"]
    suppliers_collection = db["suppliers"]
    
    print("The connection is successful!")
except Exception as e:
    print(f"Connection error: {e}")

