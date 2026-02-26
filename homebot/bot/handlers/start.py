
from aiogram import Router, types
from aiogram.filters import Command
from homebot.bot.keyboards.menu_kb import menu_keyboard

router = Router()

@router.message(Command("start", "home"))
async def cmd_start(message: types.Message):
    """
    Handles the /start and /home commands, displaying the main menu.
    """
    await message.answer("Welcome Home!", reply_markup=menu_keyboard())

@router.callback_query(lambda c: c.data == "home_menu")
async def home_menu_callback(callback: types.CallbackQuery):
    """
    Handles the callback query for the Home menu button.
    """
    await callback.message.edit_text("You are in the Home section.", reply_markup=menu_keyboard())
    await callback.answer()
