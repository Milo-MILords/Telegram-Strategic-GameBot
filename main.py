import telebot
from telebot import types
import sqlite3

# Initialize the bot with your token
API_TOKEN = ''
ADMIN_ID = 000
CHANNEL_ID = ""
bot = telebot.TeleBot(API_TOKEN)

# Initialize the database
conn = sqlite3.connect('game_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Create the necessary tables
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    group_id INTEGER,
                    clothes INTEGER DEFAULT 2000,
                    money INTEGER DEFAULT 2000,
                    stones INTEGER DEFAULT 2000,
                    wood INTEGER DEFAULT 2000,
                    iron INTEGER DEFAULT 2000,
                    gold INTEGER DEFAULT 2000,
                    food INTEGER DEFAULT 2000,
                    meat INTEGER DEFAULT 2000,
                    swordsmen INTEGER DEFAULT 1500,
                    gunmen INTEGER DEFAULT 1500,
                    cavalry_swordsmen INTEGER DEFAULT 1500,
                    cavalry_gunmen INTEGER DEFAULT 1500,
                    special_guard INTEGER DEFAULT 1500,
                    medium_cannons INTEGER DEFAULT 1500,
                    large_cannons INTEGER DEFAULT 1500,
                    small_ships INTEGER DEFAULT 1500,
                    medium_ships INTEGER DEFAULT 1500,
                    large_ships INTEGER DEFAULT 1500,
                    stone_factory INTEGER DEFAULT 0,
                    wood_factory INTEGER DEFAULT 0,
                    iron_factory INTEGER DEFAULT 0,
                    gold_mine INTEGER DEFAULT 0,
                    farm INTEGER DEFAULT 0,
                    animal_farm INTEGER DEFAULT 0,
                    clothes_factory INTEGER DEFAULT 0,
                    bank INTEGER DEFAULT 0,
                    swordsmen_camp INTEGER DEFAULT 0,
                    gunmen_camp INTEGER DEFAULT 0,
                    cavalry_swordsmen_camp INTEGER DEFAULT 0,
                    cavalry_gunmen_camp INTEGER DEFAULT 0,
                    special_guard_camp INTEGER DEFAULT 0,
                    medium_cannon_factory INTEGER DEFAULT 0,
                    large_cannon_factory INTEGER DEFAULT 0,
                    small_shipyard INTEGER DEFAULT 0,
                    medium_shipyard INTEGER DEFAULT 0,
                    large_shipyard INTEGER DEFAULT 0,
                    treaties TEXT DEFAULT ''
                    )''')
conn.commit()

user_context = {}


def is_group_chat(message):
    return message.chat.type in ['group']


@bot.message_handler(commands=['setlord'])
def set_lord(message):
    if is_group_chat(message):
        user_id = message.from_user.id
        group_id = message.chat.id
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, group_id) VALUES (?, ?)",
            (user_id, group_id))
        conn.commit()
        bot.reply_to(message, "شما به عنوان یک لرد در این گروه ثبت شدید.")
    else:
        bot.reply_to(message, "این دستور فقط در گروه‌ها قابل استفاده است.")


@bot.message_handler(commands=['start'])
def start(message):
    if is_group_chat(message):
        user_id = message.from_user.id
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = cursor.fetchone()
        if user:
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton("💰 دارایی", callback_data='assets'))
            markup.add(types.InlineKeyboardButton("🛠️ ارتقا", callback_data='upgrade'))
            markup.add(types.InlineKeyboardButton("🙌 بیانیه", callback_data='statement'))
            markup.add(types.InlineKeyboardButton("✉️ پیام خصوصی", callback_data='private_message'))
            markup.add(types.InlineKeyboardButton("📜 معاهده", callback_data='treaty'))
            markup.add(types.InlineKeyboardButton("⚔️ لشکرکشی", callback_data='attack'))
            markup.add(types.InlineKeyboardButton("🔨آپ هفتگی", callback_data='weekly_update'))
            markup.add(types.InlineKeyboardButton("🛠️ تنظیم دارایی", callback_data='change_assets'))
            bot.send_message(message.chat.id, "خوش آمدین قربان", reply_markup=markup)
        else:
            bot.reply_to(message, "شما ابتدا باید با /setlord ثبت نام کنید.")
    else:
        bot.reply_to(message, "این ربات فقط در گروه‌ها قابل استفاده است.")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    data_parts = call.data.split('_')
    global item_to_upgrade
    item_to_upgrade = '_'.join(call.data.split('_')[1:])
    #print(data_parts)

    if data_parts[0] == 'assets':
        show_assets(call.message, user_id)
    elif data_parts[0] == 'upgrade':
        if len(data_parts) == 1:
            show_upgrade_options(call.message)
        elif len(data_parts) == 3:
            confirm_upgrade(call.message)
        elif '_'.join(data_parts[0:2]) == 'upgrade_confirm':
            process_upgrade_confirmation(call)
    elif call.data == 'treaty_confirmed' or call.data == 'treaty_not_confirmed':
        process_treaty_confirmation(call)
    elif data_parts[0] == 'private':
        if len(data_parts) == 2 and data_parts[1] == 'message':
            ask_for_private_message(call.message, user_id)
        elif len(data_parts) == 3 and data_parts[1] == 'send':
            group_id = int(data_parts[2])
            send_private_message(call, group_id)
    elif data_parts[0] == 'change':
        if len(data_parts) == 2 and data_parts[1] == 'assets':
            if user_id == ADMIN_ID:
                show_asset_change_options(call.message)
            else:
                bot.answer_callback_query(call.id, "شما ادمین نیستید.")
        elif len(data_parts) == 3 and data_parts[1] == 'asset':
            asset_type = data_parts[2]
            ask_for_new_asset_value(call.message, asset_type, user_id)
    elif data_parts[0] == 'weekly':
        if data_parts[1] == 'update':
            if user_id == ADMIN_ID:
                collect_factory_output(call.message, user_id)
            else:
                bot.answer_callback_query(call.id, "شما ادمین نیستید.")
    elif data_parts[0] == 'attack':
        if len(data_parts) == 1:
            ask_for_attack_type(call.message, user_id)
        else:
            handle_attack_type_selection(call)
    elif data_parts[0] == 'statement':
        if len(data_parts) == 1:
            ask_for_statement(call.message, user_id)
    elif data_parts[0] == 'treaty':
        if len(data_parts) == 1:
            show_treaty_options(call.message)
        elif len(data_parts) == 2 and data_parts[1] == 'new':
            ask_for_treaty_content(call.message, user_id)
        elif len(data_parts) == 3 and data_parts[1] == 'send':
            group_id = int(data_parts[2])
            send_treaty_confirmation(call, group_id)
    else:
        bot.answer_callback_query(call.id, "دستور نامعتبر است.")


def show_assets(message, user_id):
    cursor.execute(
        "SELECT clothes, money, stones, wood, iron, gold, food, meat, swordsmen, gunmen, cavalry_swordsmen, cavalry_gunmen, special_guard, medium_cannons, large_cannons, small_ships, medium_ships, large_ships, "
        "stone_factory, wood_factory, iron_factory, gold_mine, farm, animal_farm, clothes_factory, bank, "
        "swordsmen_camp, gunmen_camp, cavalry_swordsmen_camp, cavalry_gunmen_camp, special_guard_camp, medium_cannon_factory, large_cannon_factory, small_shipyard, medium_shipyard, large_shipyard, treaties FROM users WHERE user_id=?",
        (user_id,))
    user = cursor.fetchone()
    if user:
        assets_message = (
            f"💰 دارایی:\n"
            f"لباس🥋 : {user[0]}\n"
            f"پول💵 : {user[1]}\n"
            f"🪨 سنگ: {user[2]}\n"
            f"🌲 چوب: {user[3]}\n"
            f"🪛 آهن: {user[4]}\n"
            f"🏅 طلا: {user[5]}\n"
            f"🍞 غذا: {user[6]}\n"
            f"🍖 گوشت: {user[7]}\n"
            f"🗡️ سرباز شمشیرزن: {user[8]}\n"
            f"🔫 سرباز تفنگدار: {user[9]}\n"
            f"🗡️ سواره‌نظام شمشیرزن: {user[10]}\n"
            f"🔫 سواره‌نظام تفنگدار: {user[11]}\n"
            f"🛡️ گارد ویژه: {user[12]}\n"
            f"🎯 توپ متوسط: {user[13]}\n"
            f"🎯 توپ بزرگ: {user[14]}\n"
            f"⛵ کشتی کوچک: {user[15]}\n"
            f"🚢 کشتی متوسط: {user[16]}\n"
            f"🛳️ کشتی بزرگ: {user[17]}\n\n"
            f"🏭 کارخانجات:\n"
            f"کارخونه سنگ: {user[18]}\n"
            f"کارخونه چوب: {user[19]}\n"
            f"کارخونه آهن: {user[20]}\n"
            f"معدن طلا: {user[21]}\n"
            f"زمین کشاورزی: {user[22]}\n"
            f"دامداری: {user[23]}\n"
            f"کارخانه لباس: {user[24]}\n"
            f"بانک🏦: {user[25]}\n\n"
            f"⚔️کمپ‌ها:\n"
            f"کمپ سرباز شمشیرزن: {user[26]}\n"
            f"کمپ سرباز تفنگدار: {user[27]}\n"
            f"کمپ سواره‌نظام شمشیرزن: {user[28]}\n"
            f"کمپ سواره‌نظام تفنگدار: {user[29]}\n"
            f"کمپ گارد ویژه: {user[30]}\n\n"
            f"🔧 کارخانجات توپخانه:\n"
            f"کارخانه توپ متوسط: {user[31]}\n"
            f"کارخانه توپ بزرگ: {user[32]}\n\n"
            f"⚓کشتی‌سازی‌ها:\n"
            f"کشتی‌سازی کوچک: {user[33]}\n"
            f"کشتی‌سازی متوسط: {user[34]}\n"
            f"کشتی‌سازی بزرگ: {user[35]}\n\n"
            f"📜 معاهدات:\n{user[36]}"
        )
        bot.send_message(message.chat.id, assets_message)
    else:
        bot.send_message(message.chat.id, "شما ابتدا باید با /setlord ثبت نام کنید.")


def show_upgrade_options(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(types.InlineKeyboardButton("کارخونه سنگ", callback_data='upgrade_stone_factory'))
    markup.add(types.InlineKeyboardButton("کارخونه چوب", callback_data='upgrade_wood_factory'))
    markup.add(types.InlineKeyboardButton("کارخونه آهن", callback_data='upgrade_iron_factory'))
    markup.add(types.InlineKeyboardButton("معدن طلا", callback_data='upgrade_gold_mine'))
    markup.add(types.InlineKeyboardButton("زمین کشاورزی", callback_data='upgrade_farm_farm'))
    markup.add(types.InlineKeyboardButton("دامداری", callback_data='upgrade_animal_farm'))
    markup.add(types.InlineKeyboardButton("کارخانه لباس", callback_data='upgrade_clothes_factory'))
    markup.add(types.InlineKeyboardButton("بانک", callback_data='upgrade_bank_bank'))
    markup.add(types.InlineKeyboardButton("کمپ سرباز شمشیرزن", callback_data='upgrade_swordsmen_camp'))
    markup.add(types.InlineKeyboardButton("کمپ سرباز تفنگدار", callback_data='upgrade_gunmen_camp'))
    markup.add(types.InlineKeyboardButton("کمپ سواره‌نظام شمشیرزن", callback_data='upgrade_cavalryswordsmen_camp'))
    markup.add(types.InlineKeyboardButton("کمپ سواره‌نظام تفنگدار", callback_data='upgrade_cavalrygunmen_camp'))
    markup.add(types.InlineKeyboardButton("کمپ گارد ویژه", callback_data='upgrade_specialguard_camp'))
    markup.add(types.InlineKeyboardButton("کارخانه توپ متوسط", callback_data='upgrade_mediumcannon_factory'))
    markup.add(types.InlineKeyboardButton("کارخانه توپ بزرگ", callback_data='upgrade_largecannon_factory'))
    markup.add(types.InlineKeyboardButton("کشتی‌سازی کوچک", callback_data='upgrade_small_shipyard'))
    markup.add(types.InlineKeyboardButton("کشتی‌سازی متوسط", callback_data='upgrade_medium_shipyard'))
    markup.add(types.InlineKeyboardButton("کشتی‌سازی بزرگ", callback_data='upgrade_large_shipyard'))
    bot.send_message(message.chat.id, "انتخاب کنید که کدام بخش را میخواهید ارتقا دهید", reply_markup=markup)


def confirm_upgrade(message):
    cost_message = get_upgrade_cost_message()
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("بله", callback_data=f'upgrade_confirm_{item_to_upgrade}'))
    bot.send_message(message.chat.id, cost_message, reply_markup=markup)


def get_upgrade_cost_message():
    if item_to_upgrade == 'stone_factory':
        return "برای ارتقا کارخونه سنگ به 500 سنگ و 500 پول نیاز دارید."
    elif item_to_upgrade == 'wood_factory':
        return "برای ارتقا کارخونه چوب به 500 سنگ و 500 پول نیاز دارید."
    elif item_to_upgrade == 'iron_factory':
        return "برای ارتقا کارخونه آهن به 500 سنگ و 500 پول نیاز دارید."
    elif item_to_upgrade == 'gold_mine':
        return "برای ارتقا معدن طلا به 500 چوب، 500 سنگ و 500 پول نیاز دارید."
    elif item_to_upgrade == 'farm_farm':
        return "برای ارتقا زمین کشاورزی به 500 چوب و 500 سنگ نیاز دارید."
    elif item_to_upgrade == 'animal_farm':
        return "برای ارتقا دامداری به 500 چوب، 500 آهن و 500 سنگ نیاز دارید."
    elif item_to_upgrade == 'clothes_factory':
        return "برای ارتقا کارخانه لباس به 500 طلا، 500 پول و 500 سنگ نیاز دارید."
    elif item_to_upgrade == 'bank_bank':
        return "برای ارتقا بانک به 500 سنگ، 500 آهن و 500 طلا نیاز دارید."
    elif item_to_upgrade == 'swordsmen_camp':
        return "برای ارتقا کمپ سرباز شمشیرزن به 500 پول، 500 سنگ و 500 چوب نیاز دارید."
    elif item_to_upgrade == 'gunmen_camp':
        return "برای ارتقا کمپ سرباز تفنگدار به 500 پول، 500 طلا و 500 آهن نیاز دارید."
    elif item_to_upgrade == 'cavalryswordsmen_camp':
        return "برای ارتقا کمپ سواره‌نظام شمشیرزن به 500 آهن، 250 طلا، 500 سنگ و 250 پول نیاز دارید."
    elif item_to_upgrade == 'cavalrygunmen_camp':
        return "برای ارتقا کمپ سواره‌نظام تفنگدار به 800 طلا، 800 سنگ و 500 پول نیاز دارید."
    elif item_to_upgrade == 'specialguard_camp':
        return "برای ارتقا کمپ گارد ویژه به 1000 پول، 1000 سنگ و 1000 چوب نیاز دارید."
    elif item_to_upgrade == 'mediumcannon_factory':
        return "برای ارتقا کارخانه توپ متوسط به 500 آهن، 250 پول و 250 چوب نیاز دارید."
    elif item_to_upgrade == 'largecannon_factory':
        return "برای ارتقا کارخانه توپ بزرگ به 500 آهن، 500 سنگ، 250 پول و 200 طلا نیاز دارید."
    elif item_to_upgrade == 'small_shipyard':
        return "برای ارتقا کشتی‌سازی کوچک به 200 آهن، 200 چوب و 200 پول نیاز دارید."
    elif item_to_upgrade == 'medium_shipyard':
        return "برای ارتقا کشتی‌سازی متوسط به 500 آهن، 500 چوب و 500 پول نیاز دارید."
    elif item_to_upgrade == 'large_shipyard':
        return "برای ارتقا کشتی‌سازی بزرگ به 1000 آهن، 1000 چوب و 1000 پول نیاز دارید."
    else:
        return "آیتم مشخص شده برای ارتقا موجود نیست."


@bot.callback_query_handler(func=lambda call: call.data.startswith('upgrade_confirm_'))
def process_upgrade_confirmation(call):
    user_id = call.from_user.id
    if check_upgrade_cost(user_id):
        apply_upgrade(user_id)
        bot.send_message(call.message.chat.id, f"ارتقا یافت")
    else:
        bot.send_message(call.message.chat.id, "موجودی شما کافی نیست")
    bot.answer_callback_query(call.id)


def check_upgrade_cost(user_id):
    cursor.execute("SELECT stones, wood, iron, gold, money FROM users WHERE user_id=?", (user_id,))
    resources = cursor.fetchone()
    #print(item_to_upgrade)
    if item_to_upgrade == 'confirm_stone_factory':
        return resources[0] >= 500 and resources[4] >= 500
    elif item_to_upgrade == 'confirm_wood_factory':
        return resources[0] >= 500 and resources[4] >= 500
    elif item_to_upgrade == 'confirm_iron_factory':
        return resources[0] >= 500 and resources[4] >= 500
    elif item_to_upgrade == 'confirm_gold_mine':
        return resources[2] >= 500 and resources[0] >= 500 and resources[4] >= 500
    elif item_to_upgrade == 'confirm_farm_farm':
        return resources[2] >= 500 and resources[0] >= 500
    elif item_to_upgrade == 'confirm_animal_farm':
        return resources[2] >= 500 and resources[3] >= 500 and resources[0] >= 500
    elif item_to_upgrade == 'confirm_clothes_factory':
        return resources[3] >= 500 and resources[4] >= 500 and resources[0] >= 500
    elif item_to_upgrade == 'confirm_bank_bank':
        return resources[0] >= 500 and resources[2] >= 500 and resources[3] >= 500
    elif item_to_upgrade == 'confirm_swordsmen_camp':
        return resources[4] >= 500 and resources[0] >= 500 and resources[2] >= 500
    elif item_to_upgrade == 'confirm_gunmen_camp':
        return resources[4] >= 500 and resources[3] >= 500 and resources[2] >= 500
    elif item_to_upgrade == 'confirm_cavalryswordsmen_camp':
        return resources[2] >= 500 and resources[3] >= 250 and resources[0] >= 500 and resources[4] >= 250
    elif item_to_upgrade == 'confirm_cavalrygunmen_camp':
        return resources[3] >= 800 and resources[0] >= 800 and resources[4] >= 500
    elif item_to_upgrade == 'confirm_specialguard_camp':
        return resources[4] >= 1000 and resources[0] >= 1000 and resources[2] >= 1000
    elif item_to_upgrade == 'confirm_mediumcannon_factory':
        return resources[2] >= 500 and resources[4] >= 250 and resources[1] >= 250
    elif item_to_upgrade == 'confirm_largecannon_factory':
        return resources[2] >= 500 and resources[0] >= 500 and resources[4] >= 250 and resources[3] >= 200
    elif item_to_upgrade == 'confirm_small_shipyard':
        return resources[2] >= 200 and resources[1] >= 200 and resources[4] >= 200
    elif item_to_upgrade == 'confirm_medium_shipyard':
        return resources[2] >= 500 and resources[1] >= 500 and resources[4] >= 500
    elif item_to_upgrade == 'confirm_large_shipyard':
        return resources[2] >= 1000 and resources[1] >= 1000 and resources[4] >= 1000
    else:
        return False


def apply_upgrade(user_id):
    if item_to_upgrade == 'confirm_stone_factory':
        cursor.execute(
            "UPDATE users SET stones = stones - 500, money = money - 500, stone_factory = stone_factory + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_wood_factory':
        cursor.execute(
            "UPDATE users SET stones = stones - 500, money = money - 500, wood_factory = wood_factory + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_iron_factory':
        cursor.execute(
            "UPDATE users SET stones = stones - 500, money = money - 500, iron_factory = iron_factory + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_gold_mine':
        cursor.execute(
            "UPDATE users SET wood = wood - 500, stones = stones - 500, money = money - 500, gold_mine = gold_mine + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_farm_farm':
        cursor.execute(
            "UPDATE users SET wood = wood - 500, stones = stones - 500, farm = farm + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_animal_farm':
        cursor.execute(
            "UPDATE users SET wood = wood - 500, iron = iron - 500, stones = stones - 500, animal_farm = animal_farm + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_clothes_factory':
        cursor.execute(
            "UPDATE users SET gold = gold - 500, money = money - 500, stones = stones - 500, clothes_factory = clothes_factory + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_bank_bank':
        cursor.execute(
            "UPDATE users SET stones = stones - 500, iron = iron - 500, gold = gold - 500, bank = bank + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_swordsmen_camp':
        cursor.execute(
            "UPDATE users SET money = money - 500, stones = stones - 500, wood = wood - 500, swordsmen_camp = swordsmen_camp + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_gunmen_camp':
        cursor.execute(
            "UPDATE users SET money = money - 500, gold = gold - 500, iron = iron - 500, gunmen_camp = gunmen_camp + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_cavalryswordsmen_camp':
        cursor.execute(
            "UPDATE users SET iron = iron - 500, gold = gold - 250, stones = stones - 500, money = money - 250, cavalry_swordsmen_camp = cavalry_swordsmen_camp + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_cavalrygunmen_camp':
        cursor.execute(
            "UPDATE users SET gold = gold - 800, stones = stones - 800, money = money - 500, cavalry_gunmen_camp = cavalry_gunmen_camp + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_specialguard_camp':
        cursor.execute(
            "UPDATE users SET money = money - 1000, stones = stones - 1000, wood = wood - 1000, special_guard_camp = special_guard_camp + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_mediumcannon_factory':
        cursor.execute(
            "UPDATE users SET iron = iron - 500, money = money - 250, wood = wood - 250, medium_cannon_factory = medium_cannon_factory + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_largecannon_factory':
        cursor.execute(
            "UPDATE users SET iron = iron - 500, stones = stones - 500, money = money - 250, gold = gold - 200, large_cannon_factory = large_cannon_factory + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_small_shipyard':
        cursor.execute(
            "UPDATE users SET iron = iron - 200, wood = wood - 200, money = money - 200, small_shipyard = small_shipyard + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_medium_shipyard':
        cursor.execute(
            "UPDATE users SET iron = iron - 500, wood = wood - 500, money = money - 500, medium_shipyard = medium_shipyard + 1 WHERE user_id=?",
            (user_id,))
    elif item_to_upgrade == 'confirm_large_shipyard':
        cursor.execute(
            "UPDATE users SET iron = iron - 1000, wood = wood - 1000, money = money - 1000, large_shipyard = large_shipyard + 1 WHERE user_id=?",
            (user_id,))
    #print('done')
    conn.commit()


def ask_for_private_message(message, user_id):
    bot.send_message(message.chat.id, "لطفا پیام خصوصی خود را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_private_message(msg, user_id))


def get_private_message(message, user_id):
    private_message = message.text
    user_context[user_id] = {'private_message': private_message}
    cursor.execute("SELECT DISTINCT group_id FROM users")
    groups = cursor.fetchall()
    if groups:
        markup = types.InlineKeyboardMarkup(row_width=2)
        for group in groups:
            bot_name = bot.get_chat(group[0]).title
            markup.add(types.InlineKeyboardButton(bot_name, callback_data=f'private_send_{group[0]}'))
        bot.send_message(message.chat.id, "انتخاب کنید که به کدام گروه ارسال شود:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('private_send_'))
def send_private_message(call, group_id):
    user_id = call.from_user.id
    private_message = user_context[user_id].get('private_message')
    user_info = bot.get_chat(user_id)
    user_name = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"
    if private_message:
        bot.send_message(group_id, f"📬 پیام خصوصی از {user_name}:\n\n{private_message}", parse_mode='HTML')
        bot.answer_callback_query(call.id, "پیام خصوصی ارسال شد.")
    else:
        bot.answer_callback_query(call.id, "پیام خصوصی یافت نشد.")


def show_asset_change_options(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    asset_types = ['clothes', 'stones', 'wood', 'iron', 'gold', 'money', 'food', 'meat', 'swordsmen', 'gunmen',
                   'cavalry_swordsmen', 'cavalry_gunmen', 'special_guard', 'medium_cannons', 'large_cannons',
                   'small_ships', 'medium_ships', 'large_ships']
    for asset in asset_types:
        markup.add(types.InlineKeyboardButton(asset, callback_data=f'change_asset_{asset}'))
    bot.send_message(message.chat.id, "انتخاب کنید که کدام دارایی را میخواهید تغییر دهید:", reply_markup=markup)


def ask_for_new_asset_value(message, asset_type, user_id):
    user_context[user_id] = {'asset_type': asset_type}
    bot.send_message(message.chat.id, f"لطفا مقدار جدید برای {asset_type} را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: set_new_asset_value(msg, user_id))


def set_new_asset_value(message, user_id):
    try:
        new_value = int(message.text)
        asset_type = user_context[user_id].get('asset_type')
        cursor.execute(f"UPDATE users SET {asset_type} = ? WHERE user_id = ?", (new_value, user_id))
        conn.commit()
        bot.send_message(message.chat.id, f"{asset_type} به {new_value} تغییر یافت.")
    except ValueError:
        bot.send_message(message.chat.id, "مقدار وارد شده معتبر نیست. لطفا یک عدد وارد کنید.")
    except Exception as e:
        bot.send_message(message.chat.id, f"خطا: {e}")


def show_treaty_options(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ثبت معاهده جدید", callback_data='treaty_new'))
    bot.send_message(message.chat.id, "انتخاب کنید که کدام بخش را میخواهید انجام دهید", reply_markup=markup)


def ask_for_treaty_content(message, user_id):
    bot.send_message(message.chat.id, "لطفا محتوای معاهده را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_treaty_content(msg, user_id))


def get_treaty_content(message, user_id):
    treaty_content = message.text
    user_context[user_id] = {'treaty_content': treaty_content}
    cursor.execute("SELECT DISTINCT group_id FROM users")
    groups = cursor.fetchall()
    if groups:
        markup = types.InlineKeyboardMarkup()
        for group in groups:
            bot_name = bot.get_chat(group[0]).title
            markup.add(types.InlineKeyboardButton(bot_name, callback_data=f'treaty_send_{group[0]}'))
        bot.send_message(message.chat.id, "انتخاب کنید که به کدام گروه ارسال شود:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('treaty_send_'))
def send_treaty_confirmation(call, group_id):
    user_id = call.from_user.id
    treaty_content = user_context[user_id].get('treaty_content')
    if treaty_content:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("بله", callback_data='treaty_confirmed'))
        markup.add(types.InlineKeyboardButton("خیر", callback_data='treaty_not_confirmed'))
        user_info = bot.get_chat(user_id)
        user_name = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"
        bot.send_message(group_id, f"📜 معاهده جدید از {user_name}:\n\n{treaty_content}\n\nتایید میکنید؟",
                         reply_markup=markup, parse_mode='HTML')
        user_context[user_id]['group_id'] = group_id
        bot.answer_callback_query(call.id, "معاهده ارسال شد.")
    else:
        bot.answer_callback_query(call.id, "محتوای معاهده یافت نشد.")


def process_treaty_confirmation(call):
    user_id = call.from_user.id
    group_id = user_context[user_id]['group_id']
    #print(call.data)
    if call.data == 'treaty_confirmed':
        cursor.execute("SELECT treaties FROM users WHERE user_id = ?", (user_id,))
        user_treaties = cursor.fetchone()[0]
        new_treaties = user_treaties + "\n\n" + user_context[user_id].get('treaty_content') if user_treaties else \
            user_context[user_id].get('treaty_content')
        cursor.execute("UPDATE users SET treaties = ? WHERE user_id = ?", (new_treaties, user_id))
        conn.commit()
        bot.send_message(group_id, 'معاهده تایید شد')
    else:
        bot.send_message(group_id, 'معاهده رد شد')
    bot.answer_callback_query(call.id, 'نتیجه معاهده ثبت شد')


def collect_factory_output(call, user_id):
    cursor.execute(
        "SELECT stone_factory, wood_factory, iron_factory, gold_mine, farm, animal_farm, clothes_factory, bank, swordsmen_camp, gunmen_camp, cavalry_swordsmen_camp, cavalry_gunmen_camp, special_guard_camp, medium_cannon_factory, large_cannon_factory, small_shipyard, medium_shipyard, large_shipyard FROM users WHERE user_id=?",
        (user_id,))
    user_factories = cursor.fetchone()

    if user_factories:
        stones_collected = user_factories[0] * 1500
        wood_collected = user_factories[1] * 1500
        iron_collected = user_factories[2] * 1500
        gold_collected = user_factories[3] * 1500
        food_collected = user_factories[4] * 1500
        meat_collected = user_factories[5] * 1500
        clothes_collected = user_factories[6] * 1500
        money_collected = user_factories[7] * 1500
        swordsmen_collected = user_factories[8] * 500
        gunmen_collected = user_factories[9] * 500
        cavalry_swordsmen_collected = user_factories[10] * 500
        cavalry_gunmen_collected = user_factories[11] * 500
        special_guard_collected = user_factories[12] * 500
        medium_cannons_collected = user_factories[13] * 1500
        large_cannons_collected = user_factories[14] * 1500
        small_ships_collected = user_factories[15] * 500
        medium_ships_collected = user_factories[16] * 500
        large_ships_collected = user_factories[17] * 500

        cursor.execute(
            "UPDATE users SET money = money + ?, stones = stones + ?, wood = wood + ?, iron = iron + ?, gold = gold + ?, food = food + ?, meat = meat + ?, clothes = clothes + ?, small_ships = small_ships + ?, medium_ships = medium_ships + ?, large_ships = large_ships + ?, swordsmen = swordsmen + ?, gunmen = gunmen + ?, cavalry_swordsmen = cavalry_swordsmen + ?, cavalry_gunmen = cavalry_gunmen + ?, special_guard = special_guard + ?, medium_cannons = medium_cannons + ?, large_cannons = large_cannons + ? WHERE user_id=?",
            (money_collected, stones_collected, wood_collected, iron_collected, gold_collected, food_collected,
             meat_collected, clothes_collected, small_ships_collected, medium_ships_collected, large_ships_collected,
             swordsmen_collected, gunmen_collected, cavalry_swordsmen_collected, cavalry_gunmen_collected,
             special_guard_collected, medium_cannons_collected, large_cannons_collected,
             user_id))
        conn.commit()

        collection_message = (f"🏭 محصولات جمع‌آوری شده:\n"
                              f"پول💵 : {money_collected}\n"
                              f"🪨 سنگ: {stones_collected}\n"
                              f"🌲 چوب: {wood_collected}\n"
                              f"🪛 آهن: {iron_collected}\n"
                              f"🏅 طلا: {gold_collected}\n"
                              f"🍞 غذا: {food_collected}\n"
                              f"🍖 گوشت: {meat_collected}\n"
                              f"👗 لباس: {clothes_collected}\n"
                              f"⛵ کشتی کوچک: {small_ships_collected}\n"
                              f"🚢 کشتی متوسط: {medium_ships_collected}\n"
                              f"🛳️ کشتی بزرگ: {large_ships_collected}\n"
                              f"🗡️ سرباز شمشیرزن: {swordsmen_collected}\n"
                              f"🔫 سرباز تفنگدار: {gunmen_collected}\n"
                              f"🗡️ سواره‌نظام شمشیرزن: {cavalry_swordsmen_collected}\n"
                              f"🔫 سواره‌نظام تفنگدار: {cavalry_gunmen_collected}\n"
                              f"🛡️ گارد ویژه: {special_guard_collected}\n"
                              f"🎯 توپ متوسط: {medium_cannons_collected}\n"
                              f"🎯 توپ بزرگ: {large_cannons_collected}\n")

        bot.send_message(call.chat.id, collection_message)
    else:
        bot.send_message(call.chat.id, "خطا")


def ask_for_statement(message, user_id):
    bot.send_message(message.chat.id, "<b>لطفا بیانیه خود را ارسال کنید </b>", parse_mode='HTML')
    bot.register_next_step_handler(message, lambda msg: send_statement(msg, user_id))


def send_statement(message, user_id):
    user_info = bot.get_chat(user_id)
    user_link = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"
    group_name = message.chat.title if message.chat.title else "نامشخص"
    bot.send_message(message.chat.id, "بیانیه شما <b>ارسال شد</b>", parse_mode='HTML')

    additional_caption = f"\n\n🌍 از {group_name}\n👤 فرمانده: {user_link}"

    if message.text:
        bot.send_message(CHANNEL_ID, f"{message.text}{additional_caption}", parse_mode='HTML')
    elif message.photo:
        original_caption = message.caption if message.caption else " "
        bot.send_photo(CHANNEL_ID, message.photo[-1].file_id, caption=f"{original_caption}{additional_caption}",
                       parse_mode='HTML')
    elif message.video:
        original_caption = message.caption if message.caption else " "
        bot.send_video(CHANNEL_ID, message.video.file_id, caption=f"{original_caption}{additional_caption}",
                       parse_mode='HTML')
    elif message.document:
        original_caption = message.caption if message.caption else " "
        bot.send_document(CHANNEL_ID, message.document.file_id, caption=f"{original_caption}{additional_caption}",
                          parse_mode='HTML')
    elif message.audio:
        original_caption = message.caption if message.caption else " "
        bot.send_audio(CHANNEL_ID, message.audio.file_id, caption=f"{original_caption}{additional_caption}",
                       parse_mode='HTML')
    elif message.voice:
        original_caption = message.caption if message.caption else " "
        bot.send_voice(CHANNEL_ID, message.voice.file_id, caption=f"{original_caption}{additional_caption}",
                       parse_mode='HTML')


def ask_for_attack_type(message, user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("زمینی", callback_data='attack_type_land'))
    markup.add(types.InlineKeyboardButton("دریایی", callback_data='attack_type_sea'))
    #markup.add(types.InlineKeyboardButton("هوایی", callback_data='attack_type_air'))
    bot.send_message(message.chat.id, "نوع لشکرکشی را انتخاب کنید:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('attack_type_'))
def handle_attack_type_selection(call):
    global photo_url
    user_id = call.from_user.id
    attack_type = call.data.split('_')[2]
    user_context[user_id] = {'attack_type': attack_type}
    if attack_type == "land":
        photo_url = "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/2"
    elif attack_type == "sea":
        photo_url = "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/3"
    bot.send_message(call.message.chat.id, "لطفا اطلاعات ارتش خود را وارد کنید:")
    bot.register_next_step_handler(call.message, lambda msg: get_attack_origin(msg, user_id))


def get_attack_origin(message, user_id):
    attack_details = message.text
    user_context[user_id]['attack_details'] = attack_details
    bot.send_message(message.chat.id, "مبدا لشکرکشی را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_attack_destination(msg, user_id))


def get_attack_destination(message, user_id):
    attack_origin = message.text
    user_context[user_id]['attack_origin'] = attack_origin
    bot.send_message(message.chat.id, "مقصد لشکرکشی را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_attack_time(msg, user_id))


def get_attack_time(message, user_id):
    attack_destination = message.text
    user_context[user_id]['attack_destination'] = attack_destination
    bot.send_message(message.chat.id, "زمان رسیدن را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: send_attack_details(msg, user_id))


def send_attack_details(message, user_id):
    attack_time = message.text
    attack_type = user_context[user_id]['attack_type']
    attack_details = user_context[user_id]['attack_details']
    attack_origin = user_context[user_id]['attack_origin']
    attack_destination = user_context[user_id]['attack_destination']
    # Get user info
    user_info = bot.get_chat(user_id)
    user_name = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"

    # Send details to admin
    bot.send_message(ADMIN_ID,
                     f"🔖 ارتش کشور {attack_origin} به مقصد {attack_destination} حرکت کردند ({attack_type})\n\n⚜️ "
                     f"فرمانده: {user_name}\n⌛️ زمان رسیدن: {attack_time}\n📝 جزئیات: {attack_details}",
                     parse_mode='HTML')

    # Send summary to channel
    bot.send_photo(CHANNEL_ID, photo_url, caption=
    f"🔖 ارتش کشور {attack_origin} به مقصد {attack_destination} حرکت کردند ({attack_type})\n\n⚜️ "
    f"فرمانده: {user_name}\n⌛️ زمان رسیدن: {attack_time}",
                   parse_mode='HTML')

    bot.send_message(message.chat.id, "اطلاعات لشکرکشی ارسال شد.")


# Start the bot
bot.infinity_polling()
