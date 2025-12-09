import os
import numpy as np
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class VectorService:
    def __init__(self, descriptions: List[str], metric: str = "cosine"):
        self.metric = metric
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(descriptions)

    def _similarity(self, q_vec) -> np.ndarray:
        if self.metric == "cosine":
            return cosine_similarity(q_vec, self.matrix).flatten()
        if self.metric == "dot":
            return (q_vec @ self.matrix.T).toarray().flatten()
        return cosine_similarity(q_vec, self.matrix).flatten()

    def search(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        q_vec = self.vectorizer.transform([query])
        sims = self._similarity(q_vec)
        idxs = np.argsort(-sims)[:top_k]
        return [(int(i), float(sims[i])) for i in idxs]

