
from aiogram import Router, types
from aiogram.filters import Command
from homebot.bot.keyboards.menu_kb import menu_keyboard

router = Router()

@router.message(Command("security"))
async def cmd_security(message: types.Message):
    """
    Handles the /security command, displaying the security menu.
    """
    await message.answer("Security options:", reply_markup=menu_keyboard())

@router.callback_query(lambda c: c.data == "security_menu")
async def security_menu_callback(callback: types.CallbackQuery):
    """
    Handles the callback query for the Security menu button.
    """
    await callback.message.edit_text("You are in the Security section.", reply_markup=menu_keyboard())
    await callback.answer()
