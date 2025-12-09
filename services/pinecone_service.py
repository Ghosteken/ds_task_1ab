import os
from typing import List, Dict


class PineconeService:
    def __init__(self, index_name: str = "products-index", dimension: int = 512):
        self.pc = None
        self.index = None
        self.index_name = index_name
        self.dimension = dimension
        api_key = os.getenv("PINECONE_API_KEY")
        try:
            if api_key:
                from pinecone import Pinecone
                self.pc = Pinecone(api_key=api_key)
                self._ensure_index()
        except Exception:
            self.pc = None

    def _ensure_index(self):
        exists = False
        try:
            for idx in self.pc.list_indexes().indexes:
                if idx.name == self.index_name:
                    exists = True
                    break
            if not exists:
                self.pc.create_index(name=self.index_name, dimension=self.dimension, metric="cosine")
            self.index = self.pc.Index(self.index_name)
        except Exception:
            self.index = None

    def upsert_vectors(self, ids: List[str], vectors: List[List[float]], metadata: List[Dict] = None):
        if self.index is None:
            return
        items = []
        for i, vec in enumerate(vectors):
            item = {"id": ids[i], "values": vec}
            if metadata:
                item["metadata"] = metadata[i]
            items.append(item)
        self.index.upsert(vectors=items)

    def query(self, vector: List[float], top_k: int = 5):
        if self.index is None:
            return []
        res = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
        return res.matches

