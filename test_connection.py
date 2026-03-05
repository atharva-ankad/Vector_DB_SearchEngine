from core.db_client import mongo_client

# This should trigger the connect() method automatically
# because get_collection calls connect() if it's null.
collection = mongo_client.get_collection()

# Let's try to insert a dummy document to prove we have write access
try:
    sample_doc = {"name": "Test Connection", "status": "Active"}
    result = collection.insert_one(sample_doc)
    print(f" Inserted document with ID: {result.inserted_id}")
    
    # Clean up (delete it so we don't mess up the DB)
    collection.delete_one({"_id": result.inserted_id})
    print(" Cleaned up test document.")
    
except Exception as e:
    print(f"❌ Error during write test: {e}")

# Close connection
mongo_client.close()