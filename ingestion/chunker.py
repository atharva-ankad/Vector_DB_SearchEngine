from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.config import settings

class ChunkProcessor:
    def __init__(self):
        """
        Initializes the Splitter.
        We load the settings from our config file so we can change them easily later.
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
            # NEW: Explicit Priority List
            separators=[
                "\n\n", # 1. Paragraphs (Best)
                ". ",   # 3. Sentences (Better than just spaces!)
                "\n",   # 2. Line breaks (Okay)
                " ",    # 4. Words (Fallback)
                ""      # 5. Characters (Worst case)
            ]
        )

    def process(self, pages_content):
        """
        Takes a list of Page dictionaries (from Parser).
        Returns a list of Chunk dictionaries (ready for DB).
        """
        chunks = []
        
        for page in pages_content:
            # 1. The Heavy Lifting
            # The splitter takes the long string and returns a list of shorter strings.
            texts = self.text_splitter.split_text(page['text'])
            
            # 2. Wrapping Metadata
            # We don't just want strings; we want objects with IDs and sources.
            for i, text in enumerate(texts):
                # Create a unique ID for this chunk
                # Format: filename_pageNumber_chunkIndex
                # Example: sample.pdf_p1_0
                chunk_id = f"{page['source']}_p{page['page']}_{i}"
                
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": text,
                    # We keep the metadata! This is crucial for citations.
                    "metadata": {
                        "source": page['source'],
                        "page": page['page'],
                        "chunk_index": i
                    }
                })
                
        print(f"✅ Chunking Complete: Created {len(chunks)} chunks from {len(pages_content)} pages.")
        return chunks

# --- TEST BLOCK ---
if __name__ == "__main__":
    # We create MOCK data to test this file in isolation.
    # We pretend the Parser gave us this:
    mock_data = [
        {
            "page": 1, 
            "source": "test_manual.pdf", 
            "text": "This is a paragraph about safety. " * 20  # Repeat to make it long
        }
    ]
    
    chunker = ChunkProcessor()
    result = chunker.process(mock_data)
    
    # Verify the first chunk
    if result:
        print("\n--- CHUNK 1 PREVIEW ---")
        print(f"ID: {result[0]['chunk_id']}")
        print(f"Length: {len(result[0]['text'])} characters")
        print(f"Text: {result[0]['text'][:100]}...")