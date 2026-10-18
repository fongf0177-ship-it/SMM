import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os
import time

# យក Token ពី Environment Variables
TOKEN = os.environ.get('BOT_TOKEN', 'ដាក់_TOKEN_របស់អ្នកនៅទីនេះ')
bot = telebot.TeleBot(TOKEN)

user_languages = {}

texts = {
    'kh': {
        'welcome': "សួស្តី {name}! សូមជ្រើសរើសសេវាកម្មខាងក្រោម៖",
        'select_below': "👇 សូមជ្រើសរើសជម្រើសនៅខាងក្រោម៖",
        'btn_manage': "👨🏻‍💻 គ្រប់គ្រងគណនី",
        'btn_rent': "🛍 ជួលសេវាកម្ម",
        'btn_change_lang_inline': "🇬🇧",
        'manage_text': "នេះគឺជាទំព័រសម្រាប់ គ្រប់គ្រងគណនី របស់អ្នក។",
        'rent_menu_text': "សូមជ្រើសរើសសេវាកម្មដែលអ្នកចង់ជួលខាងក្រោម៖",
        'btn_bot_smm': "🤖 BOT SMM",
        'btn_back': "🔙 ត្រឡប់ក្រោយ",
        'bot_smm_text': "តារាងសម្រាប់លោកអ្នកជួល Telegram bot តម្លៃ :",
        'package_selected': "អ្នកបានជ្រើសរើសកញ្ចប់ {package} ។\n\n👇 សូមផ្ញើ API TOKEN BOT និង KHQR CODE របស់អ្នកមកកាន់យើងខ្ញុំ៖",
        'data_received': "✅ ទទួលបានទិន្នន័យជោគជ័យ!\n\nសូមរង់ចាំការបញ្ជាក់ពី Admin របស់យើងខ្ញុំ។",
        'main_menu_text': "អ្នកបានត្រឡប់មកម៉ឺនុយដើមវិញ៖",
        'lang_changed': "ភាសាត្រូវបានផ្លាស់ប្តូរទៅជា ខ្មែរ 🇰🇭"
    },
    'en': {
        'welcome': "Hello {name}! Please select a service below:",
        'select_below': "👇 Please select an option below:",
        'btn_manage': "👨🏻‍💻 Manage Account",
        'btn_rent': "🛍 Rent Service",
        'btn_change_lang_inline': "🇰🇭",
        'manage_text': "This is your Account Management page.",
        'rent_menu_text': "Please select a service you want to rent below:",
        'btn_bot_smm': "🤖 BOT SMM",
        'btn_back': "🔙 Back",
        'bot_smm_text': "Table for renting Telegram bot, Prices :",
        'package_selected': "You have selected the {package} package.\n\n👇 Please send your API TOKEN BOT and KHQR CODE to us:",
        'data_received': "✅ Data received successfully!\n\nPlease wait for confirmation from our Admin.",
        'main_menu_text': "You are back to the Main Menu:",
        'lang_changed': "Language changed to English 🇬🇧"
    }
}

def get_user_lang(chat_id):
    return user_languages.get(chat_id, 'kh')

def get_main_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton(texts[lang]['btn_manage']), KeyboardButton(texts[lang]['btn_rent']))
    return markup

def get_rent_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(KeyboardButton(texts[lang]['btn_bot_smm']), KeyboardButton(texts[lang]['btn_back']))
    return markup

def get_inline_lang_keyboard(lang):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=texts[lang]['btn_change_lang_inline'], callback_data='change_lang'))
    return markup

def get_smm_pricing_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🛍️ 1 Month 2.50$", callback_data='rent_1m'),
        InlineKeyboardButton("🛍️ 2 Month 4.99$", callback_data='rent_2m'),
        InlineKeyboardButton("🛍️ 3 Month 7.00$", callback_data='rent_3m')
    )
    return markup

