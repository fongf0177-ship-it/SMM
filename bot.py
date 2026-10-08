import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

# ទាញយក Token ពី Environment Variables របស់ Railway
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ---------------- ផ្នែកចាប់ផ្តើម (/start) ----------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton('🥷 Account'), KeyboardButton('🛍 Store'))
    markup.row(KeyboardButton('💸 Deposit'), KeyboardButton('💬 Admin'))
    markup.row(KeyboardButton('📚 How to use'), KeyboardButton('🕒 Purchase history'))

    bot.send_message(message.chat.id, "Hello! Welcome to Toad Store 24/7\nPlease select a service below", reply_markup=markup)

    inline_markup = InlineKeyboardMarkup()
    inline_markup.row(
        InlineKeyboardButton('🇰🇭 ខ្មែរ', callback_data='lang_kh'),
        InlineKeyboardButton('🇬🇧 English', callback_data='lang_en')
    )

    bot.send_message(message.chat.id, "សូមជ្រើសរើសភាសា / Please choose your language:", reply_markup=inline_markup)


# ---------------- មុខងារគណនី (Account Info) ----------------
@bot.message_handler(func=lambda message: message.text in ['🥷 គណនី', '🥷 Account'])
def show_account_info(message):
    user = message.from_user
    
    # ទាញយក Username និង ID ពិតប្រាកដពី Telegram
    username = f"@{user.username}" if user.username else "មិនមាន (None)"
    user_id = user.id
    
    # ទិន្នន័យសាកល្បង (Mock Data) សម្រាប់ Rank និង Balance
    rank = "Newbie 🟢" 
    balance = "$0.00"

    account_text = (
        "👤 **ព័ត៌មានគណនីរបស់អ្នក (Your Account):**\n\n"
        f"🔹 **Username:** {username}\n"
        f"🔹 **ID:** `{user_id}`\n"
        f"🔹 **Rank:** {rank}\n"
        f"🔹 **Balance:** {balance}"
    )
    
    bot.send_message(message.chat.id, account_text, parse_mode="Markdown")


# ---------------- មុខងារដាក់ប្រាក់ (Deposit Flow) ----------------
@bot.message_handler(func=lambda message: message.text in ['💸 ដាក់ប្រាក់', '💸 Deposit'])
def ask_deposit_amount(message):
    msg = bot.send_message(message.chat.id, "សូមបញ្ចូលចំនួនប្រាក់ដែលអ្នកចង់ដាក់ (ឧទាហរណ៍: 10, 50, 100):\n\nPlease enter the amount you want to deposit:")
    bot.register_next_step_handler(msg, process_amount_step)

def process_amount_step(message):
    amount = message.text
    qr_url = "https://img.sanishtech.com/u/0408236e7a40ead82aa09cd34e876f46.jpeg"
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('❌ បោះបង់ / Cancel', callback_data='cancel_deposit'),
        InlineKeyboardButton('✅ បញ្ជាក់ / Confirm', callback_data='confirm_deposit')
    )
    
    caption = f"ចំនួនទឹកប្រាក់ដែលត្រូវបង់ / Amount to pay: **{amount}**\n\nសូមស្កេន QR Code ខាងក្រោមដើម្បីធ្វើការទូទាត់ប្រាក់។\nPlease scan the QR code below to make a payment."
    bot.send_photo(message.chat.id, photo=qr_url, caption=caption, parse_mode="Markdown", reply_markup=markup)


