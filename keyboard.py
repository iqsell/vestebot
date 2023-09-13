from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

catalog_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

catalog_keyboard.row(
    KeyboardButton(text="✅ Приобрести"),
)

catalog_keyboard.row(
    KeyboardButton(text="⬅️"),
    KeyboardButton(text="➡️")
)

help_buttons = [
    [InlineKeyboardButton(text="FAQ", callback_data="faq"),
     InlineKeyboardButton(text="Поддержка", callback_data="help_message"),],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
]


catalog_keyboard.add(
    KeyboardButton(text="🔙 Назад")
)

back_catalog_button = [
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_catalog")]
]

back_button = [
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
]

profile_menu = [
    [InlineKeyboardButton(text="📇 Профиль", callback_data="profile")],
     [InlineKeyboardButton(text="👕 Каталог", callback_data="catalog")],
     [InlineKeyboardButton(text="🔎 О проекте", callback_data="about_project"),
     InlineKeyboardButton(text="Поддержка 📖", callback_data="help_chat")]
]