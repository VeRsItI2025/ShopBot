# utils/storage.py
from services.product_service import PRODUCTS

def get_products_by_category(category: str):
    return [p for p in PRODUCTS if p["category"] == category]