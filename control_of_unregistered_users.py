# Методы из библиотеки для работы с Telegram ботом
import requests
import json
# Импорт наших модулей
from connect_db import connect_db

db = connect_db()
cursor = db.cursor()

not_registered_users = set()
not_registered_users.add(45158456)


def receiving_telegram_id() -> set: # получение списка id
    query = f"""
            SELECT telegram_id
             FROM users
    """
    cursor.execute(query)
    result = [record[0] for record in cursor.fetchall()]

    if result:
        return not_registered_users - set(result)


print(receiving_telegram_id())