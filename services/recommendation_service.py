from typing import List, Dict


class RecommendationService:
    def __init__(self, data_service, vector_service):
        self.data_service = data_service
        self.vector_service = vector_service

    def _is_bad_query(self, q: str) -> bool:
        if not q or len(q.strip()) < 3:
            return True
        banned = {"hack", "sql", "drop", "delete"}
        return any(b in q.lower() for b in banned)

    def recommend(self, query: str, top_k: int = 5) -> Dict[str, List[Dict]]:
        if self._is_bad_query(query):
            return {"products": [], "response": "Please provide a clearer product-related query."}
        df = self.data_service.get_products()
        indices = self.vector_service.search(query, top_k)
        items = []
        for idx, score in indices:
            row = df.iloc[idx]
            items.append(
                {
                    "StockCode": str(row.get("StockCode", "")),
                    "Description": str(row.get("Description", "")),
                    "UnitPrice": float(row.get("UnitPrice", 0.0)),
                    "Country": str(row.get("Country", "")),
                    "similarity": score,
                }
            )
        if not items:
            resp = "No matching products found."
        else:
            names = ", ".join(x["Description"] for x in items)
            resp = f"Recommended products: {names}."
        return {"products": items, "response": resp}

