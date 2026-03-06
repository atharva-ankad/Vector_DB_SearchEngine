from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure
from core.config import settings

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        """
        Establishes the connection to MongoDB Atlas.
        """
        try:
            # 1. Create the Client
            print(f"🔌 Attempting to connect to MongoDB Atlas...")
            
            # UPDATED: Added server_api for Atlas stability
            self.client = MongoClient(settings.MONGO_URI, server_api=ServerApi('1'))
            
            # 2. The Ping Test (The "Hello?")
            # UPDATED: 'ping' is the modern command for Atlas
            self.client.admin.command('ping')
            
            # 3. Select the Database and Collection
            self.db = self.client[settings.DB_NAME]
            self.collection = self.db[settings.COLLECTION_NAME]
            
            print(f"✅ Successfully connected to Database: {settings.DB_NAME}")
            print(f"✅ Using Collection: {settings.COLLECTION_NAME}")
            
        except ConnectionFailure as e:
            print("❌ CRITICAL ERROR: Could not connect to MongoDB Atlas.")
            print(f"   Error details: {e}")
            print("   Check: 1. Your IP is whitelisted in Atlas.")
            print("          2. Your username/password in config.py is correct.")
            raise

    def get_collection(self):
        if self.collection is None:
            self.connect()
        return self.collection

    def close(self):
        if self.client:
            self.client.close()
            print("Connection closed.")

# --- THE SINGLETON INSTANCE ---
mongo_client = MongoDBClient()

# --- TEST BLOCK (Run this file directly to test connection) ---
if __name__ == "__main__":
    print("🧪 Testing MongoDB Atlas Connection...")
    try:
        # This triggers the connect() method
        col = mongo_client.get_collection()
        print("🎉 TEST PASSED: Connection object is ready!")
    except Exception as e:
        print("💥 TEST FAILED.")