from pymongo import MongoClient
from datetime import datetime
from config import Config

# Inisialisasi koneksi MongoDB
client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

# Contoh operasi database
def tambah_data(data):
    collection = db["air-quality"]
    data['timestamp'] = datetime.now()
    result = collection.insert_one(data)
    return str(result.inserted_id)

def ambil_semua_data():
    collection = db["air-quality"]
    data = list(collection.find({}))
    # Konversi ObjectId ke string
    for item in data:
        item["_id"] = str(item["_id"])
    return data