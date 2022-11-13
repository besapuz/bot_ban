from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from os import environ
load_dotenv()

storage = MemoryStorage()
bot = Bot(token=environ["TELEGRAM_TOKEN"])
dp = Dispatcher(bot, storage=storage)

