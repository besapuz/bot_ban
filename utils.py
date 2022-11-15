from os import environ

from aiogram import Dispatcher
from aiogram import Bot
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from connect_ad import connect_ad
from connect_db import connect_db
from exception_list import get_except_chat_id
from keyboard_admin import button_case_admin

REDIS_DB_URL = environ['REDIS_DB_URL']  # Адрес БД Redis
REDIS_DB_PORT = int(environ["REDIS_DB_PORT"])
BOT_ID = int(environ["BOT_ID"])

storage = RedisStorage2(REDIS_DB_URL, REDIS_DB_PORT, db=5, pool_size=10, prefix='my_fsm_key')
bot = Bot(token=environ["TELEGRAM_TOKEN"])
dp = Dispatcher(bot, storage=storage)

db = connect_db()
ldap = connect_ad()


async def check_users(all_participants: list, chat_id: int, admin_id: int) -> None:
    all_users_details = []  # список telegram id каждого пользователя
    for participant in all_participants:
        all_users_details.append({'id': participant.id, 'bot': participant.bot, "name": participant.username})

    for user_id in all_users_details:
        # if not ldap.search('OU=Пользователи,OU=Учетные записи,OU=Технологии надежности,DC=reliab,DC=tech',
        #                    f"(&(objectClass=user)(telegram={user_id['id']}))", attributes=['memberOf']):

        except_user = get_except_chat_id(db, user_id['id'])   # кортеж исключений из ID чатов
        if user_id["id"] == BOT_ID:
            continue

        elif chat_id in except_user:
            await bot.send_message(chat_id=admin_id,
                                   text=f"{user_id['id']} name: {user_id['name']} в списке исключения",
                                   reply_markup=button_case_admin)

        elif user_id['id'] == admin_id:
            await bot.send_message(chat_id=admin_id,
                                   text=f"{user_id['id']} name: {user_id['name']} администратор чата",
                                   reply_markup=button_case_admin)

        else:
            try:
                await bot.unban_chat_member(chat_id, user_id['id'])
                await bot.send_message(chat_id=admin_id,
                                       text=f"{user_id['id']} {user_id['name']} исключен из группы",
                                       reply_markup=button_case_admin)
            except Exception as e:
                continue
