from aiogram import types

kbd = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text="⚡️ Дізнатись погоду", callback_data="weather_check")],
    [types.InlineKeyboardButton(text="🏠 Головне меню", callback_data="menu")],
])

kbd2 = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text="⚡️ Дізнатись погоду", callback_data="weather_check")],
])