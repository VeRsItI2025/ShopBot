import sqlite3

# Подключение к базе (создаст файл shop.db, если его нет)
conn = sqlite3.connect("shop.db")
conn.row_factory = sqlite3.Row   # строки будут dict-подобные
cursor = conn.cursor()

# Создание таблицы товаров
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price REAL,
    old_price REAL,
    desc TEXT,
    photos TEXT,
    details TEXT,
    status TEXT DEFAULT 'Новый',
    discount_until TEXT   -- время окончания скидки
)
""")


# Создание таблицы заказов
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT,
    phone TEXT,
    items TEXT,
    total REAL,
    status TEXT DEFAULT 'Новый'
)
""")

# Создание таблицы корзины
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    quantity INTEGER DEFAULT 1
)
""")

conn.commit()

# --- CRUD функции для товаров ---
def add_product(name, category, price, desc, photos: list[str], details, status="Новый"):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    photos_str = ";".join(photos)  # превращаем список в строку
    cursor.execute(
        "INSERT INTO products (name, category, price, desc, photos, details, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, category, price, desc, photos_str, details, status)
    )
    conn.commit()
    conn.close()


def get_all_products():
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    products = []
    for row in rows:
        product = dict(row)
        product["photos"] = product.get("photos", "").split(";") if product.get("photos") else []
        products.append(product)
    return products


def get_products_by_category(category: str):
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    products = []
    for row in rows:
        product = dict(row)
        product["photos"] = product.get("photos", "").split(";") if product.get("photos") else []
        products.append(product)
    return products



def get_product_by_id(product_id: int):
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        product = dict(row)
        product["photos"] = product["photos"].split(";") if product["photos"] else []
        return product
    return None


def update_product(product_id: int, field: str, value):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute(f"UPDATE products SET {field} = ? WHERE id = ?", (value, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id: int):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

# --- Работа с заказами ---
def save_order(user_id, name, phone, cart):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    total = sum(item["price"] for item in cart)
    items = "; ".join([f"{item['name']} ({item['price']} грн)" for item in cart])

    cursor.execute(
        "INSERT INTO orders (user_id, name, phone, items, total, status) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, name, phone, items, total, "Новый")
    )

    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id

def update_order_status(order_id: int, status: str):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

def get_all_orders():
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return [dict(row) for row in orders]

def get_order_by_id(order_id: int):
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    conn.close()
    return dict(order) if order else None

# --- Работа с корзиной ---
def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
        (user_id, product_id, quantity)
    )
    conn.commit()
    conn.close()

def get_cart(user_id: int):
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cart.id, cart.product_id, cart.quantity,
               products.name, products.price, products.photos
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = ?
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    items = []
    for row in rows:
        item = dict(row)
        item["photos"] = item["photos"].split(";") if item["photos"] else []
        items.append(item)
    return items

def clear_cart(user_id: int):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def remove_from_cart(user_id: int, product_id: int):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    conn.close()

def calculate_total(user_id: int) -> float:
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(products.price * cart.quantity) as total
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = ?
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result["total"] if result and result["total"] else 0.0

# Скидки

def set_discount(product_id: int, new_price: float, until: str):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    old_price = row[0] if row else None

    cursor.execute("""
        UPDATE products
        SET old_price = ?, price = ?, status = 'Скидка', discount_until = ?
        WHERE id = ?
    """, (old_price, new_price, until, product_id))

    conn.commit()
    conn.close()


def remove_expired_discounts():
    import datetime
    now = datetime.datetime.now().isoformat()

    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET price = old_price, old_price = NULL, status = 'Новый', discount_until = NULL
        WHERE discount_until IS NOT NULL AND discount_until < ?
    """, (now,))
    conn.commit()
    conn.close()


def set_discount_price(product_id: int, new_price: float):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()

    # получаем текущую цену
    cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    old_price = row[0] if row else None

    # обновляем запись
    cursor.execute(
        "UPDATE products SET old_price = ?, price = ?, status = 'Скидка' WHERE id = ?",
        (old_price, new_price, product_id)
    )
    conn.commit()
    conn.close()




def get_all_categories():
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products")
    rows = cursor.fetchall()
    conn.close()
    # превращаем список кортежей в список строк
    return [row[0] for row in rows]


# --- Тестовые данные ---
if __name__ == "__main__":
    # Очистим таблицу товаров
    cursor.execute("DELETE FROM products")
    conn.commit()

    # Добавляем тестовые товары
    add_product(
        "Ноутбук Lenovo IdeaPad",
        "Ноутбуки",
        1500,
        "Ноутбук для Gaming",
        [
            "https://i.postimg.cc/Hk1bk3tZ/Chat-GPT-Image-22-sic-2026-r-17-59-22.png",
            "https://i.postimg.cc/Hk1bk3tZ/Chat-GPT-Image-22-sic-2026-r-17-59-22.png"
        ],
        "Процессор Intel i5, 8GB RAM, SSD 256GB"
    )

    add_product(
        "Смартфон Samsung Galaxy S21",
        "Телефоны",
        850,
        "Флагманский смартфон с отличной камерой",
        [
            "https://i.postimg.cc/Hk1bk3tZ/Chat-GPT-Image-22-sic-2026-r-17-59-22.png"
        ],
        "Экран 6.2'', 8GB RAM, 128GB ROM"
    )

    print("✅ База пересоздана и заполнена тестовыми товарами")
