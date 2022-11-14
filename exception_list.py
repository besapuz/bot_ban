from connect_db import connect_db

db = connect_db()


def get_telegram_id_chat_id(connection):
    try:
        # with connection.cursor() as cursor:
        # Записать данные
        #     sql = """UPDATE users SET except_chat='{-1001614832688, 30}'::bigint[] WHERE telegram_id=623614341"""
        # cursor.execute(sql, ('webmaster@python.org', 'very-secret'))
        #
        #     cursor.execute(sql)

        # connection is not autocommit by default. So you must commit to save
        # your changes.
        # connection.commit()

        with connection.cursor() as cursor:
            # Получить данные
            sql = f"""
                    SELECT except_chat 
                    FROM users 
                    WHERE telegram_id 
                    IN (623614341)"""
            cursor.execute(sql)
            result = cursor.fetchone()
            return result
    finally:
        connection.close()


if __name__ == "__main__":
    get_telegram_id_chat_id(db)
# UPDATE users SET except_chat='{-1001614832688, 30}'::bigint[] WHERE telegram_id=623614341