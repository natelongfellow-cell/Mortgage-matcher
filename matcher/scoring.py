from .utils import normalize

def score_fields(a, b):
    a_norm = normalize(a)
    b_norm = normalize(b)
    return {
        "match": a_norm == b_norm,
        "score": 100 if a_norm == b_norm else 0,
    }
