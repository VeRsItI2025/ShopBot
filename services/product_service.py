# services/product_service.py
from db import get_product_by_id, get_all_products, get_products_by_category

# Получить товар по ID
def fetch_product_by_id(product_id: int):
    return get_product_by_id(product_id)

# Получить все товары
def fetch_all_products():
    return get_all_products()

# Получить товары по категории
def fetch_products_by_category(category: str):
    return get_products_by_category(category)