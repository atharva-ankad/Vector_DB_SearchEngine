from rag.retriever import VectorRetriever
from rag.generator import GroqGenerator

def main():
    print("Initializing RAG System (Groq Edition)...")
    
    retriever = VectorRetriever()
    generator = GroqGenerator()
    
    print("\n✅ System Ready! (Type 'exit' to quit)\n")

    while True:
        query = input("User: ")
        if query.lower() in ['exit', 'quit']:
            break

        # 1. Retrieve
        relevant_chunks = retriever.retrieve(query, top_k=4)
        
        # 2. Generate (Streamed)
        if relevant_chunks:
            # The generator now prints the response as it streams
            generator.generate_answer(query, relevant_chunks)
            
            # Print citations after the stream finishes
            print("📚 References:")
            for chunk in relevant_chunks:
                meta = chunk.get('metadata', {})
                print(f"- Page {meta.get('page')} (Score: {chunk.get('score', 0):.4f})")
            print("\n")
        else:
            print("No relevant context found.\n")

if __name__ == "__main__":
    main()