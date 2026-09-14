import math
import os
import json
from typing import List, Dict, Any
from backend.memory.memory_store import load_memories, save_memory
from backend.retrieval.embeddings import get_embedding, get_embeddings
from backend.retrieval.contextual_retrieval import detect_context, meaningful_words, CONTEXT_MAP, keyword_matches

# Configuration weights (Engineering parameters, not scientifically validated)
SEMANTIC_WEIGHT = 0.5
CONTEXT_WEIGHT = 0.3
IMPORTANCE_WEIGHT = 0.2


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculates pure mathematical cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return dot_product / (norm1 * norm2)


def semantic_search(user_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Performs true semantic retrieval by comparing vector embeddings
    of the query against the user's memories.
    """
    if not query or not query.strip():
        return []
        
    memories = load_memories(user_id)
    if not memories:
        return []
        
    query_vector = get_embedding(query)
    memory_texts = [mem.get("content", "") for mem in memories]
    memory_vectors = get_embeddings(memory_texts)
    
    scored_memories = []
    
    for i, memory in enumerate(memories):
        score = cosine_similarity(query_vector, memory_vectors[i])
        scored_memory = memory.copy()
        scored_memory["semantic_similarity"] = score
        scored_memories.append(scored_memory)
        
    scored_memories.sort(key=lambda x: x["semantic_similarity"], reverse=True)
    return scored_memories[:top_k]


def combined_rerank_search(user_id: str, query: str, top_k: int = 5, top_n_candidates: int = 20) -> List[Dict[str, Any]]:
    """
    MILESTONE 3: Combined Semantic + Contextual Reranking Pipeline.
    1. Retrieves a broad set of candidates using semantic similarity.
    2. Scores candidates based on context and importance.
    3. Normalizes and combines scores for a final ranking.
    """
    # 1. Semantic retrieval for a larger candidate set (Top N)
    semantic_results = semantic_search(user_id, query, top_k=top_n_candidates)
    
    if not semantic_results:
        return []
        
    # 2. Extract query context variables
    detected_contexts = detect_context(query)
    query_words = meaningful_words(query)
    
    raw_candidates = []
    
    for res in semantic_results:
        semantic_score = res["semantic_similarity"] # Already bounded roughly 0 to 1
        
        content = res.get("content", "").lower()
        scope = res.get("scope", "").lower()
        
        # Importance is usually 0.0 to 1.0 based on our extractor
        importance_score = float(res.get("importance", 0.0))
        
        # Calculate raw context score mimicking contextual_retrieval.py
        content_words = meaningful_words(content)
        scope_words = meaningful_words(scope)
        
        raw_context = 0.0
        raw_context += len(query_words & content_words) * 2.0
        raw_context += len(query_words & scope_words) * 3.0
        
        for context in detected_contexts:
            context_keywords = CONTEXT_MAP.get(context, [])
            
            content_match = any(keyword_matches(content, k) for k in context_keywords)
            scope_match = any(keyword_matches(scope, k) for k in context_keywords)
            
            if content_match:
                raw_context += 10.0
            if scope_match:
                raw_context += 15.0
                
        raw_candidates.append({
            "memory": res, # Keeping original memory dict
            "semantic_score": semantic_score,
            "raw_context": raw_context,
            "importance_score": importance_score
        })
        
    # 4. Normalize context scores so they don't dominate the bounded semantic scores
    max_context = max([c["raw_context"] for c in raw_candidates]) if raw_candidates else 0.0
    
    final_results = []
    for c in raw_candidates:
        # Prevent division by zero if no context matches
        context_score = (c["raw_context"] / max_context) if max_context > 0 else 0.0
        
        # 3. Combine scores using configurable weights
        final_score = (
            (SEMANTIC_WEIGHT * c["semantic_score"]) +
            (CONTEXT_WEIGHT * context_score) +
            (IMPORTANCE_WEIGHT * c["importance_score"])
        )
        
        final_results.append({
            "memory": {k: v for k, v in c["memory"].items() if k != "semantic_similarity"}, # Clean dict
            "semantic_score": c["semantic_score"],
            "context_score": context_score,
            "importance_score": c["importance_score"],
            "final_score": final_score
        })
        
    # Sort by final aggregated score
    final_results.sort(key=lambda x: x["final_score"], reverse=True)
    return final_results[:top_k]


if __name__ == "__main__":
    
    test_user_id = "rerank_test_user"
    
    # 1. Clean test environment
    memory_file = "data/memory.json"
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            data = json.load(f)
        if test_user_id in data:
            data[test_user_id] = []
            with open(memory_file, "w") as f:
                json.dump(data, f)
    
    # 2. Dataset highlighting the differences
    test_memories = [
        # Memory A: High semantic match to "learning algorithms", but low importance, no scope
        {"content": "I watched a video on learning sorting algorithms.", "type": "interest", "scope": "", "importance": 0.2},
        # Memory B: Lower semantic match, but massive importance and relevant scope
        {"content": "I enjoy competitive programming.", "type": "preference", "scope": "competitive programming", "importance": 1.0},
        # Memory C: Specific keyword triggers context map for Python
        {"content": "I usually develop my projects using Python.", "type": "preference", "scope": "software development", "importance": 0.8},
    ]
    
    for mem in test_memories:
        save_memory(test_user_id, mem)
        
    # 3. Run evaluation scenario
    query = "How do I usually approach competitive programming algorithms?"
    
    print("\n" + "="*50)
    print(f"QUERY: '{query}'")
    print("="*50)
    
    # Run Pure Semantic Retrieval
    print("\n--- 1. PURE SEMANTIC RETRIEVAL ---")
    semantic_res = semantic_search(test_user_id, query, top_k=2)
    for i, res in enumerate(semantic_res, 1):
        print(f"  {i}. [Semantic Score: {res['semantic_similarity']:.4f}] {res['content']}")
        
    # Run Combined Reranking
    print("\n--- 2. COMBINED CONTEXTUAL RERANKING ---")
    rerank_res = combined_rerank_search(test_user_id, query, top_k=2)
    for i, res in enumerate(rerank_res, 1):
        print(f"  {i}. [Final Score: {res['final_score']:.4f}] {res['memory']['content']}")
        print(f"     -> Semantic: {res['semantic_score']:.4f} | Context: {res['context_score']:.4f} | Importance: {res['importance_score']:.4f}")
    
    print("\n")
