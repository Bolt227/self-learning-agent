from typing import List, Dict, Any

class TextChunker:
    """
    RAG Pipeline Component: Text Chunker.
    Splits large, normalized document text into smaller, overlapping chunks 
    that fit comfortably inside embedding limits and LLM context windows.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")
            
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes a loaded document dictionary and deterministically splits its text 
        into overlapping chunks, preserving original metadata for traceability.
        """
        text = document.get("text", "")
        if not text:
            return []
            
        doc_id = document.get("document_id", "unknown_id")
        # Extract filename as the source, per the prompt requirement ("source": "example.pdf")
        source = document.get("filename", "unknown_source")
        
        chunks = []
        chunk_id = 0
        
        # Calculate the exact distance to slide the window forward each iteration
        step = self.chunk_size - self.chunk_overlap
        
        for i in range(0, len(text), step):
            # Extract the raw chunk slice
            chunk_text = text[i : i + self.chunk_size]
            
            # Safety check: Never return purely empty/whitespace chunks
            if not chunk_text.strip():
                continue
                
            chunks.append({
                "text": chunk_text.strip(),
                "document_id": doc_id,
                "chunk_id": chunk_id,
                "source": source
            })
            
            chunk_id += 1
            
            # If our current slice successfully captured the absolute end of the document,
            # stop immediately to prevent creating trailing redundant overlap-only chunks.
            if i + self.chunk_size >= len(text):
                break
                
        return chunks


if __name__ == "__main__":
    print("=== Testing RAG Text Chunker ===\n")
    
    # 1. Mock a document exactly as it would be emitted by document_loader.py
    mock_document = {
        "document_id": "doc-555-abc",
        "filename": "ai_history.pdf",
        "source": "/path/to/ai_history.pdf",
        "type": ".pdf",
        "text": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to intelligence of humans and other animals. "
                "AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals. "
                "A major goal of AI research is to create technology that allows computers and machines to function in an intelligent manner."
    }
    
    # 2. Configure tiny chunks artificially so we can visually verify the overlap on a short string
    # We want 100 character chunks, with 30 characters of overlap trailing backward.
    chunker = TextChunker(chunk_size=100, chunk_overlap=30)
    
    print(f"Original Text Length: {len(mock_document['text'])} characters")
    print(f"Configuration: Chunk Size = {chunker.chunk_size}, Overlap = {chunker.chunk_overlap}\n")
    
    # 3. Execute
    chunks = chunker.chunk_document(mock_document)
    
    print(f"SUCCESS: Split document into {len(chunks)} sequential chunks.\n")
    
    for c in chunks:
        print(f"--- Chunk ID: {c['chunk_id']} ---")
        print(f"Document ID:  {c['document_id']}")
        print(f"Source:       {c['source']}")
        print(f"Length:       {len(c['text'])} chars")
        print(f"Content:      \"{c['text']}\"\n")
