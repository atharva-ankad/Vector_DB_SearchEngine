from pymongo.operations import SearchIndexModel
from core.db_client import mongo_client
from core.config import settings

def create_vector_index():
    collection = mongo_client.get_collection()
    
    print(f"🏗️  Requesting Vector Index creation: '{settings.VECTOR_INDEX_NAME}'...")

    # 1. The Index Definition
    # This JSON payload tells mongot exactly how to structure the graph.
    definition = {
        "fields": [
            {
                "type": "vector",
                "path": "vector",           # The field in our documents
                "numDimensions": 384,       # Must match our Embedder (all-MiniLM-L6-v2)
                "similarity": "cosine"      # The math to use for distance
            }
        ]
    }

    # 2. The Model Object
    # We explicitly specify type="vectorSearch" (Critical for v8.0+)
    model = SearchIndexModel(
        definition=definition,
        name=settings.VECTOR_INDEX_NAME,
        type="vectorSearch" 
    )

    try:
        # 3. Send the Command
        # This tells mongot to start indexing in the background.
        result = collection.create_search_index(model)
        
        print(f"✅ Index creation initiated! Name: {result}")
        print("⏳ Note: Indexing happens asynchronously. Wait ~10-20 seconds before searching.")
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        print("--> Common Setup Issue: Ensure your 'mongot' process is running and connected to this replica set.")

if __name__ == "__main__":
    # Ensure you have defined VECTOR_INDEX_NAME = "vector_index" in core/config.py first!
    create_vector_index()