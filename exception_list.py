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


# UPDATE users SET except_chat='{-1001614832688, 30}'::bigint[] WHERE telegram_id=
# SELECT except_chat FROM users WHERE telegram_id=