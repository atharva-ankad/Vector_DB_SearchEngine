from sentence_transformers import SentenceTransformer
from core.config import settings

class Embedder:
    def __init__(self):
        """
        Initializes the Embedding Model.
        This might take a few seconds the first time because it downloads the model weights.
        """
        print(f" Loading Embedding Model: {settings.EMBEDDING_MODEL_NAME}...")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        print(" Model loaded successfully.")

    def embed_chunks(self, chunks):
        """
        Takes a list of Chunk dictionaries.
        Adds a "vector" field to each dictionary.
        
        Args:
            chunks (list): List of dicts with 'text' field.
            
        Returns:
            list: The same list, but now with vectors.
        """
        # 1. Extract just the text strings
        # The model needs a list of strings: ["text1", "text2", ...]
        texts = [chunk['text'] for chunk in chunks]
        
        # 2. Generate Embeddings
        # batch_size=32 means it processes 32 chunks at a time to save memory.
        # show_progress_bar=True helps us see it's working.
        vectors = self.model.encode(texts, batch_size=32, show_progress_bar=True)
        
        # 3. Attach vectors back to the chunk objects
        # The model returns Numpy arrays. We convert them to standard Python lists
        # because MongoDB stores lists, not Numpy arrays.
        for i, chunk in enumerate(chunks):
            chunk['vector'] = vectors[i].tolist()
            
        return chunks

# --- TEST BLOCK ---
if __name__ == "__main__":
    # Create a dummy chunk
    mock_chunks = [
        {"text": "This is a test sentence.", "metadata": {}},
        {"text": "Embeddings are cool.", "metadata": {}}
    ]
    
    embedder = Embedder()
    result = embedder.embed_chunks(mock_chunks)
    
    print("\n--- VECTOR PREVIEW ---")
    vector = result[0]['vector']
    print(f"Dimensions: {len(vector)}") # Should be 384
    print(f"First 5 numbers: {vector[:5]}")