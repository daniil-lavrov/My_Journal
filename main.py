import asyncio
import datetime
import logging
import pytz
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aioredis import Redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
import text
from handlers import router
from db import Cursor

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

async def check_and_send(bot, config):
    with Cursor() as cur:
        count = len(cur.execute("SELECT user_id, time_zone, time_reminder FROM users").fetchall())
        for i in range(0, count):
            one_user = (cur.execute("SELECT user_id, time_zone, time_reminder FROM users").fetchall())[i]
            if datetime.datetime.now(pytz.timezone(one_user[1])).strftime('%H%M') == one_user[2]:
                try:
                    await bot.send_message(chat_id=one_user[0], text=text.reminder_text)
                except Exception as E:
                    pass


def set_scheduled_jobs(scheduler, bot, config, *args, **kwargs):
    # Добавляем задачи на выполнение

    scheduler.add_job(check_and_send, "interval", seconds=60, args=(bot, config))

async def main():

    scheduler = AsyncIOScheduler()
    set_scheduled_jobs(scheduler, bot, config)

    redis = Redis(host="redis", port=6379)

    dp = Dispatcher(storage=RedisStorage(redis=redis))
    dp.include_router(router)

    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
