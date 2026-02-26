
"""
Module for handling non-menu/non-security related callbacks,
covering Network, AI, and Stats sections.
"""
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup
from homebot.core.mikrotik_api import MikroTikAPI
from homebot.core.shelly_api import ShellyAPI
from homebot.core.db_manager import DBManager

router = Router()

# Placeholder for shared objects that would normally be injected via middlewares or state.
mikrotik_stub = MikroTikAPI(host="10.10.100.20", username="admin", password="stub_password")
shelly_stub = ShellyAPI(ip_address="192.168.1.10")
db_manager_stub = DBManager()

@router.callback_query(lambda c: c.data == "network_menu")
async def network_menu_callback(callback: types.CallbackQuery):
    """
    Handles the callback query for the Network menu button. Stubs MikroTik interaction.
    """
    await callback.answer("Entering Network Configuration...")
    
    # Stub: Fetch network info
    interfaces = await mikrotik_stub.get_interface_list()
    
    # Log critical action (as per requirement)
    await db_manager_stub.log_critical_action(
        source="TelegramBot.SensorsHandler",
        action="ViewNetworkInfo",
        details=f"Fetched {len(interfaces)} interfaces"
    )
    
    # Placeholder response, will be updated later
    await callback.message.edit_text(
        f"You are in the Network section.\nFound interfaces: {', '.join([i['name'] for i in interfaces])}", 
        reply_markup=InlineKeyboardMarkup()
    )

@router.callback_query(lambda c: c.data == "ai_menu")
async def ai_menu_callback(callback: types.CallbackQuery):
    """
    Handles the callback query for the AI menu button.
    """
    await callback.answer("AI Services")
    await callback.message.edit_text(
        "You are in the AI section. Placeholder for future ML/AI services.",
        reply_markup=InlineKeyboardMarkup()
    )

@router.callback_query(lambda c: c.data == "stats_menu")
async def stats_menu_callback(callback: types.CallbackQuery):
    """
    Handles the callback query for the Stats menu button. Stubs Shelly interaction.
    """
    await callback.answer("Gathering Statistics...")
    
    # Stub: Get status from a Shelly device
    status = await shelly_stub.get_device_status()
    
    await callback.message.edit_text(
        f"You are in the Stats section.\nLast Shelly Status: {status['status']}",
        reply_markup=InlineKeyboardMarkup()
    )
