import os
import telebot
import logging
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Получаем логгер, который будет перехвачен OTel
logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        token = os.getenv("TELEGRAM_TOKEN")
        if not token:
            logger.error("TELEGRAM_TOKEN is not set!")
            raise ValueError("TELEGRAM_TOKEN is missing")
        
        self.bot = telebot.TeleBot(token)
        self.webhook_url = os.getenv("WEBHOOK_URL", "https://api.cloudpak.info")
        self.allowed_users = [int(x) for x in os.getenv('ALLOWED_USERS', '0').split(',')]
        
        # Регистрируем обработчики сразу при инициализации
        self._register_handlers()
        logger.info("TelegramService initialized")

    def _is_authorized(self, user_id):
        if 0 in self.allowed_users: return True
        return user_id in self.allowed_users

    def _register_handlers(self):
        """Регистрация всех команд и callback-ов"""

        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            if not self._is_authorized(message.from_user.id):
                self.bot.reply_to(message, "⛔ Доступ запрещен.")
                return

            markup = InlineKeyboardMarkup(row_width=2)
            # Кнопка Mini App
            web_app_info = WebAppInfo(url=self.webhook_url) 
            btn_app = InlineKeyboardButton("🚀 Открыть Dashboard", web_app=web_app_info)
            
            # Обычные кнопки
            btn_cam = InlineKeyboardButton("📷 Камеры", callback_data='menu_cameras')
            btn_status = InlineKeyboardButton("ℹ️ Статус", callback_data='cmd_status')
            
            markup.add(btn_app)
            markup.add(btn_cam, btn_status)
            
            self.bot.send_message(
                message.chat.id, 
                f"Привет, {message.from_user.first_name}! 🏠\nУправление HomeBot:", 
                reply_markup=markup
            )

        @self.bot.message_handler(commands=['status'])
        def send_status(message):
            if not self._is_authorized(message.from_user.id): return
            self.bot.reply_to(message, "✅ Система работает.\nK3s Cluster: Online")

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            if not self._is_authorized(call.from_user.id): return
            
            logger.info(f"Button pressed: {call.data} by {call.from_user.username}")
            
            if call.data == 'cmd_status':
                self.bot.answer_callback_query(call.id, "Все системы в норме")
            elif call.data == 'menu_cameras':
                self.bot.answer_callback_query(call.id, "Функция в разработке")
            
    def process_update(self, json_string):
        """Метод вызывается из Flask webhook"""
        if not json_string:
            return
        update = telebot.types.Update.de_json(json_string)
        self.bot.process_new_updates([update])

    def setup_webhook(self):
        """Инициализация вебхука"""
        current_webhook = self.bot.get_webhook_info()
        target_url = f"{self.webhook_url}/webhook"
        
        if current_webhook.url != target_url:
            logger.info(f"Setting webhook to {target_url}")
            self.bot.remove_webhook()
            self.bot.set_webhook(url=target_url)
            return True
        return False

# Создаем экземпляр, но не инициализируем его глобально, если хотим ленивую загрузку.
# Но для простоты оставим создание здесь, оно упадет если нет токена.
try:
    tg_service = TelegramService()
except Exception as e:
    logger.warning(f"Telegram Service not started: {e}")
    tg_service = None
