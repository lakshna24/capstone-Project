import re
import math
from typing import List, Dict, Any

VOCABULARY = [
    "sort",
    "search",
    "binary",
    "insertion",
    "sql",
    "join",
    "fastapi",
    "pydantic",
    "prompt",
    "llm",
    "database",
    "validate"
]

SEED_NOTES = [
    {"id": 1, "text": "Binary search requires a sorted array and repeatedly halves the search range using a midpoint comparison."},
    {"id": 2, "text": "Insertion sort builds a sorted list one element at a time by shifting larger elements to the right."},
    {"id": 3, "text": "FastAPI uses Pydantic models to validate request bodies and automatically generates Swagger documentation."},
    {"id": 4, "text": "SQL joins combine rows from two tables using a matching column, such as inner join, left join, and full join."},
    {"id": 5, "text": "Prompt engineering structures a task, context, constraints, and desired output format to guide an LLM's response."},
]

def summarize_notes(raw_text: str) -> Dict[str, Any]:
    """
    Offline Note Summarizer.
    Returns dict with keys: topic, key_points, difficulty.
    """
    trimmed = raw_text.strip()
    if not trimmed:
        return {
            "topic": "untitled",
            "key_points": [],
            "difficulty": "easy"
        }

    # Topic derivation: first non-empty line
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    topic = lines[0] if lines else "untitled"

    # Key points: split on '.', '!', '?'
    raw_sentences = re.split(r'[.!?]', raw_text)
    key_points = [s.strip() for s in raw_sentences if s.strip()][:3]

    # Word count difficulty
    words = trimmed.split()
    word_count = len(words)
    if word_count < 40:
        difficulty = "easy"
    elif word_count <= 100:
        difficulty = "medium"
    else:
        difficulty = "hard"

    return {
        "topic": topic,
        "key_points": key_points,
        "difficulty": difficulty
    }

def mock_embed(text: str) -> List[float]:
    """
    Mock Embedding generator over 12-token vocabulary.
    Tokenizes text by non-alphanumeric characters, lowercase, counts exact whole-token matches.
    Returns 12 float vector. Zero vector if text is empty/no matches.
    """
    if not text or not text.strip():
        return [0.0] * len(VOCABULARY)

    tokens = re.split(r'[^a-z0-9]+', text.lower())
    token_counts = {}
    for token in tokens:
        if token:
            token_counts[token] = token_counts.get(token, 0) + 1

    return [float(token_counts.get(vocab_word, 0)) for vocab_word in VOCABULARY]

def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Manually calculates cosine similarity: dot_product / (mag_a * mag_b).
    Returns 0.0 if either vector is all zeros. Never raises ZeroDivisionError.
    """
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot_product / (mag_a * mag_b)

def search_notes(query: str) -> List[Dict[str, Any]]:
    """
    Ranks notes by cosine similarity to query vector.
    Preserves original ID order if query produces zero vector.
    """
    query_vec = mock_embed(query)
    results = []

    for note in SEED_NOTES:
        note_vec = mock_embed(note["text"])
        sim_score = cosine_similarity(query_vec, note_vec)
        results.append({
            "id": note["id"],
            "text": note["text"],
            "similarity": round(sim_score, 4)
        })

    # If query_vec is all zero, all similarity scores are 0.0, maintain original order
    is_zero_query = all(v == 0.0 for v in query_vec)
    if is_zero_query:
        return results

    # Sort descending by similarity, preserving order for equal scores
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results
