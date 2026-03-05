import fitz  # PyMuPDF
import unicodedata
import re

class PDFParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = None

    def load(self):
        """
        Opens the PDF file.
        Why? We keep the file open only as long as needed to save memory.
        """
        try:
            self.doc = fitz.open(self.file_path)
            print(f"✅ Opened PDF: {self.file_path} with {len(self.doc)} pages.")
        except Exception as e:
            print(f"❌ Error opening PDF: {e}")
            raise

    def clean_text(self, text):
        
        # 1. Unicode Normalization (Standardize characters)
        text = unicodedata.normalize('NFKC', text)
        
        # 2. Fix Hyphenation (Fix split words at end of lines)
        # Example: "busi-\nness" -> "business"
        text = re.sub(r'-\n', '', text)
        
        # 3. The "Smart" Whitespace Fix (THE NEW PART)
        # Strategy:
        # A. We replace "Single Newline" with "Space" (Joins sentences)
        # B. We replace "Double Newline" with "Double Newline" (Preserves paragraphs)
        
        # First, we identify actual paragraphs.
        # This regex looks for 2 or more newlines and temporarily marks them 
        # with a special placeholder string that definitely isn't in the text.
        text = re.sub(r'\n\s*\n', '<<PARAGRAPH_BREAK>>', text)
        
        # Now, any remaining single newlines are just line-wraps. 
        # Replace them with a space.
        text = re.sub(r'\n', ' ', text)
        
        # Finally, restore the paragraph breaks.
        text = text.replace('<<PARAGRAPH_BREAK>>', '\n\n')
        
        # Collapse multiple spaces (but NOT newlines) into one
        # This regex matches specific horizontal whitespace (tabs, spaces)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()

    def extract(self):
        """
        The main worker.
        Iterates pages, extracts text, and cleans it.
        Returns a list of dictionaries (one per page).
        """
        if not self.doc:
            self.load()
        
        pages_content = []
        
        for page_num, page in enumerate(self.doc):
            # extract raw text
            raw_text = page.get_text()
            
            # clean it
            cleaned_text = self.clean_text(raw_text)
            
            # Why store page_num?
            # So the AI can cite its sources later! ("Found on page 5")
            if cleaned_text: # Only save if there is text
                pages_content.append({
                    "page": page_num + 1,
                    "text": cleaned_text,
                    "source": self.file_path
                })
                
        return pages_content

# --- TESTING BLOCK ---
# This allows us to run this file directly to test it without running the whole app.
if __name__ == "__main__":
    # REPLACE THIS with your actual PDF filename
    sample_pdf = r"data\pdfs\sample.pdf" 
    
    # Check if file exists first!
    import os
    if not os.path.exists(sample_pdf):
        print(f"⚠️  Please put a PDF file at: {sample_pdf}")
    else:
        parser = PDFParser(sample_pdf)
        data = parser.extract()
        
        # Print the first 500 characters of the first page to verify
        print("\n--- PREVIEW OF PAGE 1 ---")
        print(data[35]['text'][:1500])
        print("...")