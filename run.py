import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tortoise import Tortoise

from app.user.user_queries import user
from app.administrator.admin_queries import adm
from config import TOKEN, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
# from app.schedule import check_service_reminders, check_reminders, send_seasonal_notifications


logger = logging.getLogger(__name__)
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def startup(dispatcher: Dispatcher):
    await Tortoise.init(
        db_url=f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        # db_url=DB_URL,
        modules={"models": ["app.database.models"]},
    )
    await Tortoise.generate_schemas()

    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(check_service_reminders, "interval", hours=24)
    # scheduler.add_job(check_reminders, "interval", hours=24)
    # scheduler.add_job(
    #     send_seasonal_notifications, "cron", month="10", day="15", hour=9
    # )
    # scheduler.add_job(send_seasonal_notifications, "cron", month="4", day="15", hour=9)
    # scheduler.start()


async def shutdown(dispatcher: Dispatcher):
    await Tortoise.close_connections()
    exit(0)


async def main():
    dp = Dispatcher()
    dp.include_routers(user, adm)
    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
