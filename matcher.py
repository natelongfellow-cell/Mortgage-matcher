# matcher.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz
import json

def token_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return fuzz.token_sort_ratio(a, b) / 100

def tfidf_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    vectorizer = TfidfVectorizer().fit([a, b])
    vectors = vectorizer.transform([a, b])
    return float(cosine_similarity(vectors[0], vectors[1])[0][0])

def combined_similarity(a: str, b: str) -> float:
    t = token_similarity(a, b)
    s = tfidf_similarity(a, b)
    return round(0.4 * t + 0.6 * s, 4)

def compare_json(structured: dict, unstructured: dict):
    results = []
    total_score = 0
    count = 0

    for key, value in structured.items():
        u_val = unstructured.get(key, "")
        score = combined_similarity(str(value), str(u_val))

        results.append({
            "field": key,
            "structured_value": value,
            "unstructured_value": u_val,
            "score": score
        })

        total_score += score
        count += 1

    overall = round(total_score / max(count, 1), 4)

    return {
        "overall_score": overall,
        "field_results": results
    }
