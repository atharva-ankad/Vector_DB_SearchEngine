import numpy as np
from core.db_client import mongo_client
from ingestion.embedder import Embedder

class VectorRetriever:
    def __init__(self):
        """
        Initializes the Retriever.
        It needs the same Embedder model to convert questions into numbers.
        """
        self.embedder = Embedder()
        self.collection = mongo_client.get_collection()

    def retrieve(self, query, top_k=5):
        """
        The Main Search Function.
        
        Args:
            query (str): The user's question.
            top_k (int): How many results to return (default 5).
            
        Returns:
            list: The top_k most relevant chunks.
        """
        print(f"🔍 Searching for: '{query}'")
        
        # 1. Embed the Query
        # We turn the question "What is the pressure?" into a vector.
        query_vector = self.embedder.model.encode(query)
        
        # 2. Fetch All Vectors from MongoDB
        # We get the ID, Text, and Vector for every chunk.
        # In production, you would use a Vector Index here to avoid fetching everything.
        cursor = self.collection.find({}, {"vector": 1, "text": 1, "metadata": 1})
        all_chunks = list(cursor)
        
        if not all_chunks:
            print("⚠️  Database is empty.")
            return []
            
        # 3. Prepare the Math (Numpy Magic)
        # We extract just the vectors into a big matrix.
        # shape: (num_chunks, 384)
        doc_vectors = [chunk['vector'] for chunk in all_chunks]
        doc_vectors = np.array(doc_vectors)
        
        # 4. Calculate Cosine Similarity
        # Formula: (A . B) / (|A| * |B|)
        # Since our model (all-MiniLM) produces "normalized" vectors (length = 1),
        # we can skip the division! We just need the Dot Product.
        # This one line calculates the score for EVERY chunk instantly.
        scores = np.dot(doc_vectors, query_vector)
        
        # 5. Sort and Get Top K
        # np.argsort gives us the indices of the sorted scores (lowest to highest).
        # We start from the end [::-1] to get highest scores first.
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        print("\n--- TOP RESULTS ---")
        for idx in top_indices:
            chunk = all_chunks[idx]
            score = scores[idx]
            
            # Add the score to the result so we can see how confident it is
            chunk['score'] = float(score) 
            results.append(chunk)
            
            print(f"Confidence: {score:.4f} | Page: {chunk.get('metadata', {}).get('page')}")
            print(f"Text: {chunk['text'][:100]}...\n")
            
        return results

# --- TEST BLOCK ---
if __name__ == "__main__":
    retriever = VectorRetriever()
    
    # Try a question that is RELEVANT to your PDF
    # CHANGE THIS to something that exists in your specific PDF
    question = "What is the summary of this document?" 
    
    retriever.retrieve(question)