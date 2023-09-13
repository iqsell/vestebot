import logging
import time

from db import db_start, create_profile, add_product, get_user, update_user_data, get_product, next_page, previous_page, \
    set_page
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from aiogram.types.input_media import InputMedia, MediaGroup, InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from keyboard import profile_menu, back_button, catalog_keyboard, back_catalog_button, help_buttons
import config
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

# log
logging.basicConfig(level=logging.INFO)

# init
storage = MemoryStorage()
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=storage)

# prices
PRICE = types.LabeledPrice(label="Футболка ", amount=1500 * 100)  # в копейках (руб)


class UserState(StatesGroup):
    new_information = State()
    help_chat = State()


class AdminState(StatesGroup):
    new_product = State()


async def on_startup(_):
    await db_start()


# start
@dp.message_handler(commands=['start'])
async def buy(message: types.Message):
    # GOODS: id, count
    await create_profile(message.from_user.id)
    await bot.send_message(message.chat.id,
                           f'Привет, я бот через которого вы можете купить наши вещи!\n Для начала покупок введите /menu')


@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    profile_keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=profile_menu)
    await bot.send_message(message.chat.id, "📋 Выберите нужную вам функцию бота и нажмите на клавишу:",
                           reply_markup=profile_keyboard)


@dp.message_handler(text="🔙 Назад")
async def menu_back(message: types.Message):
    profile_keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=profile_menu)
    await bot.send_message(message.chat.id, text="🧹 Чистим клавиатуры", reply_markup=ReplyKeyboardRemove())
    time.sleep(0.1)
    await bot.send_message(chat_id=message.from_user.id, text="MENU\n",
                           reply_markup=profile_keyboard)


@dp.message_handler(commands=['catalog'])
async def back_to_catalog(callback: types.CallbackQuery):
    user_data = await get_user(callback.from_user.id)
    media = MediaGroup()
    product_card = await get_product(user_data['page'] + 1)
    media.attach_photo(photo=f"{product_card['image_link']}", caption=f"{product_card['product']}")
    product_card = await get_product(user_data['page'] + 2)
    media.attach_photo(photo=f"{product_card['image_link']}", caption=f"{product_card['product']}")
    await bot.send_message(callback.from_user.id, text="🔄 Каталог загружается 🔄", reply_markup=catalog_keyboard)
    time.sleep(0.1)
    await bot.send_media_group(callback.from_user.id, media=media)
    # callback.message.edit_media(InputMedia(f"{product_card['image_link']}", caption=f"{product_card['product']


""" под второй товар
@dp.message_handler(text="2️⃣")
async def first_product(message: types.Message):
    back_catalog = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=back_catalog_button)
    await bot.send_message(message.chat.id, text="💳 Готовим реквизиты к оплате", reply_markup=ReplyKeyboardRemove())
    user_data = await get_user(message.from_user.id)
    product_card = await get_product(user_data['page'] + 2)
    await bot.send_invoice(message.chat.id,
                           title="Покупка вещи",
                           description=f"Купить {product_card['product']}",
                           provider_token=config.PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url=product_card['image_link'],
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")
    await bot.send_message(message.chat.id, text="Для выхода обратно в каталог введите /catalog")
"""


