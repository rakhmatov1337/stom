from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    Message,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.filters import Command
from aiogram.enums import MenuButtonType
import asyncio

# Bot token and domain
TOKEN = "7780875320:AAF-xLME-WRTeqMu6XC_XuM5WZIxHGc8E1A"
DOMAIN = "https://stom-market.uz"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# In-memory dict to store user language temporarily
user_lang = {}

@dp.message(Command("start"))
async def choose_language(message: Message):
    lang_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            ]
        ]
    )
    await message.answer("Tilni tanlang / Выберите язык 👇", reply_markup=lang_kb)

@dp.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_lang[callback.from_user.id] = lang

    user_id = callback.from_user.id
    first_name = callback.from_user.first_name or ""
    auth_link = f"{DOMAIN}/accounts/telegram-auth/?token={user_id}&first_name={first_name}"

    # ✅ Set the menu button for this user
    await bot.set_chat_menu_button(
        chat_id=user_id,
        menu_button=types.MenuButtonWebApp(
            type=MenuButtonType.WEB_APP,
            text="🌐 Stom-market",
            web_app=WebAppInfo(url=auth_link)
        )
    )

    # ✅ Create regular keyboard (optional, like you're already doing)
    web_app_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌐 Stom-market", web_app=WebAppInfo(url=auth_link))]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    if lang == "uz":
        text = "👇 Davom etish uchun tugmani bosing:"
    else:
        text = "👇 Продолжить, нажав на кнопку:"

    await callback.message.answer(text, reply_markup=web_app_kb)
    await callback.answer()
async def language_selected(callback: types.CallbackQuery):
    lang = callback.data.split("_")[1]
    user_lang[callback.from_user.id] = lang

    user_id = callback.from_user.id
    first_name = callback.from_user.first_name or ""
    auth_link = f"{DOMAIN}/accounts/telegram-auth/?token={user_id}&first_name={first_name}"

    web_app_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌐 Stom-market", web_app=WebAppInfo(url=auth_link))]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    if lang == "uz":
        text = "👇 Davom etish uchun tugmani bosing:"
    else:
        text = "👇 Продолжить, нажав на кнопку:"

    await callback.message.answer(text, reply_markup=web_app_kb)
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