def simulate_typing_delay(chat_id):
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(1.0)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name or "អតិថិជន"
    lang = get_user_lang(chat_id)
    
    simulate_typing_delay(chat_id)
    image_url = "https://img.sanishtech.com/u/23589ed30a9f482112e591c0f4c9fa18.png"
    
    bot.send_photo(chat_id, photo=image_url, caption=texts[lang]['welcome'].format(name=user_name), reply_markup=get_inline_lang_keyboard(lang))
    bot.send_message(chat_id, texts[lang]['select_below'], reply_markup=get_main_keyboard(lang))

@bot.callback_query_handler(func=lambda call: call.data == 'change_lang')
def handle_change_lang_callback(call):
    chat_id = call.message.chat.id
    current_lang = get_user_lang(chat_id)
    new_lang = 'en' if current_lang == 'kh' else 'kh'
    user_languages[chat_id] = new_lang
    user_name = call.from_user.first_name or "អតិថិជន"
    
    bot.edit_message_caption(caption=texts[new_lang]['welcome'].format(name=user_name), chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_inline_lang_keyboard(new_lang))
    bot.send_message(chat_id, texts[new_lang]['lang_changed'], reply_markup=get_main_keyboard(new_lang))

# មុខងារពេលចុចលើកញ្ចប់ជួលណាមួយ
@bot.callback_query_handler(func=lambda call: call.data in ['rent_1m', 'rent_2m', 'rent_3m'])
def handle_rent_payment_callback(call):
    chat_id = call.message.chat.id
    lang = get_user_lang(chat_id)
    bot.answer_callback_query(call.id)
    
    simulate_typing_delay(chat_id)
    
    # កំណត់ឈ្មោះកញ្ចប់ទៅតាមការចុច
    packages = {
        'rent_1m': "1 Month 2.50$",
        'rent_2m': "2 Month 4.99$",
        'rent_3m': "3 Month 7.00$"
    }
    selected_package = packages[call.data]
    
    # ផ្ញើសារប្រាប់ពីកញ្ចប់ និងសុំ API Token + KHQR
    msg = bot.send_message(
        chat_id, 
        texts[lang]['package_selected'].format(package=selected_package)
    )
    
    # ចាំទទួលទិន្នន័យពីអតិថិជន (អាចជាអក្សរ ឬរូបភាព)
    bot.register_next_step_handler(msg, process_user_data)

# មុខងារទទួលយកទិន្នន័យ (API Token ឬ KHQR) ពីអតិថិជន
# ប្រើ content_types=['text', 'photo'] ដើម្បីអាចទទួលបានទាំងអក្សរ និងរូបភាព
def process_user_data(message):
    chat_id = message.chat.id
    lang = get_user_lang(chat_id)
    
    simulate_typing_delay(chat_id)
    
    # ផ្ញើសារបញ្ជាក់ថាទទួលបានទិន្នន័យ
    bot.reply_to(message, texts[lang]['data_received'])

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    lang = get_user_lang(chat_id)
    text = message.text

    if text in [texts['kh']['btn_manage'], texts['en']['btn_manage']]:
        simulate_typing_delay(chat_id)
        bot.reply_to(message, texts[lang]['manage_text'])

    elif text in [texts['kh']['btn_rent'], texts['en']['btn_rent']]:
        simulate_typing_delay(chat_id)
        bot.send_message(chat_id, texts[lang]['rent_menu_text'], reply_markup=get_rent_keyboard(lang))

    elif text in [texts['kh']['btn_bot_smm'], texts['en']['btn_bot_smm']]:
        simulate_typing_delay(chat_id)
        bot.send_message(chat_id, texts[lang]['bot_smm_text'], reply_markup=get_smm_pricing_keyboard())

    elif text in [texts['kh']['btn_back'], texts['en']['btn_back']]:
        simulate_typing_delay(chat_id)
        bot.send_message(chat_id, texts[lang]['main_menu_text'], reply_markup=get_main_keyboard(lang))

print("Bot កំពុងដំណើរការ...")
bot.polling(none_stop=True)
