from os import environ

from aiogram import Bot
from aiogram import types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from dotenv import load_dotenv

# классы для работы с каналами
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from connect_ad import connect_ad

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


class FSMAdmin(StatesGroup):
    admin = State()


except_user = [5473542441, 196395317]  # список исключения


async def get_user_id(channel):
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


async def check_users(all_participants: list, chat_id):
    all_users_details = []  # список telegram id каждого пользователя

    for participant in all_participants:
        all_users_details.append({'id': participant.id, 'bot': participant.bot, "name": participant.username})

    for user_id in all_users_details:
        print(user_id)

        if not ldap.search('OU=Пользователи,OU=Учетные записи,OU=Технологии надежности,DC=reliab,DC=tech',
                           f"(&(objectClass=user)(telegram={user_id['id']}))", attributes=['memberOf']):

            if user_id['id'] in except_user:
                await bot.send_message(chat_id=623614341, text=f"Участник {user_id['id']} в списке исключения")
            else:
                await bot.kick_chat_member(chat_id, user_id['id'])
                await bot.unban_chat_member(chat_id, user_id['id'])
                await bot.send_message(chat_id=623614341,
                                       text=f"Участник id: {user_id['id']} name: {user_id['name']} исключен из группы")


async def main(massage: types.Message):
    url = "https://t.me/+EMixgInnJWdlODU6"
    channel = await client.get_entity(url)
    get_user = await get_user_id(channel)
    chat_id = massage.chat.id
    await check_users(get_user, chat_id)
    await massage.reply('Модерация')


def register_handler_client(dp: Dispatcher):
    dp.register_message_handler(main, commands=['start'])


async def on_startup(_):
    print("Бот вышел в эфир")


register_handler_client(dp)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
