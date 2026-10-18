import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os
import time
import random

# យក Token របស់ Bot ពី Environment Variables
TOKEN = os.environ.get('BOT_TOKEN', 'ដាក់_TOKEN_របស់អ្នកនៅទីនេះ')
bot = telebot.TeleBot(TOKEN)

# ផ្ទុកទិន្នន័យភាសារបស់អ្នកប្រើប្រាស់ម្នាក់ៗ (ឧទាហរណ៍: { 123456789: 'kh' })
user_languages = {}

# វចនានុក្រមសម្រាប់ផ្ទុកអត្ថបទទាំង២ភាសា (ងាយស្រួលកែប្រែនៅពេលក្រោយ)
texts = {
    'kh': {
        'welcome': "សួស្តី {name}! សូមជ្រើសរើសសេវាកម្មខាងក្រោម៖",
        'btn_manage': "👨🏻‍💻 គ្រប់គ្រងគណនី",
        'btn_rent': "🛍 ជួលសេវាកម្ម",
        'btn_change_lang': "🇬🇧 ភាសាអង់គ្លេស (English)",
        'manage_text': "នេះគឺជាទំព័រសម្រាប់ គ្រប់គ្រងគណនី របស់អ្នក។",
        'rent_text': "សូមជ្រើសរើសសេវាកម្មដែលអ្នកចង់ជួល។",
        'lang_changed': "ភាសាត្រូវបានផ្លាស់ប្តូរទៅជា ខ្មែរ 🇰🇭"
    },
    'en': {
        'welcome': "Hello {name}! Please select a service below:",
        'btn_manage': "👨🏻‍💻 Manage Account",
        'btn_rent': "🛍 Rent Service",
        'btn_change_lang': "🇰🇭 ភាសាខ្មែរ (Khmer)",
        'manage_text': "This is your Account Management page.",
        'rent_text': "Please select the service you want to rent.",
        'lang_changed': "Language changed to English 🇬🇧"
    }
}

# អនុគមន៍សម្រាប់យកភាសាដែលអ្នកប្រើប្រាស់កំពុងប្រើ (Default គឺ 'kh')
def get_user_lang(chat_id):
    return user_languages.get(chat_id, 'kh')

# អនុគមន៍សម្រាប់បង្កើតផ្ទាំង Keyboard ទៅតាមភាសា
def get_main_keyboard(lang):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_manage = KeyboardButton(texts[lang]['btn_manage'])
    btn_rent = KeyboardButton(texts[lang]['btn_rent'])
    btn_lang = KeyboardButton(texts[lang]['btn_change_lang'])
    
    markup.add(btn_manage, btn_rent)
    markup.add(btn_lang) # ដាក់ប៊ូតុងប្តូរភាសានៅខាងក្រោម
    return markup

# អនុគមន៍សម្រាប់ធ្វើឱ្យ Bot គិតយឺត (Delay 3 ទៅ 4 វិនាទី)
def simulate_typing_delay(chat_id):
    # បង្ហាញសកម្មភាព "កំពុងវាយអក្សរ..." ទៅកាន់អ្នកប្រើប្រាស់
    bot.send_chat_action(chat_id, 'typing')
    # ពន្យារពេលចន្លោះពី 3 ទៅ 4 វិនាទី
    time.sleep(random.uniform(3.0, 4.0))

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name or "អតិថិជន"
    lang = get_user_lang(chat_id)
    
    # ធ្វើឱ្យ Bot Delay មុននឹងឆ្លើយតប
    simulate_typing_delay(chat_id)

    markup = get_main_keyboard(lang)
    caption_text = texts[lang]['welcome'].format(name=user_name)
    image_url = "https://img.sanishtech.com/u/23589ed30a9f482112e591c0f4c9fa18.png"
    
    bot.send_photo(
        chat_id=chat_id,
        photo=image_url,
        caption=caption_text,
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    lang = get_user_lang(chat_id)
    text = message.text

    # ប្រសិនបើអ្នកប្រើប្រាស់ចុចប៊ូតុងប្តូរភាសា
    if text in [texts['kh']['btn_change_lang'], texts['en']['btn_change_lang']]:
        # ធ្វើឱ្យ Bot Delay 
        simulate_typing_delay(chat_id)
        
        # ប្តូរភាសា
        new_lang = 'en' if lang == 'kh' else 'kh'
        user_languages[chat_id] = new_lang
        
        # ផ្ញើសារប្រាប់ថាប្តូរជោគជ័យ ជាមួយ Keyboard ភាសាថ្មី
        bot.send_message(
            chat_id, 
            texts[new_lang]['lang_changed'], 
            reply_markup=get_main_keyboard(new_lang)
        )
        return

    # ពិនិត្យមើលការចុចប៊ូតុង គ្រប់គ្រងគណនី (ទាំងភាសាខ្មែរ និងអង់គ្លេស)
    if text in [texts['kh']['btn_manage'], texts['en']['btn_manage']]:
        simulate_typing_delay(chat_id)
        bot.reply_to(message, texts[lang]['manage_text'])

    # ពិនិត្យមើលការចុចប៊ូតុង ជួលសេវាកម្ម (ទាំងភាសាខ្មែរ និងអង់គ្លេស)
    elif text in [texts['kh']['btn_rent'], texts['en']['btn_rent']]:
        simulate_typing_delay(chat_id)
        bot.reply_to(message, texts[lang]['rent_text'])

print("Bot កំពុងដំណើរការ...")
# ប្រើ none_stop=True ដើម្បីការពារកុំឱ្យ Bot គាំងពេលមាន Error តូចតាច
bot.polling(none_stop=True)