# ---------------- ចាប់យក Callback Query (ប៊ូតុងជាប់សារ) ----------------
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    # --- ផ្នែកភាសា ---
    if call.data == 'lang_kh':
        khmer_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        khmer_markup.row(KeyboardButton('🥷 គណនី'), KeyboardButton('🛍 ហាង'))
        khmer_markup.row(KeyboardButton('💸 ដាក់ប្រាក់'), KeyboardButton('💬 Admin'))
        khmer_markup.row(KeyboardButton('📚 របៀបប្រើប្រាស់'), KeyboardButton('🕒 ប្រវត្តិទិញ'))
        bot.send_message(chat_id, 'អ្នកបានជ្រើសរើសភាសាខ្មែរ។', reply_markup=khmer_markup)
        
    elif call.data == 'lang_en':
        english_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        english_markup.row(KeyboardButton('🥷 Account'), KeyboardButton('🛍 Store'))
        english_markup.row(KeyboardButton('💸 Deposit'), KeyboardButton('💬 Admin'))
        english_markup.row(KeyboardButton('📚 How to use'), KeyboardButton('🕒 Purchase history'))
        bot.send_message(chat_id, 'You have selected English.', reply_markup=english_markup)
        
    # --- ផ្នែកដាក់ប្រាក់ ---
    elif call.data == 'cancel_deposit':
        bot.edit_message_caption(chat_id=chat_id, message_id=call.message.message_id, caption="❌ ប្រតិបត្តិការដាក់ប្រាក់ត្រូវបានបោះបង់!\nDeposit transaction cancelled!")
        
    elif call.data == 'confirm_deposit':
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        msg = bot.send_message(chat_id, "សូមផ្ញើរូបភាពវិក្កយបត្រ (Screenshot) នៃការផ្ទេដើម្បីបង្កើតមុខងារបង្ហាញព័ត៌មានគណនី (Username, ID, Rank, Balance) នៅពេលគេចុចប៊ូតុង **"🥷 គណនី"** ឬ **"🥷 Account"** យើងត្រូវបន្ថែមមុខងារចាប់យកពាក្យនេះ។ 

ដោយសារយើងមិនទាន់មានភ្ជាប់ប្រព័ន្ធ Database (ឃ្លាំងផ្ទុកទិន្នន័យ) សម្រាប់រក្សាទុកលុយ ឬ Rank នៅឡើយ ដូច្នេះកន្លែង Rank និង Balance ខ្ញុំនឹងដាក់ជាទិន្នន័យគំរូ (Default) សិន។ ចំណែកឯ Username និង ID គឺ Bot អាចទាញយកពីគណនី Telegram របស់អ្នកប្រើប្រាស់បានដោយស្វ័យប្រវត្តិ។

ខាងក្រោមនេះជា **កូដពេញលេញ (Full Code)** ដែលបានបន្ថែមមុខងារគណនីរួចរាល់៖

```python
import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading

# ទាញយក Token ពី Environment Variables របស់ Railway
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ចាប់យកពាក្យបញ្ជា /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton('🥷 Account'), KeyboardButton('🛍 Store'))
    markup.row(KeyboardButton('💸 Deposit'), KeyboardButton('💬 Admin'))
    markup.row(KeyboardButton('📚 How to use'), KeyboardButton('🕒 Purchase history'))

    bot.send_message(message.chat.id, "Hello! Welcome to Toad Store 24/7\nPlease select a service below", reply_markup=markup)

    inline_markup = InlineKeyboardMarkup()
    inline_markup.row(
        InlineKeyboardButton('🇰🇭 ខ្មែរ', callback_data='lang_kh'),
        InlineKeyboardButton('🇬🇧 English', callback_data='lang_en')
    )

    bot.send_message(message.chat.id, "សូមជ្រើសរើសភាសា / Please choose your language:", reply_markup=inline_markup)


# ---------------- មុខងារគណនី (Account Info) ----------------
@bot.message_handler(func=lambda message: message.text in ['🥷 គណនី', '🥷 Account'])
def show_account_info(message):
    user = message.from_user
    # ពិនិត្យមើលថាអ្នកប្រើមាន Username ឬអត់
    username = f"@{user.username}" if user.username else "មិនមាន (None)"
    
    # ទិន្នន័យគំរូ (ដោយសារមិនទាន់ភ្ជាប់ Database)
    rank = "សមាជិកធម្មតា (Normal Member)"
    balance = "$0.00"
    
    msg_text = (
        "📋 **ព័ត៌មានគណនីរបស់អ្នក / Your Account Info:**\n\n"
        f"👤 **Username:** {username}\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"🔰 **Rank:** {rank}\n"
        f"💰 **Balance:** {balance}"
    )
    # ផ្ញើសារដោយប្រើ Markdown ដើម្បីឲ្យអក្សរដិត និង ID អាច Copy បានងាយស្រួល
    bot.send_message(message.chat.id, msg_text, parse_mode="Markdown")


# ---------------- មុខងារដាក់ប្រាក់ (Deposit Flow) ----------------
@bot.message_handler(func=lambda message: message.text in ['💸 ដាក់ប្រាក់', '💸 Deposit'])
def ask_deposit_amount(message):
    msg = bot.send_message(message.chat.id, "សូមបញ្ចូលចំនួនប្រាក់ដែលអ្នកចង់ដាក់ (ឧទាហរណ៍: 10, 50, 100):\n\nPlease enter the amount you want to deposit:")
    bot.register_next_step_handler(msg, process_amount_step)

def process_amount_step(message):
    amount = message.text
    qr_url = "[https://img.sanishtech.com/u/0408236e7a40ead82aa09cd34e876f46.jpeg](https://img.sanishtech.com/u/0408236e7a40ead82aa09cd34e876f46.jpeg)"
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('❌ បោះបង់ / Cancel', callback_data='cancel_deposit'),
        InlineKeyboardButton('✅ បញ្ជាក់ / Confirm', callback_data='confirm_deposit')
    )
    
    caption = f"ចំនួនទឹកប្រាក់ដែលត្រូវបង់ / Amount to pay: **{amount}**\n\nសូមស្កេន QR Code ខាងក្រោមដើម្បីធ្វើការទូទាត់ប្រាក់។\nPlease scan the QR code below to make a payment."
    bot.send_photo(message.chat.id, photo=qr_url, caption=caption, parse_mode="Markdown", reply_markup=markup)


# ---------------- ចាប់យកការចុចប៊ូតុងជាប់សារ (Callback Query) ----------------
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == 'lang_kh':
        khmer_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        khmer_markup.row(KeyboardButton('🥷 គណនី'), KeyboardButton('🛍 ហាង'))
        khmer_markup.row(KeyboardButton('💸 ដាក់ប្រាក់'), KeyboardButton('💬 Admin'))
        khmer_markup.row(KeyboardButton('📚 របៀបប្រើប្រាស់'), KeyboardButton('🕒 ប្រវត្តិទិញ'))
        bot.send_message(chat_id, 'អ្នកបានជ្រើសរើសភាសាខ្មែរ។', reply_markup=khmer_markup)
        
    elif call.data == 'lang_en':
        english_markup = ReplyKeyboardMarkup(resize_keyboard=True)
        english_markup.row(KeyboardButton('🥷 Account'), KeyboardButton('🛍 Store'))
        english_markup.row(KeyboardButton('💸 Deposit'), KeyboardButton('💬 Admin'))
        english_markup.row(KeyboardButton('📚 How to use'), KeyboardButton('🕒 Purchase history'))
        bot.send_message(chat_id, 'You have selected English.', reply_markup=english_markup)
        
    elif call.data == 'cancel_deposit':
        bot.edit_message_caption(chat_id=chat_id, message_id=call.message.message_id, caption="❌ ប្រតិបត្តិការដាក់ប្រាក់ត្រូវបានបោះបង់!\nDeposit transaction cancelled!")
        
    elif call.data == 'confirm_deposit':
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        msg = bot.send_message(chat_id, "សូមផ្ញើរូបភាពវិក្កយបត្រ (Screenshot) នៃការផ្ទេរប្រាក់របស់អ្នកមកកាន់ទីនេះ ខាងយើងខ្ញុំនឹងធ្វើការពិនិត្យ៖\n\nPlease send your payment screenshot here:")
        bot.register_next_step_handler(msg, process_receipt_step)
        
    bot.answer_callback_query(call.id)

def process_receipt_step(message):
    if message.content_type == 'photo':
        bot.send_message(message.chat.id, "✅ យើងទទួលបានវិក្កយបត្ររបស់អ្នកហើយ! ទឹកប្រាក់នឹងត្រូវបានបញ្ចូលទៅក្នុងគណនីរបស់អ្នកបន្ទាប់ពីការត្រួតពិនិត្យរួចរាល់។\n\n✅ We have received your receipt! The amount will be credited to your account after verification.")
    else:
        msg = bot.send_message(message.chat.id, "❌ សូមបញ្ជូនជា **រូបភាពវិក្កយបត្រ (Screenshot)** ប៉ុណ្ណោះ។ សូមព្យាយាមផ្ញើម្តងទៀត៖\n\n❌ Please send an **image screenshot** only. Try again:")
        bot.register_next_step_handler(msg, process_receipt_step)


# ---------------- Web Server សម្រាប់ Railway ----------------
@app.route('/')
def index():
    return "Telegram Bot is running smoothly on Railway using Python!"

def run_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN is missing!")
    else:
        server_thread = threading.Thread(target=run_server)
        server_thread.start()
        
        print("Bot is polling for messages...")
        bot.infinity_polling()
