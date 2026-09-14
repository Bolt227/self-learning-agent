import os
import json
from typing import List, Dict, Any

from backend.rag.document_loader import DocumentLoader
from backend.rag.chunker import TextChunker
from backend.retrieval.embeddings import get_embedding, get_embeddings
from backend.retrieval.semantic_search import cosine_similarity
from backend.retrieval.contextual_retrieval import detect_context, meaningful_words, CONTEXT_MAP, keyword_matches


# Simple local vector storage file path
RAG_STORAGE_FILE = "data/rag_store.json"


class RAGPipeline:
    """
    RAG Pipeline Component: Main Orchestrator.
    Separates Document Ingestion from Query Retrieval.
    """
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.loader = DocumentLoader()
        self.chunker = TextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        # Load simple local vector store
        self.store = self._load_store()

    def _load_store(self) -> List[Dict[str, Any]]:
        if not os.path.exists(RAG_STORAGE_FILE):
            return []
        try:
            with open(RAG_STORAGE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _save_store(self):
        os.makedirs(os.path.dirname(RAG_STORAGE_FILE) or ".", exist_ok=True)
        with open(RAG_STORAGE_FILE, "w") as f:
            json.dump(self.store, f)

    # =========================================================================
    # INGESTION PIPELINE
    # =========================================================================
    def ingest_document(self, file_path: str) -> bool:
        """
        DOCUMENT -> LOAD -> CHUNK -> GEMINI EMBEDDING -> LOCAL VECTOR STORAGE
        """
        # 1. Load document
        try:
            doc = self.loader.load(file_path)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return False

        # Prevent duplicate ingestion
        file_name = doc["filename"]
        if any(chunk.get("source") == file_name for chunk in self.store):
            print(f"Document {file_name} is already ingested. Skipping.")
            return True

        # 2. Chunk document
        chunks = self.chunker.chunk_document(doc)
        if not chunks:
            print(f"No extractable chunks in {file_path}.")
            return False

        # 3. Generate Gemini Embeddings in batch
        texts_to_embed = [c["text"] for c in chunks]
        try:
            vectors = get_embeddings(texts_to_embed)
        except Exception as e:
            print(f"Error generating embeddings for {file_path}: {e}")
            return False

        # 4. Store locally
        for i, chunk in enumerate(chunks):
            # Store chunk text, document ID, chunk ID, source, and embedding
            chunk["embedding"] = vectors[i]
            self.store.append(chunk)

        self._save_store()
        print(f"Successfully ingested {len(chunks)} chunks from {doc['filename']}")
        return True

    # =========================================================================
    # QUERY PIPELINE
    # =========================================================================
    def query(self, query_text: str, top_k: int = 3, top_n_candidates: int = 10) -> List[Dict[str, Any]]:
        """
        QUERY -> EMBEDDING -> SEMANTIC SIMILARITY -> CANDIDATE CHUNKS -> CONTEXTUAL RERANKING -> TOP RELEVANT CHUNKS
        """
        # Handle empty queries or empty vector db safely
        if not query_text or not query_text.strip() or not self.store:
            return []

        # 1. Generate query embedding
        try:
            query_vector = get_embedding(query_text)
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return []

        # 2. Semantic retrieval (Cosine Similarity)
        scored_chunks = []
        for chunk in self.store:
            # Handle corrupted data
            if "embedding" not in chunk or not chunk["embedding"]:
                continue
                
            sim = cosine_similarity(query_vector, chunk["embedding"])
            scored_chunks.append({
                "chunk": chunk,
                "semantic_score": sim
            })

        # Rank and filter to Top N Semantic Candidates
        scored_chunks.sort(key=lambda x: x["semantic_score"], reverse=True)
        candidates = scored_chunks[:top_n_candidates]

        if not candidates:
            return []

        # 3. Contextual Reranking
        detected_contexts = detect_context(query_text)
        query_words = meaningful_words(query_text)
        
        reranked = []
        for c in candidates:
            chunk_data = c["chunk"]
            text_content = chunk_data.get("text", "").lower()
            
            content_words = meaningful_words(text_content)
            
            # Reusing the logic concepts from contextual_retrieval.py
            raw_context = len(query_words & content_words) * 2.0
            
            for context in detected_contexts:
                context_keywords = CONTEXT_MAP.get(context, [])
                content_match = any(keyword_matches(text_content, k) for k in context_keywords)
                if content_match:
                    raw_context += 10.0
                    
            c["raw_context"] = raw_context
            reranked.append(c)

        # Normalize context score to prevent domination
        max_context = max([c["raw_context"] for c in reranked]) if reranked else 0.0
        
        # Configurable Engineering Weights
        SEMANTIC_WEIGHT = 0.6
        CONTEXT_WEIGHT = 0.4
        
        final_results = []
        for c in reranked:
            context_score = (c["raw_context"] / max_context) if max_context > 0 else 0.0
            final_score = (SEMANTIC_WEIGHT * c["semantic_score"]) + (CONTEXT_WEIGHT * context_score)
            
            # Format output specifically to requirements
            final_results.append({
                "text": c["chunk"]["text"],
                "source": c["chunk"]["source"],
                "chunk_id": c["chunk"]["chunk_id"],
                "semantic_score": c["semantic_score"],
                "final_score": final_score
            })

        # Rank by final aggregated score
        final_results.sort(key=lambda x: x["final_score"], reverse=True)
        return final_results[:top_k]


if __name__ == "__main__":
    import tempfile
    
    # 1. Clean environment for test
    if os.path.exists(RAG_STORAGE_FILE):
        os.remove(RAG_STORAGE_FILE)

    print("=== RAG Pipeline Ingestion ===")
    
    # Create test document
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("Python is a programming language.\n")
        f.write("FastAPI is a Python framework for building APIs.\n")
        f.write("RAG retrieves external knowledge before generating a response.")
        test_file = f.name
        
    # We use small chunk_size to force it to split the lines for the test
    rag = RAGPipeline(chunk_size=100, chunk_overlap=20)
    
    try:
        rag.ingest_document(test_file)
        
        # Test Duplicate Protection
        print("\nTesting duplicate protection:")
        rag.ingest_document(test_file)
        
        print("\n=== RAG Pipeline Query ===")
        test_query = "What Python framework can be used to build APIs?"
        print(f"Query: '{test_query}'\n")
        
        results = rag.query(test_query, top_k=2)
        
        for i, res in enumerate(results, 1):
            print(f"Result #{i}")
            print(f"Source:         {res['source']} (Chunk {res['chunk_id']})")
            print(f"Final Score:    {res['final_score']:.4f}")
            print(f"Semantic Score: {res['semantic_score']:.4f}")
            print(f"Text:           \"{res['text']}\"\n")
            
    finally:
        os.remove(test_file)
