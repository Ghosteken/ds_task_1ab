import os
import pandas as pd


class DataService:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.df = None
        self._load_or_init()
        self._clean()

    def _load_or_init(self):
        csv_path = os.path.join(self.data_dir, "products.csv")
        if os.path.exists(csv_path):
            self.df = pd.read_csv(csv_path)
        else:
            self.df = pd.DataFrame(
                [
                    {"StockCode": "001", "Description": "High-Quality Headphones", "UnitPrice": 50.0, "Country": "USA"},
                    {"StockCode": "002", "Description": "Ergonomic Wireless Mouse", "UnitPrice": 20.0, "Country": "Canada"},
                    {"StockCode": "003", "Description": "Compact Espresso Machine", "UnitPrice": 100.0, "Country": "United Kingdom"},
                    {"StockCode": "004", "Description": "Smart Fitness Tracker", "UnitPrice": 30.0, "Country": "Australia"},
                    {"StockCode": "005", "Description": "Ultra-Bright LED Torch", "UnitPrice": 25.0, "Country": "New Zealand"},
                ]
            )

    def _clean(self):
        self.df = self.df.drop_duplicates()
        self.df = self.df.fillna("")
        if "Description" in self.df.columns:
            self.df["Description"] = self.df["Description"].astype(str).str.strip()

    def get_products(self) -> pd.DataFrame:
        return self.df.copy()

