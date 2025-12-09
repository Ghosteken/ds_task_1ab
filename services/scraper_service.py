import os
import csv
import time
import requests
from bs4 import BeautifulSoup


class ScraperService:
    def __init__(self, out_root: str = "data/images"):
        self.out_root = out_root
        os.makedirs(self.out_root, exist_ok=True)

    def _duckduckgo_image_urls(self, query: str, limit: int = 10):
        params = {"q": query, "iax": "images", "ia": "images"}
        r = requests.get("https://duckduckgo.com/", params=params)
        token = "vqd"
        if token not in r.text:
            return []
        vqd = r.text.split(token + "\":\"")[1].split("\"")[0]
        api = "https://duckduckgo.com/i.js"
        urls = []
        s = requests.Session()
        while len(urls) < limit:
            res = s.get(api, params={"q": query, "vqd": vqd, "o": "json"}, timeout=10)
            data = res.json()
            for item in data.get("results", []):
                urls.append(item.get("image"))
                if len(urls) >= limit:
                    break
            if not data.get("next"):
                break
            time.sleep(0.5)
        return [u for u in urls if u]

    def scrape(self, product_class: str, count: int = 20) -> str:
        out_dir = os.path.join(self.out_root, product_class)
        os.makedirs(out_dir, exist_ok=True)
        urls = self._duckduckgo_image_urls(product_class, count)
        paths = []
        for i, url in enumerate(urls):
            try:
                resp = requests.get(url, timeout=10)
                ext = ".jpg"
                path = os.path.join(out_dir, f"img_{i}{ext}")
                with open(path, "wb") as f:
                    f.write(resp.content)
                paths.append(path)
            except Exception:
                continue
        return out_dir

    def write_train_csv(self, csv_path: str = "CNN_Model_Train_Data.csv"):
        rows = []
        for cls in os.listdir(self.out_root):
            d = os.path.join(self.out_root, cls)
            if not os.path.isdir(d):
                continue
            for fn in os.listdir(d):
                rows.append({"class": cls, "path": os.path.join(d, fn)})
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["class", "path"])
            w.writeheader()
            w.writerows(rows)

