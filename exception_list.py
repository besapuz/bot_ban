from connect_db import connect_db

db = connect_db()


def get_except_chat_id(connection, telegram_id):
    try:
        with connection.cursor() as cursor:
            # Получить данные
            sql = f"""
                    SELECT except_chat 
                    FROM users 
                    WHERE telegram_id={telegram_id}
                    """
            cursor.execute(sql)
            result = cursor.fetchone()

    except Exception as e:
        return f"Error {e}"

    if result is None:
        return []
    else:
        return result[0]


def add_except_chat_id(connection, telegram_id, chat_id):
    print(telegram_id)
    try:
        with connection.cursor() as cursor:
            # Записать данные
            sql = f"""
                    UPDATE users 
                    SET except_chat='{chat_id}'::bigint[] 
                    WHERE telegram_id={telegram_id}
                    """
            cursor.execute(sql)
            connection.commit()

    except Exception as e:
        return f"Error {e}"


# e = get_except_chat_id(db, 623614341)
# print(e)
c = add_except_chat_id(db, 1210088598, {-1001614832688})
# e = get_except_chat_id(db, 196395317)
# print(e)

# UPDATE users SET except_chat='{-1001614832688, 30}'::bigint[] WHERE telegram_id=623614341
# SELECT except_chat FROM users WHERE telegram_id=623614341