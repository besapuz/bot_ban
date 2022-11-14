from os import environ

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

load_dotenv()

api_id = environ["API_ID"]
api_hash = environ["API_HASH"]
phone = environ["PHONE"]

client = TelegramClient(phone, api_id, api_hash)
client.start()


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
