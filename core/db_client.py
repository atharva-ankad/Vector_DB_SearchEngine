from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from core.config import settings

class MongoDBClient:
    def __init__(self):
        # We start with everything as None (empty).
        # We don't connect immediately when the class is created 
        # because we want to control exactly WHEN the connection happens.
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        """
        Establishes the connection to MongoDB.
        """
        try:
            # 1. Create the Client (The "Phone")
            # We use the URL from our config file.
            print(f"🔌 Attempting to connect to MongoDB at: {settings.MONGO_URI}")
            self.client = MongoClient(settings.MONGO_URI)
            
            # 2. The Ping Test (The "Hello?")
            # Just creating the client doesn't actually touch the server.
            # We run a lightweight command ('ismaster') to force a check.
            self.client.admin.command('ismaster')
            
            # 3. Select the Database and Collection
            # acts like: use rag_db_v1
            self.db = self.client[settings.DB_NAME] 
            
            # acts like: db.createCollection('knowledge_base')
            self.collection = self.db[settings.COLLECTION_NAME]
            
            print(f"✅ Successfully connected to Database: {settings.DB_NAME}")
            print(f"✅ Using Collection: {settings.COLLECTION_NAME}")
            
        except ConnectionFailure:
            print("❌ CRITICAL ERROR: Could not connect to MongoDB.")
            print("   Is the MongoDB service running?")
            print("   (Run 'services.msc' on Windows or 'brew services' on Mac to check)")
            raise # Re-raise the error to stop the program

    def get_collection(self):
        """
        A helper method to get the collection.
        If we aren't connected yet, it connects automatically.
        """
        if self.collection is None:
            self.connect()
        return self.collection

    def close(self):
        """
        Closes the connection.
        """
        if self.client:
            self.client.close()
            print(" Connection closed.")

# --- THE SINGLETON INSTANCE ---
# We create ONE instance of this class here.
# Any other file that imports 'mongo_client' will share this same connection.
# This prevents opening 1000 connections if 1000 files need the DB.
mongo_client = MongoDBClient()