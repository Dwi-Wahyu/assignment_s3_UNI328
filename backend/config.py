import os
from dotenv import load_dotenv

# Load environment variables dari file .env
load_dotenv()

class Config:
    # Konfigurasi MongoDB
    MONGO_URI = os.getenv("MONGO_URI")  # Default: MongoDB lokal
    DB_NAME = os.getenv("DB_NAME")