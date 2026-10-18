import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os
import time
import random

# យក Token របស់ Bot ពី Environment Variables
TOKEN = os.environ.get('BOT_TOKEN', 'ដាក់_TOKEN_របស់អ្នកនៅទីនេះ')
bot = telebot.TeleBot(TOKEN)

user_languages = {}

# វចនានុក្រមអត្ថបទ
texts = {
    'kh': {
        'welcome': "សួស្តី {name}! សូមជ្រើសរើសសេវាកម្មខាងក្រោម៖",
        'select_below': "👇 សូមជ្រើសរើសជម្រើសនៅខាងក្រោម៖",
        'btn_manage': "👨🏻‍💻 គ្រប់គ្រងគណនី",
        'btn_rent': "🛍 ជួលសេវាកម្ម",
        'btn_change_lang_inline': "🇬🇧 ភាសាអង់គ្លេស (English)",
        'manage_text': "នេះគឺជាទំព័រសម្រាប់ គ្រប់គ្រងគណនី របស់អ្នក។",
        'rent_menu_text': "សូមជ្រើសរើសសេវាកម្មដែលអ្នកចង់ជួលខាងក្រោម៖",
        'btn_bot_smm': "🤖 BOT SMM",
        'btn_back': "🔙 ត្រឡប់ក្រោយ",
        'bot_smm_text': "តារាងសម្រាប់លោកអ្នកជួល Telegram bot តម្លៃ :",
        'main_menu_text': "អ្នកបានត្រឡប់មកម៉ឺនុយដើមវិញ៖",
        'lang_changed': "ភាសាត្រូវបានផ្លាស់ប្តូរទៅជា ខ្មែរ 🇰🇭"
    },
    'en': {
        'welcome': "Hello {name}! Please select a service below:",
        'select_below': "👇 Please select an option below:",
        'btn_manage': "👨🏻‍💻 Manage Account",
        'btn_rent': "🛍 Rent Service",
        'btn_change_lang_inline': "🇰🇭 ភាសាខ្មែរ (Khmer)",
        'manage_text': "This is your Account Management page.",
        'rent_menu_text': "Please select a service you want to rent below:",
        'btn_bot_smm': "🤖 BOT SMM",
        'btn_back': "🔙 Back",
        'bot_smm_text': "Table for renting Telegram bot, Prices :",
        'main_menu_text': "You are back to the Main Menu:",
        'lang_changed': "Language changed to English 🇬🇧"
    }
}

def get_user_lang(chat_id):
    return user_languages.get(chat_id, 'kh')

# ម៉ឺនុយដើម
def get_main_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_manage = KeyboardButton(texts[lang]['btn_manage'])
    btn_rent = KeyboardButton(texts[lang]['btn_rent'])
    markup.add(btn_manage, btn_rent)
    return markup

# ម៉ឺនុយជួលសេវាកម្ម
def get_rent_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    btn_bot_smm = KeyboardButton(texts[lang]['btn_bot_smm'])
    btn_back = KeyboardButton(texts[lang]['btn_back'])
    markup.add(btn_bot_smm, btn_back)
    return markup

# ប៊ូតុងប្តូរភាសា
def get_inline_lang_keyboard(lang):
    markup = InlineKeyboardMarkup()
    btn_lang = InlineKeyboardButton(text=texts[lang]['btn_change_lang_inline'], callback_data='change_lang')
    markup.add(btn_lang)
    return markup

# ប៊ូតុងតម្លៃជួល BOT SMM (Inline Buttons)
def get_smm_pricing_keyboard():
    # កំណត់ row_width=3 ដើម្បីឱ្យប៊ូតុងទាំង៣ ស្ថិតក្នុងជួរដេកតែមួយ
    markup = InlineKeyboardMarkup(row_width=3)
    btn1 = InlineKeyboardButton("🛍️ 1 Month 2.50$", callback_data='rent_1_month')
    btn2 = InlineKeyboardButton("🛍️ 2 Month 4.99$", callback_data='rent_2_months')
    btn3 = InlineKeyboardButton("🛍️ 3 Month 7.00$", callback_data='rent_3_months')
    markup.add(btn1, btn2, btn3)
    return markup

def simulate_typing_delay(chat_id):
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(random.uniform(1.0, 2.0))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name or "អតិថិជន"
    lang = get_user_lang(chat_id)
    
    simulate_typing_delay(chat_id)

    image_url = "https://img.sanishtech.com/u/23589ed30a9f482112e591c0f4c9fa18.png"
    caption_text = texts[lang]['welcome'].format(name=user_name)
    
    bot.send_photo(
        chat_id=chat_id,
        photo=image_url,
        caption=caption_text,
        reply_markup=get_inline_lang_keyboard(lang)
    )
    
    bot.send_message(
        chat_id=chat_id,
        text=texts[lang]['select_below'],
        reply_markup=get_main_keyboard(lang)
    )

@bot.callback_query_handler(func=lambda call: call.data == 'change_lang')
def handle_change_lang_callback(call):
    chat_id = call.message.chat.id
    current_lang = get_user_lang(chat_id)
    
    new_lang = 'en' if current_lang == 'kh' else 'kh'
    user_languages[chat_id] = new_lang
    user_name = call.from_user.first_name or "អតិថិជន"
    
    bot.edit_message_caption(
        caption=texts[new_lang]['welcome'].format(name=user_name),
        chat_id=chat_id,
        message_id=call.message.message_id,
        reply_markup=get_inline_lang_keyboard(new_lang)
    )
    
    bot.send_message(
        chat_id=chat_id,
        text=texts[new_lang]['lang_changed'],
        reply_markup=get_main_keyboard(new_lang)
    )

# មុខងារចាំចាប់ការចុចលើប៊ូតុងជួល (១ខែ ២ខែ ៣ខែ)
@bot.callback_query_handler(func=lambda call: call.data.startswith('rent_'))
def handle_rent_payment_callback(call):
    chat_id = call.message.chat.id
    # អ្នកអាចបន្ថែមមុខងារបង់ប្រាក់ ឬភ្ជាប់ទៅ Admin នៅទីនេះ
    bot.answer_callback_query(call.id, "សូមអរគុណ! Admin នឹងទាក់ទងទៅអ្នកឆាប់ៗនេះ។", show_alert=True)

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
        bot.send_message(
            chat_id, 
            texts[lang]['rent_menu_text'], 
            reply_markup=get_rent_keyboard(lang) 
        )

    # ពេលចុចលើពាក្យ BOT SMM វានឹងទម្លាក់តារាងតម្លៃ
    elif text in [texts['kh']['btn_bot_smm'], texts['en']['btn_bot_smm']]:
        simulate_typing_delay(chat_id)
        bot.send_message(
            chat_id,
            texts[lang]['bot_smm_text'],
            reply_markup=get_smm_pricing_keyboard() # ហៅប៊ូតុងតម្លៃមកបង្ហាញ
        )

    elif text in [texts['kh']['btn_back'], texts['en']['btn_back']]:
        simulate_typing_delay(chat_id)
        bot.send_message(
            chat_id, 
            texts[lang]['main_menu_text'], 
            reply_markup=get_main_keyboard(lang) 
        )

print("Bot កំពុងដំណើរការ...")
bot.polling(none_stop=True)
