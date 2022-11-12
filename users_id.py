# импорт для работы с переменными окружения
from os import environ
from dotenv import load_dotenv

# классы для работы с каналами
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# Получение переменных окружения
load_dotenv()

# Присваиваем значения внутренним переменным
api_id = environ["API_ID"]
api_hash = environ["API_HASH"]
username = environ["USER_NAME"]

client = TelegramClient(username, api_id, api_hash)

client.start()


async def get_user_id(channel) -> None:
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

    all_users_details = set()  # список telegram id каждого пользователя

    for participant in all_participants:
        all_users_details.add(participant.id)

#     дописать сюда проверку


async def main():
    url = "https://t.me/+EMixgInnJWdlODU6"
    channel = await client.get_entity(url)
    await get_user_id(channel)


with client:
    client.loop.run_until_complete(main())
