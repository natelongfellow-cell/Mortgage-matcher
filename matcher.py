from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re


class SchemaMatcher:
    def __init__(self):
        # Load a small, fast semantic model (Render‑safe on free tier)
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    @staticmethod
    def _normalize_field_name(name: str) -> str:
        name = name.lower().strip()
        name = re.sub(r"[_\-]+", " ", name)
        name = re.sub(r"[^a-z0-9\s]", "", name)
        return name

    @staticmethod
    def _tokenize(name: str) -> List[str]:
        return [t for t in name.split() if t]

    @staticmethod
    def _jaccard(a: List[str], b: List[str]) -> float:
        sa, sb = set(a), set(b)
        if not sa and not sb:
            return 0.0
        return len(sa & sb) / len(sa | sb)

    @staticmethod
    def _fuzzy_ratio(a: str, b: str) -> float:
        # Simple normalized Levenshtein‑like ratio (no external lib)
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        la, lb = len(a), len(b)
        max_len = max(la, lb)
        mismatches = sum(ch1 != ch2 for ch1, ch2 in zip(a.ljust(max_len), b.ljust(max_len)))
        return 1.0 - (mismatches / max_len)

    def _semantic_scores(
        self, structured_fields: List[str], unstructured_fields: List[str]
    ) -> np.ndarray:
        all_texts = structured_fields + unstructured_fields
        embeddings = self.model.encode(all_texts)
        s_emb = embeddings[: len(structured_fields)]
        u_emb = embeddings[len(structured_fields) :]
        return cosine_similarity(s_emb, u_emb)

    def match(
        self,
        structured_keys: List[str],
        unstructured_keys: List[str],
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        # Normalize
        s_norm = [self._normalize_field_name(k) for k in structured_keys]
        u_norm = [self._normalize_field_name(k) for k in unstructured_keys]

        s_tokens = [self._tokenize(k) for k in s_norm]
        u_tokens = [self._tokenize(k) for k in u_norm]

        # Semantic similarity matrix
        sem_matrix = self._semantic_scores(s_norm, u_norm)

        results: List[Dict[str, Any]] = []

        for i, s_key in enumerate(structured_keys):
            row: List[Tuple[str, float, Dict[str, float]]] = []

            for j, u_key in enumerate(unstructured_keys):
                # Components
                sem = float(sem_matrix[i, j])
                jac = self._jaccard(s_tokens[i], u_tokens[j])
                fuzz = self._fuzzy_ratio(s_norm[i], u_norm[j])

                # Weighted score (tuneable)
                score = 0.6 * sem + 0.25 * fuzz + 0.15 * jac

                row.append(
                    (
                        u_key,
                        score,
                        {
                            "semantic": sem,
                            "fuzzy": fuzz,
                            "token_jaccard": jac,
                        },
                    )
                )

            # Sort by score desc
            row.sort(key=lambda x: x[1], reverse=True)
            best = row[0] if row else None
            alternatives = row[1:top_k] if len(row) > 1 else []

            results.append(
                {
                    "structured_field": s_key,
                    "best_match": {
                        "unstructured_field": best[0] if best else None,
                        "score": best[1] if best else 0.0,
                        "components": best[2] if best else {},
                    },
                    "alternatives": [
                        {
                            "unstructured_field": alt[0],
                            "score": alt[1],
                            "components": alt[2],
                        }
                        for alt in alternatives
                    ],
                }
            )

        return results
