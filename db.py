import sqlite3 as sq


async def db_start():
    global db, cursor

    db = sq.connect('database.db')
    cursor = db.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY NOT NULL, phone_number TEXT, adress TEXT, indx TEXT,username TEXT, order_value INTEGER DEFAULT 0, personal_sale INTEGER DEFAULT 0, page INTEGER DEFAULT 1, page INTEGER DEFAULT 1)")

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS promo(promocode TEXT, sale_by_promo INTEGER)")

    db.commit()


def update_user_data(user_id, address=None, indx=None, username=None, phone_number=None):
    update_query = "UPDATE users SET"
    update_params = []
    if address is not None:
        update_query += " adress=?,"
        update_params.append(address)
    elif username is not None:
        update_query += " username=?,"
        update_params.append(username)
    elif indx is not None:
        update_query += " indx=?,"
        update_params.append(indx)
    elif phone_number is not None:
        update_query += " phone_number=?,"
        update_params.append(phone_number)
    update_params.append(user_id)
    update_query = update_query.rstrip(",") + " WHERE user_id=?"
    print(update_query)
    print(update_params)

    cursor.execute(update_query, update_params)
    db.commit()


async def create_profile(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    result = cursor.fetchone()

    if result is None:
        # Добавление нового пользователя в базу данных
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
        db.commit()


async def get_user(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    column_names = [description[0] for description in cursor.description]
    user_data = dict(zip(column_names, result))
    return user_data


async def create_promo(promo, promo_value):
    cursor.execute('INSERT INTO promo (promo, promo_value) VALUES (?, ?)', (promo, promo_value))
    db.commit()


async def add_product(product, image_link, description):
    # Устанавливаем соединение с базой данны

    # Создаем таблицу, если она не существует
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, product TEXT, image_link TEXT, description TEXT)')

    # Проверяем текущий максимальный id в таблице
    cursor.execute('SELECT MAX(id) FROM products')
    max_id = cursor.fetchone()[0]
    if max_id is None:
        max_id = 0
    else:
        max_id += 1

    # Вставляем новый товар в таблицу с автоматической нумерацией id
    cursor.execute('INSERT INTO products (id, product, image_link, description) VALUES (?, ?, ?, ?)',
                   (max_id, product, image_link, description))

    # Сохраняем изменения и закрываем соединение с базой данных
    db.commit()


async def get_product(id):
    cursor.execute('SELECT * FROM products WHERE id = ?', (id,))
    result = cursor.fetchone()

    column_names = [description[0] for description in cursor.description]
    product_data = dict(zip(column_names, result))
    print(id)
    return product_data


async def set_page(user_id, page):
    cursor.execute("UPDATE users SET page=? WHERE user_id=?", (page, user_id))
    db.commit()


async def next_page(user_id):
    cursor.execute("SELECT page FROM users WHERE user_id=?", (user_id,))
    current_page = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT() FROM products")
    count = cursor.fetchone()[0]
    print(count // 2, count // 2 * 2, count)
    if count // 2 * 2 - 3 == current_page:
        new_page = current_page
    else:
        new_page = current_page + 2

    # Обновляем базу данных с новым значением balance
    cursor.execute("UPDATE users SET page=? WHERE user_id=?", (new_page, user_id))

    # Сохраняем изменения в базе данных
    db.commit()


async def previous_page(user_id):
    cursor.execute("SELECT page FROM users WHERE user_id=?", (user_id,))
    current_page = cursor.fetchone()[0]

    # Вычисляем новое значение balance
    if current_page > 1:
        new_page = current_page - 2
    else:
        new_page = -1

    # Обновляем базу данных с новым значением balance
    cursor.execute("UPDATE users SET page=? WHERE user_id=?", (new_page, user_id))

    # Сохраняем изменения в базе данных
    db.commit()