@dp.message_handler(text="✅ Приобрести")
async def first_product(message: types.Message):
    back_catalog = InlineKeyboardMarkup(resize_keyboard=True).add(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_catalog"))  # inline_keyboard=back_catalog_button)
    await bot.send_message(message.chat.id, text="💳 Готовим реквизиты к оплате", reply_markup=ReplyKeyboardRemove())
    time.sleep(0.1)

    user_data = await get_user(message.from_user.id)
    product_card = await get_product(user_data['page'] + 1)
    await bot.send_invoice(message.chat.id,
                           title="Покупка вещи",
                           description=f"Купить {product_card['product']}",
                           provider_token=config.PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url=f"{product_card['image_link']}",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")
    await bot.send_message(message.chat.id, text="Для возврата в каталог введите /catalog")


@dp.callback_query_handler(text='back_to_menu')
async def menu_callback(callback: types.CallbackQuery):
    profile_keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=profile_menu)
    await callback.message.edit_text("MENU\n", reply_markup=profile_keyboard)


@dp.message_handler(commands=['new_product'])
async def new_product(message: types.Message, state: FSMContext):
    if message.from_user.id in config.sellers:
        await bot.send_message(message.chat.id,
                               "Введите параметры нового товара(название, ссылка на картинку, описание)")
        await AdminState.new_product.set()
    else:
        await bot.send_message(message.chat.id,
                               "У вас нет прав на использование этой команды")


@dp.message_handler(state=AdminState.new_product)
async def new_product2(message: types.Message, state: FSMContext):
    product_data = message.text.split(', ', maxsplit=2)
    await state.finish()
    await add_product(product_data[0], product_data[1], product_data[2])


@dp.callback_query_handler(text='profile')
async def profile(callback: types.CallbackQuery, state: FSMContext):
    user_data = await get_user(callback.from_user.id)
    back_keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=back_button).add(
        InlineKeyboardButton(text="Заполнить информацию", callback_data="give_information"))

    try:
        await callback.message.edit_text(f"🪪 ID: {user_data['user_id']}\n\n"
                                         f"👤 ФИО: {user_data['username'] if user_data['username'] else 'не заполнено'}\n\n"
                                         f"🏠 Адрес: {user_data['adress'] if user_data['adress'] else 'не заполнено'}\n\n"
                                         f"📪 Индекс: {user_data['indx'] if user_data['indx'] else 'не заполнено'}\n\n"
                                         f"☎️ Номер телефона: {user_data['phone_number'] if user_data['phone_number'] else 'не заполнено'}\n\n"
                                         f"🛒 Всего покупок: {user_data['order_value']}\n\n"
                                         f"🔥 Персональная скидка: {user_data['personal_sale']}%\n\n"
                                         f"🗒 Примечания: {user_data['notes'] if user_data['notes'] else 'не заполнено'}",
                                         reply_markup=back_keyboard)
    except:
        await callback.edit_text(f"🪪 ID: {user_data['user_id']}\n\n"
                                 f"👤 ФИО: {user_data['username'] if user_data['username'] else 'не заполнено'}\n\n"
                                 f"🏠 Адрес: {user_data['adress'] if user_data['adress'] else 'не заполнено'}\n\n"
                                 f"📪 Индекс: {user_data['indx'] if user_data['indx'] else 'не заполнено'}\n\n"
                                 f"☎️ Номер телефона: {user_data['phone_number'] if user_data['phone_number'] else 'не заполнено'}\n\n"
                                 f"🛒 Всего покупок: {user_data['order_value']}\n\n"
                                 f"🔥 Персональная скидка: {user_data['personal_sale']}\n\n"
                                 f"🗒 Примечания: {user_data['notes'] if user_data['notes'] else 'не заполнено'}",
                                 reply_markup=back_keyboard)


@dp.callback_query_handler(text='give_information')
async def give_information(callback: types.CallbackQuery):
    user_data = await get_user(callback.from_user.id)
    kb = [[]]
    text = False
    for i in user_data.items():
        if i[0] == "phone_number":
            text = "Номер телефона"
        elif i[0] == "username":
            text = "ФИО"
        elif i[0] == "adress":
            text = "Адрес"
        elif i[0] == "indx":
            text = 'Индекс'
        elif i[0] == "notes":
            text = "Примечания"
        if text:
            kb[0].append(InlineKeyboardButton(text=f"{text}", callback_data=f"new_data:{text}"))
        text = False
    information_keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=kb)
    information_keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="profile"))
    try:
        await callback.message.edit_text("Заполните информацию", reply_markup=information_keyboard)
    except:
        await callback.edit_text("Заполните информацию", reply_markup=information_keyboard)


@dp.callback_query_handler(text_startswith='new_data:')
async def send_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(f"Введите свой {callback.data[9:]}" if callback.data[9:] == "Примечания" else "Напишите Примечания")
    await UserState.new_information.set()
    await state.update_data(type=callback.data[9:])


@dp.message_handler(state=UserState.new_information)
async def enter_new_inf(message: types.Message, state: FSMContext):
    message_data = message.text
    type = await state.get_data()
    if type['type'] == 'Номер телефона':
        update_user_data(message.from_user.id, phone_number=message_data)
    elif type['type'] == 'ФИО':
        update_user_data(message.from_user.id, username=message_data)
    elif type['type'] == 'Адрес':
        update_user_data(message.from_user.id, address=message_data)
    elif type['type'] == 'Индекс':
        update_user_data(message.from_user.id, indx=message_data)
    elif type['type'] == 'Примечания':
        update_user_data(message.from_user.id, notes=message_data)
    await state.finish()
    msg_call = await bot.send_message(message.from_user.id, '·')
    msg_call['from']['id'] = message.from_user.id
    await give_information(msg_call)


