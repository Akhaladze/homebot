
import asyncio
import os
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from homebot.bot.handlers import start, security, sensors
from homebot.bot.keyboards.menu_kb import menu_keyboard

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

async def main():
    """
    Initializes and starts the Telegram bot.
    """
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"), parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Register all routers
    dp.include_router(start.router)
    dp.include_router(security.router)
    dp.include_router(sensors.router)

    # Set up main menu commands
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Start the bot and show main menu"),
        types.BotCommand(command="home", description="Go to Home section"),
        types.BotCommand(command="security", description="Go to Security section"),
        types.BotCommand(command="network", description="Go to Network configuration (Sensors)"),
        types.BotCommand(command="ai", description="Go to AI services (Sensors)"),
        types.BotCommand(command="stats", description="Go to device statistics (Sensors)"),
    ])

    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")
    except Exception as e:
        logging.error(f"Bot encountered an error: {e}")
