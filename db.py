import sqlite3

# Подключение к базе (создаст файл shop.db, если его нет)
conn = sqlite3.connect("shop.db")
conn.row_factory = sqlite3.Row   # строки будут dict-подобные
cursor = conn.cursor()

# Создание таблицы товаров
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    desc TEXT,
    photo TEXT,
    status TEXT DEFAULT 'Новый'
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
def add_product(name, category, price, desc, photo):
    conn = sqlite3.connect("shop.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, category, price, desc, photo, status) VALUES (?, ?, ?, ?, ?, ?)",
        (name, category, price, desc, photo, "Новый")
    )
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return [dict(row) for row in products]

def get_products_by_category(category: str):
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    products = cursor.fetchall()
    conn.close()
    return [dict(row) for row in products]

def get_product_by_id(product_id: int):
    conn = sqlite3.connect("shop.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return dict(product) if product else None

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
               products.name, products.price, products.photo
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id = ?
    """, (user_id,))
    items = cursor.fetchall()
    conn.close()
    return [dict(row) for row in items]

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
        "https://i.postimg.cc/7Zz2ML2J/Chat-GPT-Image.png"
    )

    add_product(
        "Смартфон Samsung Galaxy S21",
        "Телефоны",
        850,
        "Флагманский смартфон с отличной камерой",
        "https://i.postimg.cc/brHtcVqx/Chat-GPT-Image.png"
    )

    print("✅ База пересоздана и заполнена тестовыми товарами")