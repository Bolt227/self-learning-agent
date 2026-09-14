import os
import uuid
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any

class DocumentLoader:
    """
    RAG Pipeline Component: Document Loader.
    Responsible for normalizing various file formats into raw text + metadata.
    """
    def __init__(self):
        # Map extensions to specific extraction logic
        self.loaders = {
            ".txt": self._load_text,
            ".md": self._load_text,
            ".docx": self._load_docx,
            ".pdf": self._load_pdf
        }

    def load(self, file_path: str) -> Dict[str, Any]:
        """
        Loads a document, returning normalized text and preservation metadata.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if os.path.getsize(file_path) == 0:
            raise ValueError(f"File is empty: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in self.loaders:
            raise ValueError(f"Unsupported file format: {ext}. Supported: {list(self.loaders.keys())}")
            
        # Base metadata
        filename = os.path.basename(file_path)
        doc_id = str(uuid.uuid4())
        
        try:
            raw_text = self.loaders[ext](file_path)
            
            # Normalize text: clean line endings and trim white space
            normalized_text = raw_text.replace('\r\n', '\n').strip()
            
            if not normalized_text:
                raise ValueError(f"No extractable text found in {filename}")
                
            return {
                "document_id": doc_id,
                "filename": filename,
                "source": os.path.abspath(file_path),
                "type": ext,
                "text": normalized_text
            }
            
        except Exception as e:
            raise RuntimeError(f"Error loading document '{filename}': {str(e)}")

    def _load_text(self, file_path: str) -> str:
        """Loads plain text files."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def _load_docx(self, file_path: str) -> str:
        """
        Extracts text from a DOCX file using Python's built-in zipfile and XML parser.
        This completely avoids the need for external dependencies like 'python-docx'.
        """
        try:
            with zipfile.ZipFile(file_path) as docx:
                xml_content = docx.read("word/document.xml")
                tree = ET.fromstring(xml_content)
                
                # Word XML namespace
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                
                paragraphs = []
                for p in tree.iterfind('.//w:p', ns):
                    p_text = [t.text for t in p.iterfind('.//w:t', ns) if t.text]
                    if p_text:
                        paragraphs.append("".join(p_text))
                        
                return "\n".join(paragraphs)
        except zipfile.BadZipFile:
            raise ValueError("Corrupt or invalid DOCX file structure")

    def _load_pdf(self, file_path: str) -> str:
        """
        PDF extraction requires complex layout algorithms not present in the standard library.
        Attempts to use PyPDF2 if installed, otherwise safely aborts to prevent bloat.
        """
        try:
            import PyPDF2
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join([page.extract_text() or "" for page in reader.pages])
        except ImportError:
            raise ImportError(
                "PDF extraction requires an external library to avoid unnecessary bloat. "
                "Please run: 'pip install PyPDF2' if you need PDF support."
            )


if __name__ == "__main__":
    import tempfile
    
    loader = DocumentLoader()
    print("=== Testing RAG Document Loader ===\n")
    
    # 1. Test Standard TXT Extraction
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("Self-Learning Agent Context.\n\nThis is a sample document meant to test RAG ingestion.")
        temp_txt = f.name
        
    try:
        result = loader.load(temp_txt)
        print("[SUCCESS] Loaded Valid File")
        print(f"Document ID: {result['document_id']}")
        print(f"Filename:    {result['filename']}")
        print(f"Source path: {result['source']}")
        print(f"Text Content:\n\"{result['text']}\"\n")
    finally:
        os.remove(temp_txt)
        
    # 2. Test Empty File Handling Safely
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w") as f:
        pass # Empty file
        
    try:
        loader.load(f.name)
    except Exception as e:
        print(f"[SUCCESS] Handled Empty File gracefully -> {type(e).__name__}: {e}")
        
    # 3. Test Unsupported Format
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False, mode="w") as f:
        pass
        
    try:
        loader.load(f.name)
    except Exception as e:
        print(f"[SUCCESS] Handled Unsupported Format gracefully -> {type(e).__name__}: {e}")
