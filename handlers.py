# для работы с переменными окружения
from os import environ

from aiogram import Bot
from aiogram import types, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
# классы для работы с каналами
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from id_users import get_user_id
from keyboard_admin import button_case_admin

from connect_ad import connect_ad
from connect_db import connect_db
from connect_redis import connect_redis

# импорт для работы с переменными окружения
# Получение переменных окружения
from utils import check_users

load_dotenv()

REDIS_DB_URL = environ['REDIS_DB_URL']  # Адрес БД Redis
REDIS_DB_PORT = int(environ["REDIS_DB_PORT"])
URL_GROUP = environ['URL_GROUP']

# Подключение к БД и получение курсора
db = connect_db()
cursor = db.cursor()

# Подключение к redis
redis = connect_redis()

storage = RedisStorage2(REDIS_DB_URL, REDIS_DB_PORT, db=5, pool_size=10, prefix='my_fsm_key')
bot = Bot(token=environ["TELEGRAM_TOKEN"])
dp = Dispatcher(bot, storage=storage)

# Присваиваем значения внутренним переменным
api_id = environ["API_ID"]
api_hash = environ["API_HASH"]
phone = environ["PHONE"]

client = TelegramClient(phone, api_id, api_hash)
client.start()
ldap = connect_ad()
ADMIN_ID = None


class FSMAdmin(StatesGroup):
    EXCEPTION = State()
    EXCLUDE = State()
    DELETE = State()


async def exclude(massage: types.Message, state: FSMContext):
    global ADMIN_ID
    ADMIN_ID = massage.from_user.id
    await FSMAdmin.EXCLUDE.set()
    channel = await client.get_entity(URL_GROUP)
    get_user = await get_user_id(channel)
    chat_id = massage.chat.id
    await check_users(get_user, chat_id, ADMIN_ID)
    await state.finish()
    await massage.delete()


async def add_user_exception(massage: types.Message):
    await FSMAdmin.EXCEPTION.set()
    await massage.reply("Введите ID пользователя:")


async def exception(massage: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["EXCEPTION"] = massage.text  # добавлять в базу
    await bot.send_message(massage.from_user.id, f"Пользователь {data['EXCEPTION']} добавлен в исключения.",
                           reply_markup=button_case_admin)

    await state.finish()


async def delete_user_exception(massage: types.Message):
    await FSMAdmin.DELETE.set()
    await massage.reply("Введите ID пользователя:")


async def delete(massage: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["DELETE"] = massage.text
    await bot.send_message(massage.from_user.id, f"Пользователь {data['DELETE']} удален из списка исключений.",
                           reply_markup=button_case_admin)

    await state.finish()


async def cancel(massage: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    return await bot.send_message(massage.from_user.id, f"Действия отменены")


def register_handler_client(dp: Dispatcher):
    dp.register_message_handler(exclude, commands='moderator', is_chat_admin=True)
    dp.register_message_handler(cancel, state="*", commands='отмена')
    dp.register_message_handler(cancel, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(add_user_exception, commands='добавить')
    dp.register_message_handler(delete_user_exception, commands='удалить')
    dp.register_message_handler(exception, state=FSMAdmin.EXCEPTION)
    dp.register_message_handler(delete, state=FSMAdmin.DELETE)
