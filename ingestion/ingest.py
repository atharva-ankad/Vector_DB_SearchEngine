import os
from ingestion.parser import PDFParser
from ingestion.chunker import ChunkProcessor
from ingestion.embedder import Embedder
from core.db_client import mongo_client

class IngestionPipeline:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def run(self):
        print(f"🚀 Starting Ingestion for: {self.pdf_path}")
        
        # --- Step 1: Extraction ---
        if not os.path.exists(self.pdf_path):
            print(f"❌ Error: File not found at {self.pdf_path}")
            return

        print("1️⃣  Parsing PDF...")
        parser = PDFParser(self.pdf_path)
        pages = parser.extract()
        if not pages:
            print("❌ No text found in PDF. Stopping.")
            return

        # --- Step 2: Chunking ---
        print("2️⃣  Chunking text...")
        chunker = ChunkProcessor()
        chunks = chunker.process(pages)
        
        # --- Step 3: Embedding ---
        print("3️⃣  Generating Embeddings (This uses the CPU)...")
        embedder = Embedder()
        # This adds the "vector" field to our chunk dictionaries
        chunks_with_vectors = embedder.embed_chunks(chunks)

        # --- Step 4: Storage (The Load) ---
        print("4️⃣  Saving to MongoDB...")
        collection = mongo_client.get_collection()
        
        # CRITICAL: For this learning project, we clear the DB first 
        # so we don't get duplicate answers every time we run the script.
        # In production, you would check if the file already exists.
        deleted = collection.delete_many({})
        print(f"🧹 Cleared {deleted.deleted_count} old documents.")

        # Bulk Insert
        # MongoDB is very fast at inserting lists of dictionaries.
        result = collection.insert_many(chunks_with_vectors)
        
        print(f" Success! Inserted {len(result.inserted_ids)} chunks into the Knowledge Base.")
        print(" Pipeline Complete.")

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    # Point this to your file
    PDF_FILE = "data/pdfs/sample.pdf"
    
    pipeline = IngestionPipeline(PDF_FILE)
    pipeline.run()