@dp.callback_query_handler(text='catalog')
async def catalog(callback: types.CallbackQuery):
    await set_page(callback.from_user.id, -1)
    user_data = await get_user(callback.from_user.id)
    media = MediaGroup()
    product_card = await get_product(user_data['page'] + 1)
    media.attach_photo(photo=f"{product_card['image_link']}", caption=f"{product_card['product']}")
    product_card = await get_product(user_data['page'] + 2)
    media.attach_photo(photo=f"{product_card['image_link']}", caption=f"{product_card['product']}")
    await bot.send_message(callback.from_user.id, text="🔄 Каталог обновляется 🔄", reply_markup=catalog_keyboard)
    time.sleep(0.1)

    await bot.send_media_group(callback.from_user.id, media=media)
    # callback.message.edit_media(InputMedia(f"{product_card['image_link']}", caption=f"{product_card['product']}"), reply_markup=catalog_keyboard)


# next page
@dp.message_handler(text="➡️")
async def next_pages(message: types.Message):
    media = MediaGroup()
    await next_page(message.from_user.id)
    user_data = await get_user(message.from_user.id)
    product_card = await get_product(user_data['page'] + 1)
    media.attach_photo(photo=f"{product_card['image_link']}", caption=f"{product_card['product']}")
    product_card = await get_product(user_data['page'] + 2)
    media.attach_photo(photo=f"{product_card['image_link']}", caption=f"{product_card['product']}")
    await bot.send_media_group(message.from_user.id, media=media)


@dp.message_handler(text="⬅️")
async def prev_pages(message: types.Message):
    media = MediaGroup()
    await previous_page(message.from_user.id)
    user_data = await get_user(message.from_user.id)
    product_card = await get_product(user_data['page'] + 1)
    media.attach_photo(photo=f"{product_card['image_link']}", caption=f"{product_card['product']}")
    product_card = await get_product(user_data['page'] + 2)
    media.attach_photo(photo=f"{product_card['image_link']}", caption=f"{product_card['product']}")
    await bot.send_media_group(message.from_user.id, media=media)


@dp.callback_query_handler(text='about_project')
async def about_project(callback: types.CallbackQuery):
    back_keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=back_button)
    await callback.message.edit_text(
        f"Мы создатели бренда Veste Никита и Саша.\n<b>История создания:</b>\nМы знакомы и общаемся очень давно и"
        f" в моменте пришла идея сделать свой"
        f" бренд одежды и мы решили заняться этим"
        f"Сделали бота,"
        f" наняли творческих\nхудожников работающих за респект (Кристина\nспасибо), нашли фабрики с лучшим "
        f"качеством\n(ведь и сами их носим) и рады представить\nвам наши вещи. В каждый принт вложена "
        f"своя(и)\nидея(и) и эмоции, но вы в праве сами решать,\nчто чувствуете глядя на них, хотя для каждой"
        f"\nработы есть свое описание. Выбирайте лучшее,\nвыбирайте <i>veste!</i>\n\n<a href='t.me/vestej'>Наш канал</a>",
        parse_mode="HTML", reply_markup=back_keyboard)


@dp.callback_query_handler(text='help_chat')
async def help_chat(callback: types.CallbackQuery):
    help_keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=help_buttons)
    await callback.message.edit_text("Выберите раздел:\n", reply_markup=help_keyboard)


@dp.callback_query_handler(text='help_message')
async def help_chat(callback: types.CallbackQuery):
    back_keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=back_button)
    await callback.message.edit_text("Напишите свой вопрос, и наш менеджер поможет вам", reply_markup=back_keyboard)
    await UserState.help_chat.set()

@dp.callback_query_handler(text='faq')
async def about_project(callback: types.CallbackQuery):
    back_keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=back_button)
    await callback.message.edit_text(
        f"<a href='t.me/vestej'>Наш канал</a>",
        parse_mode="HTML", reply_markup=back_keyboard)

@dp.message_handler(state=UserState.help_chat)
async def help_redirect(message: types.Message, state: FSMContext):
    await bot.forward_message(config.admins[0], message.chat.id, message.message_id)
    time.sleep(0.1)
    await message.answer("Ваше обращение было отправлено в поддержку, ожидайте ответа")
    await state.finish()


# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    # PROMO: promo_code, count (default 1)
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    # ORDERS: payment_id / user_id / status
    message_reply = await bot.send_message(message.chat.id,
                                           f"✅ Платёж на сумму {message.successful_payment.total_amount // 100} "
                                           f"{message.successful_payment.currency} прошел успешно!"
                                           f"\n\nС вами скоро свяжутся для уточнения деталей заказа")


@dp.message_handler(content_types=ContentType.CONTACT)
async def contact(message: types.Message):
    # TODO check order
    await send_message_to_logs(message)


async def send_message_to_logs(message: types.Message):
    await bot.forward_message(1001838206565, message.chat.id, message.message_id)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
