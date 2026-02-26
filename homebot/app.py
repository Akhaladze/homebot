import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Import handlers
from homebot.bot.handlers import start, security, sensors

# Load environment variables
load_dotenv()

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://api.cloudpak.info")
WEBHOOK_PATH = "/webhook/telegram"
FULL_WEBHOOK_URL = f"{WEBHOOK_URL}{WEBHOOK_PATH}"

# --- Bot & Dispatcher Setup ---
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Register routers
dp.include_router(start.router)
dp.include_router(security.router)
dp.include_router(sensors.router)

async def set_webhook(bot: Bot):
    """
    Sets the Telegram webhook on startup.
    """
    logger.info(f"Setting webhook to {FULL_WEBHOOK_URL}")
    await bot.set_webhook(FULL_WEBHOOK_URL)

async def delete_webhook(bot: Bot):
    """
    Removes the Telegram webhook on shutdown.
    """
    logger.info("Removing webhook")
    await bot.delete_webhook()

async def on_startup(app: web.Application):
    """
    Startup event handler.
    """
    await set_webhook(bot)
    # Set bot commands
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Start the bot and show main menu"),
        types.BotCommand(command="home", description="Go to Home section"),
        types.BotCommand(command="security", description="Go to Security section"),
        types.BotCommand(command="network", description="Go to Network configuration (Sensors)"),
        types.BotCommand(command="ai", description="Go to AI services (Sensors)"),
        types.BotCommand(command="stats", description="Go to device statistics (Sensors)"),
    ])

async def on_shutdown(app: web.Application):
    """
    Shutdown event handler.
    """
    await delete_webhook(bot)

# --- Routes ---
async def index(request):
    """
    Root endpoint to verify server status.
    """
    logger.info("Index page accessed")
    return web.json_response({"status": "running", "mode": "aiohttp"})

async def health_check(request):
    """
    Health check endpoint for container orchestration.
    """
    return web.json_response({"status": "ok"})

# --- App Factory ---
def create_app():
    """
    Creates and configures the aiohttp application.
    """
    app = web.Application()
    
    # Register startup/shutdown handlers
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # Setup routes
    app.router.add_get("/", index)
    app.router.add_get("/health", health_check)
    
    # Setup aiogram webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Mount dispatcher to app (for dependency injection if needed later)
    setup_application(app, dp, bot=bot)
    
    return app

# if __name__ == "__main__":
#    app = create_app()
#    web.run_app(app, host="0.0.0.0", port=5000)
