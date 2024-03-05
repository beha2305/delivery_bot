from dostavka import Database
from telegram import (Update, KeyboardButton, InlineKeyboardButton,
                      ReplyKeyboardMarkup, InlineKeyboardMarkup)
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters, CallbackQueryHandler)
from datetime import datetime
db = Database()


async def start(update, context):
    user = update.message.from_user
    user_data = db.get_user(user.id)
    db.add_bucket(user.id)
    if not user_data:
        db.add_user(chat_id=user.id, tg_firstname=user.first_name, tg_username=user.username)
        user_data = db.get_user(user.id)
    if not user_data["lang"]:

        buttons = [
            [
                InlineKeyboardButton(text="english🇬🇧󠁧󠁢󠁥󠁮", callback_data="lang_1"),
                InlineKeyboardButton(text="russian🇷🇺", callback_data="lang_2"),
                InlineKeyboardButton(text="uzbek🇺🇿", callback_data="lang_3")
            ]
        ]
        db.add_log(user_data["id"], log="1")
        await update.message.reply_text(f'{update.effective_user.first_name} Tilni tanlang',
                                        reply_markup=InlineKeyboardMarkup(buttons))
    elif not user_data["fullname"]:
        db.add_log(user_id=user_data['id'], log="2")
        await update.message.reply_text("ismingizni kiriting: ")
    elif not user_data["phone_number"]:
        phone_button = [
            [
                KeyboardButton("Share contact📱", request_contact=True)
            ]
        ]
        await update.message.reply_text(f"Iltimos telefon raqamingizni +998********* ko'rinishda kiriting",
                                        reply_markup=ReplyKeyboardMarkup(phone_button, resize_keyboard=True))
    else:
        setting_button = [
            [
                KeyboardButton(text='Buyurtma berish')
            ],
            [
                KeyboardButton(text="Buyurtmalar tarixi"),
                KeyboardButton(text="Manzillarimiz")
            ],
            [
                KeyboardButton("🔴Biz haqimizda🔴"),
                KeyboardButton("Sozlamalar⚙️")
            ]
        ]
        db.add_log(user_id=user_data['id'], log="4")
        await update.message.reply_text(f"Assalomu aleykum, xush kelibsiz!",
                                        reply_markup=ReplyKeyboardMarkup(setting_button, resize_keyboard=True,
                                                                         one_time_keyboard=True))


async def message(update, context):
    id = update.message.from_user.id
    # print(id)
    msg = update.message.text
    user_data = db.get_user(id)["id"]
    # print(user_data)
    log = db.get_log(user_data)["log"]
    if int(log) == 2:
        db.add_user(chat_id=id, fullname=msg)
        db.add_log(user_data, log="3")
        phone_button = [
            [
                KeyboardButton("Share contact📱", request_contact=True)
            ]
        ]
        await update.message.reply_text(f"Iltimos telefon raqamingizni +998********* ko'rinishda kiriting",
                                        reply_markup=ReplyKeyboardMarkup(phone_button, resize_keyboard=True))
    elif int(log) == 3:
        s = False
        for i in range(4, len(msg)):
            if ord(msg[i]) > 47 and ord(msg[i]) < 58:
                s = True
        if msg[:5] == '+998' and len(msg) == 13 and s == True:
            db.add_user(chat_id=id, phone_number=msg)
            db.add_log(user_data, log="4")
            setting_button = [
                [
                    KeyboardButton(text='Buyurtma berish')
                ],
                [
                    KeyboardButton(text="Buyurtmalar tarixi"),
                    KeyboardButton(text="Manzillarimiz")
                ],
                [
                    KeyboardButton("🔴Biz haqimizda🔴"),
                    KeyboardButton("Sozlamalar⚙️")
                ]
            ]
            await update.message.reply_text(f"Siz muvaffaqiyatli ro'yxatdan o'tdingiz",
                                            reply_markup=ReplyKeyboardMarkup(setting_button, resize_keyboard=True,
                                                                             one_time_keyboard=True))
        else:
            await update.message.reply_text("Telefon raqam noto'g'ri kiritilgan, iltimos qaytadan yuboring")
    elif int(log) == 4:
        if msg == "Buyurtma berish":
            db.add_log(user_id=user_data, log="5")
            categories = db.get_category()
            category_button = []
            temp_button = []
            for category in categories:
                temp_button.append(
                    InlineKeyboardButton(text=f"{category['name']}", callback_data=f"category_{category['id']}"))
                if len(temp_button) == 2:
                    category_button.append(temp_button)
                    temp_button = []
            if len(temp_button) == 1:
                category_button.append(temp_button)
            category_button.append([InlineKeyboardButton(text="Asosiy menu", callback_data="main_menu")])
            await update.message.reply_text("Kategoriyalardan birini tanlang. (https://telegra.ph/Taomnoma-09-30)",
                                            reply_markup=InlineKeyboardMarkup(category_button))
    if msg == "Buyurtmalar tarixi":
        orders = db.get_orders(id)
        print(orders[0]['id'])
        i = 0
        info = ''
        price = 0
        for order_id in orders:
            order_items = db.get_order_item(order_id['id'])
            print(order_items)
            product_id = order_items[0]['product_id']
            count = order_items[0]['count']
            product_name = db.get_productinfo(product_id)
            info += f"{product_name['name']} X{count}\n"
            price += product_name['price'] * count
            i += 1
            # print(order_items)
        await update.message.reply_text(f"{info}\nTotal price: {price}")


