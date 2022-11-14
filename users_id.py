# для работы с переменными окружения
from os import environ

from aiogram import Bot
from aiogram import types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv
# классы для работы с каналами
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from connect_ad import connect_ad
from keyboard_admin import button_case_admin

# импорт для работы с переменными окружения
# Получение переменных окружения
load_dotenv()

storage = MemoryStorage()
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


exception_users = [5473542441, 196395317]  # список исключения


async def get_user_id(channel) -> list:
    """Получает id всех пользователей канала"""
    offset_user = 0  # номер участника, с которого начинается считывание
    limit_user = 100  # максимальное число записей, передаваемых за один раз

    all_participants = []  # список всех участников канала
    filter_user = ChannelParticipantsSearch('')

    while True:
        participants = await client(GetParticipantsRequest(channel,
                                                           filter_user, offset_user, limit_user, hash=0))
        if not participants.users:
            break
        all_participants.extend(participants.users)
        offset_user += len(participants.users)
    return all_participants


async def check_users(all_participants: list, chat_id: int) -> None:
    all_users_details = []  # список telegram id каждого пользователя

    for participant in all_participants:
        all_users_details.append({'id': participant.id, 'bot': participant.bot, "name": participant.username})

    for user_id in all_users_details:
        if not ldap.search('OU=Пользователи,OU=Учетные записи,OU=Технологии надежности,DC=reliab,DC=tech',
                           f"(&(objectClass=user)(telegram={user_id['id']}))", attributes=['memberOf']):

            if user_id['id'] in exception_users:
                await bot.send_message(chat_id=ADMIN_ID,
                                       text=f"{user_id['id']} name: {user_id['name']} в списке исключения",
                                       reply_markup=button_case_admin)
            else:
                await bot.kick_chat_member(chat_id, user_id['id'])
                await bot.unban_chat_member(chat_id, user_id['id'])
                await bot.send_message(chat_id=ADMIN_ID,
                                       text=f"{user_id['id']} {user_id['name']} исключен из группы",
                                       reply_markup=button_case_admin)


# async def moderator(massage: types.Message):
#     await FSMAdmin.exception.set()
#     await massage.delete()
#     await bot.send_message(massage.from_user.id, "Что пожелаешь", reply_markup=button_case_admin)


async def exclude(massage: types.Message, state: FSMContext):
    global ADMIN_ID
    ADMIN_ID = massage.from_user.id
    url = "https://t.me/+EMixgInnJWdlODU6"
    await FSMAdmin.EXCLUDE.set()
    channel = await client.get_entity(url)
    get_user = await get_user_id(channel)
    chat_id = massage.chat.id
    await check_users(get_user, chat_id)
    await state.finish()
    await massage.delete()


async def add_user_exception(massage: types.Message):
    await FSMAdmin.EXCEPTION.set()
    await massage.reply("Введите ID пользователя:")


async def exception(massage: types.Message, state: FSMContext):
    exception_user_id = massage.text
    await state.finish()
    exception_users.append(exception_user_id)  # добавлять в базу
    await bot.send_message(massage.from_user.id, f"Пользователь {exception_user_id} добавлен в исключения.",
                           reply_markup=button_case_admin)


async def delete_user_exception(massage: types.Message):
    await FSMAdmin.DELETE.set()
    await massage.reply("Введите ID пользователя:")


async def delete(massage: types.Message, state: FSMContext):
    delete_user_id = massage.text
    delete_user_id = int(delete_user_id)
    await state.finish()
    exception_users.remove(delete_user_id)
    await bot.send_message(massage.from_user.id, f"Пользователь {delete_user_id} удален из списка исключений.",
                           reply_markup=button_case_admin)


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
