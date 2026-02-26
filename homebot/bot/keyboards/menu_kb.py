
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def menu_keyboard():
    """
    Creates the main menu keyboard with Home, Security, Network, AI, and Stats buttons.
    """
    buttons = [
        [InlineKeyboardButton(text="Home", callback_data="home_menu")],
        [InlineKeyboardButton(text="Security", callback_data="security_menu")],
        [InlineKeyboardButton(text="Network", callback_data="network_menu")],
        [InlineKeyboardButton(text="AI", callback_data="ai_menu")],
        [InlineKeyboardButton(text="Stats", callback_data="stats_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