async def contact(update, context):
    phone_number = update.message.contact.phone_number
    id = update.message.from_user.id
    user_data = db.get_user(id)["id"]
    db.add_user(chat_id=id, phone_number=phone_number)
    db.add_log(user_data, log="4")
    setting_button = [
        [
            KeyboardButton(text='Buyurtma berish')
        ],
        [
            KeyboardButton(text="Buyurtmalar tarixi"),
            KeyboardButton(text="Manzillarimiz")
        ],
        [
            KeyboardButton("🔴Biz haqimizda🔴"),
            KeyboardButton("Sozlamalar⚙️")
        ]
    ]
    await update.message.reply_text(f"Siz muvaffaqiyatli ro'yxatdan o'tdingiz",
                                    reply_markup=ReplyKeyboardMarkup(setting_button, resize_keyboard=True,
                                                                     one_time_keyboard=True))


async def callback(update, context):
    id = update.callback_query.from_user.id
    user = update.callback_query.from_user
    user_data = db.get_user(id)["id"]
    msg = update.callback_query.data.split("_")
    message_id = update.callback_query.message.message_id
    if msg[0] == "lang":
        db.add_user(chat_id=user.id, lang=msg[1])
        db.add_log(user_data, log="2")
        await context.bot.delete_message(chat_id=user.id, message_id=message_id)
        await update.callback_query.message.reply_text("ismingizni kiriting: ")

    elif msg[0] == "category":
        db.add_log(user_id=user_data, log="6")
        products = db.get_product(f"{int(msg[1])}")
        product_button = []
        temp_button = []
        for product in products:
            temp_button.append(
                InlineKeyboardButton(text=f"{product['name']}", callback_data=f"product_{product['id']}"))
            if len(temp_button) == 2:
                product_button.append(temp_button)
                temp_button = []
        if len(temp_button) == 1:
            product_button.append(temp_button)
        product_button.append([InlineKeyboardButton(text="⬅️back", callback_data="product_back")])
        category_photo = products[0]['category_photo']
        category_name = products[0]['category_name']
        await context.bot.delete_message(chat_id=id, message_id=message_id)
        await update.callback_query.message.reply_photo(photo=open(f"{category_photo}", "rb"),
                                                        caption=category_name,
                                                        reply_markup=InlineKeyboardMarkup(product_button))
    elif msg[0] == 'product':
        if msg[1] == "back":
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            db.add_log(user_id=user_data, log="5")
            categories = db.get_category()
            category_button = []
            temp_button = []
            for category in categories:
                temp_button.append(
                    InlineKeyboardButton(text=f"{category['name']}", callback_data=f"category_{category['id']}"))
                if len(temp_button) == 2:
                    category_button.append(temp_button)
                    temp_button = []
            if len(temp_button) == 1:
                category_button.append(temp_button)
            category_button.append([InlineKeyboardButton(text="Asosiy menu", callback_data="main_menu")])
            await update.callback_query.message.reply_text(
                "Kategoriyalardan birini tanlang. (https://telegra.ph/Taomnoma-09-30)",
                reply_markup=InlineKeyboardMarkup(category_button))
        else:
            db.add_log(user_id=user_data, log="7")
            product = db.get_productinfo(product_id=msg[1])
            product_photo = product['photo']
            product_name = product['name']
            product_price = product['price']
            product_description = product['description']
            quantity = 1
            product_button = [
                [
                    InlineKeyboardButton(text="➖", callback_data=f"detail_minus_{product['id']}_{quantity}"),
                    InlineKeyboardButton(text=f"{quantity}", callback_data=f"detail_1_{product['id']}_{quantity}"),
                    InlineKeyboardButton(text="➕", callback_data=f"detail_plus_{product['id']}_{quantity}")
                ],
                [
                    InlineKeyboardButton(text="🛒Savatga qo'shish", callback_data=f"detail_bucket_{product['id']}_{quantity}")
                ],
                [
                    InlineKeyboardButton(text="⬅️back", callback_data=f"detail_back_{product['id']}_{product['category_id']}")
                ]
            ]
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            await update.callback_query.message.reply_photo(photo=open(f"{product_photo}", "rb"),
                                                            caption=f"{product_name}\n"
                                                                    f"Narxi: {product_price}\n{product_description}",
                                                            reply_markup=InlineKeyboardMarkup(product_button))
    elif msg[0] == "detail":
        if msg[1] == "back":
            db.add_log(user_id=user_data, log="6")
            products = db.get_product(f"{int(msg[2])}")
            product_button = []
            temp_button = []
            for product in products:
                temp_button.append(InlineKeyboardButton(text=f"{product['name']}", callback_data=f"product_{product['id']}"))
                if len(temp_button) == 2:
                    product_button.append(temp_button)
                    temp_button = []
            if len(temp_button) == 1:
                product_button.append(temp_button)
            product_button.append([InlineKeyboardButton(text="⬅️back", callback_data="product_back")])
            category_photo = products[0]['category_photo']
            category_name = products[0]['category_name']
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            await update.callback_query.message.reply_photo(photo=open(f"{category_photo}", "rb"),
                                                            caption=category_name,
                                                            reply_markup=InlineKeyboardMarkup(product_button))
        elif msg[1] == "minus" and int(msg[3]) >1 :
            product = db.get_productinfo(product_id=msg[2])
            product_name = product['name']
            product_price = product['price']
            product_description = product['description']
            quantity = int(msg[3]) - 1
            product_button = [
                [
                    InlineKeyboardButton(text="➖", callback_data=f"detail_minus_{product['id']}_{quantity}"),
                    InlineKeyboardButton(text=f"{quantity}", callback_data=f"detail_1_{product['id']}_{quantity}"),
                    InlineKeyboardButton(text="➕", callback_data=f"detail_plus_{product['id']}_{quantity}")
                ],
                [
                    InlineKeyboardButton(text="🛒Savatga qo'shish",
                                         callback_data=f"detail_bucket_{product['id']}_{quantity}")
                ],
                [
                    InlineKeyboardButton(text="⬅️back", callback_data=f"detail_back_{product['category_id']}")
                ]
            ]
            await context.bot.edit_message_caption(chat_id=id, message_id=message_id,
                                                        caption=f"{product_name}\n"
                                                                f"Narxi: {product_price * quantity}\n{product_description}",
                                                        reply_markup=InlineKeyboardMarkup(product_button))
        elif msg[1] == "plus" :
            product = db.get_productinfo(product_id=msg[2])
            product_name = product['name']
            product_price = product['price']
            product_description = product['description']
            quantity = int(msg[3]) + 1
            product_button = [
                [
                    InlineKeyboardButton(text="➖", callback_data=f"detail_minus_{product['id']}_{quantity}"),
                    InlineKeyboardButton(text=f"{quantity}", callback_data=f"detail_1_{product['id']}_{quantity}"),
                    InlineKeyboardButton(text="➕", callback_data=f"detail_plus_{product['id']}_{quantity}")
                ],
                [
                    InlineKeyboardButton(text="🛒Savatga qo'shish",
                                         callback_data=f"detail_bucket_{product['id']}_{quantity}_{product['category_id']}")
                ],
                [
                    InlineKeyboardButton(text="⬅️back", callback_data=f"detail_back_{product['category_id']}")
                ]
            ]
            await context.bot.edit_message_caption(chat_id=id, message_id=message_id,
                                                        caption=f"{product_name}\n"
                                                                f"Narxi: {product_price * quantity}\n{product_description}",
                                                        reply_markup=InlineKeyboardMarkup(product_button))
        elif msg[1] == "bucket":
            bucket_id = db.get_bucket_id(chat_id= id)["id"]
            print(msg)
            db.add_item(bucket_id,int(msg[2]), int(msg[3]))
            categories = db.get_category()
            category_button = []
            temp_button = []
            for category in categories:
                temp_button.append(
                    InlineKeyboardButton(text=f"{category['name']}", callback_data=f"category_{category['id']}"))
                if len(temp_button) == 2:
                    category_button.append(temp_button)
                    temp_button = []
            if len(temp_button) == 1:
                category_button.append(temp_button)
            category_button.append([InlineKeyboardButton(text= "Savatcha", callback_data= f"Savatcha_{int(msg[2])}_{int(msg[3])}")])
            category_button.append([InlineKeyboardButton(text= "⬅️back", callback_data= f"Savatcha_back_{int(msg[2])}_{int(msg[3])}")])
            category_button.append([InlineKeyboardButton(text="Asosiy menu", callback_data="main_menu")])
            products = db.get_item(bucket_id=bucket_id)
            text = ''
            price = 0
            for product in products:
                text +=f"{str(product['count'])}x {product['item_name']}\n"
                price += int(product['item_price'])
            bucket_info = f"Savatchada\n{text}\nProducts: {price}\nDelivery: {price//3}\nTotal: {price + price//3}"
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            await update.callback_query.message.reply_text(bucket_info,
                                                            reply_markup=InlineKeyboardMarkup(category_button))
    elif msg[0] == "Savatcha":
        if msg[1] != "back" and msg[1] != "plus" and msg[1] != "minus":
            bucket_id = db.get_bucket_id(id)['id']
            products = db.get_item(bucket_id)
            text = ''
            price = 0
            bucket_button = [
                [
                    InlineKeyboardButton(text="⬅️back", callback_data=f"Savatcha_back_{int(msg[1])}_{int(msg[2])}"),
                    InlineKeyboardButton(text="Buyurtma berish", callback_data="Buyurtma_qilish1")
                ],
                [
                    InlineKeyboardButton(text="Savatni bo'shatish", callback_data="clear_bucket")
                ]
            ]
            for product in products:
                text += f"{str(product['count'])}x {product['item_name']}\n"
                text2 = product['item_name']
                price += int(product['item_price'])
                bucket_button.append([
                    InlineKeyboardButton(text="➖", callback_data=f"Savatcha_minus_{product['product_id']}_{product['count']}"),
                    InlineKeyboardButton(text= f"{text2}", callback_data= "product"),
                    InlineKeyboardButton(text="➕", callback_data=f"Savatcha_plus_{product['product_id']}_{product['count']}")
                ])
            bucket_info = f"Savatchada\n{text}\nProducts: {price}\nDelivery: {price//3}\nTotal: {price + price//3}"
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            await update.callback_query.message.reply_text(bucket_info,
                                                              reply_markup=InlineKeyboardMarkup(bucket_button))
        elif msg[1] == "back":
            bucket_id = db.get_bucket_id(chat_id=id)["id"]
            categories = db.get_category()
            category_button = []
            temp_button = []
            for category in categories:
                temp_button.append(
                    InlineKeyboardButton(text=f"{category['name']}", callback_data=f"category_{category['id']}"))
                if len(temp_button) == 2:
                    category_button.append(temp_button)
                    temp_button = []
            if len(temp_button) == 1:
                category_button.append(temp_button)
            category_button.append([InlineKeyboardButton(text="Savatcha", callback_data=f"Savatcha_{int(msg[2])}_{int(msg[3])}")])
            category_button.append([InlineKeyboardButton(text="⬅️back", callback_data="back")])
            category_button.append([InlineKeyboardButton(text="Asosiy menu", callback_data="main_menu")])
            products = db.get_item(bucket_id=bucket_id)
            price = 0
            bucket_info = ''
            for product in products:
                text = f"{str(product['count'])}x {product['item_name']}\n"
                price += int(product['item_price'])
                bucket_info += f"Savatchada\n{text}\nProducts: {price}\nDelivery: {price // 3}\nTotal: {price + price // 3}"
            await context.bot.delete_message(chat_id=id, message_id=message_id)
            await update.callback_query.message.reply_text(bucket_info,
                                                           reply_markup= InlineKeyboardMarkup(category_button))
        elif msg[1] == "minus" and int(msg[3])>1:
            bucket_id = db.get_bucket_id(chat_id=id)["id"]
            db.minus_count(product_id= msg[2], bucket_id= bucket_id, count= int(msg[3]))
            products = db.get_item(bucket_id)
            text = ''
            price = 0
            bucket_button = [
                [
                    InlineKeyboardButton(text="⬅️back", callback_data=f"Savatcha_back_{int(msg[2])}_{int(msg[3])}"),
                    InlineKeyboardButton(text="Buyurtma berish", callback_data="Buyurtma_qilish1")
                ],
                [
                    InlineKeyboardButton(text="Savatni bo'shatish", callback_data="clear_bucket")
                ]
            ]
            for product in products:
                text += f"{str(product['count'])}x {product['item_name']}\n"
                text2 = product['item_name']
                price += int(product['item_price'])
                bucket_button.append([
                    InlineKeyboardButton(text="➖", callback_data=f"Savatcha_minus_{product['product_id']}_{product['count']}"),
                    InlineKeyboardButton(text=f"{text2}", callback_data="product"),
                    InlineKeyboardButton(text="➕", callback_data=f"Savatcha_plus_{product['product_id']}_{product['count']}")
                ])
            bucket_info = f"Savatchada\n{text}\nProducts: {price}\nDelivery: {price // 3}\nTotal: {price + price // 3}"
            await context.bot.edit_message_text(chat_id=id, message_id=message_id,
                                                             text= bucket_info,
                                                             reply_markup= InlineKeyboardMarkup(bucket_button))
        elif msg[1] == "plus":
            bucket_id = db.get_bucket_id(chat_id=id)["id"]
            db.plus_count(product_id= msg[2], bucket_id= bucket_id, count= int(msg[3]))
            products = db.get_item(bucket_id)
            text = ''
            bucket_button = [
                [
                    InlineKeyboardButton(text="⬅️back", callback_data=f"Savatcha_back_{int(msg[2])}_{int(msg[3])}"),
                    InlineKeyboardButton(text="Buyurtma berish", callback_data="Buyurtma_qilish1")
                ],
                [
                    InlineKeyboardButton(text="Savatni bo'shatish", callback_data="clear_bucket")
                ]
            ]
            for product in products:
                text += f"{str(product['count'])}x {product['item_name']}\n"
                text2 = product['item_name']
                price = int(product['item_price']) * product['count']
                bucket_button.append([
                    InlineKeyboardButton(text="➖", callback_data=f"Savatcha_minus_{product['product_id']}_{product['count']}"),
                    InlineKeyboardButton(text=f"{text2}", callback_data="product"),
                    InlineKeyboardButton(text="➕", callback_data=f"Savatcha_plus_{product['product_id']}_{product['count']}")
                ])
            bucket_info = f"Savatchada\n{text}\nProducts: {price}\nDelivery: {price // 3}\nTotal: {price + price // 3}"
            await context.bot.edit_message_text(text=bucket_info,
                                                chat_id=id, message_id=message_id,
                                                reply_markup=InlineKeyboardMarkup(bucket_button))
    elif msg[0] == "clear":
        bucket_id = db.get_bucket_id(chat_id=id)["id"]
        db.clear_bucket(bucket_id)
        categories = db.get_category()
        category_button = []
        temp_button = []
        for category in categories:
            temp_button.append(
                InlineKeyboardButton(text=f"{category['name']}", callback_data=f"category_{category['id']}"))
            if len(temp_button) == 2:
                category_button.append(temp_button)
                temp_button = []
        if len(temp_button) == 1:
            category_button.append(temp_button)
        category_button.append([InlineKeyboardButton(text="Asosiy menu", callback_data="main_menu")])
        await context.bot.delete_message(chat_id=id, message_id=message_id)
        await update.callback_query.message.reply_text("Kategoriyalardan birini tanlang. (https://telegra.ph/Taomnoma-09-30)",
                                        reply_markup=InlineKeyboardMarkup(category_button))
    elif msg[0] == "Buyurtma":
        bucket_id = db.get_bucket_id(chat_id=id)["id"]
        products = db.get_item(bucket_id)
        price = 0
        for product in products:
            db.clear_item(product['product_id'])
            price += product['item_price']
        order_id = db.add_order(id=id, price=price, date=datetime.now())
        for product2 in products:
            db.add_order_item(order_id[0], product2['product_id'], product2['count'])
        await context.bot.delete_message(chat_id=id, message_id=message_id)
        await update.callback_query.message.reply_text("Buyurtmangiz qabul qilindi")

app = ApplicationBuilder().token("6460478195:AAERJ5nQOC5eIwtchBqfJcdowMEqi950Rnw").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(callback))
app.add_handler(MessageHandler(filters=filters.CONTACT, callback=contact))
app.add_handler(MessageHandler(filters=filters.TEXT, callback=message))
app.run_polling()
