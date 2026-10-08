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
    # បង្កើតប៊ូតុងខាងក្រោម (Reply Keyboard)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton('🥷 Account'), KeyboardButton('🛍 Store'))
    markup.row(KeyboardButton('💸 Deposit'), KeyboardButton('💬 Admin'))
    markup.row(KeyboardButton('📚 How to use'), KeyboardButton('🕒 Purchase history'))

    # ផ្ញើសារស្វាគមន៍ទី១
    bot.send_message(message.chat.id, "Hello! Welcome to Toad Store 24/7\nPlease select a service below", reply_markup=markup)

    # បង្កើតប៊ូតុងជាប់សារសម្រាប់ជ្រើសរើសភាសា (Inline Keyboard)
    inline_markup = InlineKeyboardMarkup()
    inline_markup.row(
        InlineKeyboardButton('🇰🇭 ខ្មែរ', callback_data='lang_kh'),
        InlineKeyboardButton('🇬🇧 English', callback_data='lang_en')
    )

    # ផ្ញើសារទី២
    bot.send_message(message.chat.id, "សូមជ្រើសរើសភាសា / Please choose your language:", reply_markup=inline_markup)

# ចាប់យកការចុចប៊ូតុងភាសា
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'lang_kh':
        bot.send_message(call.message.chat.id, 'អ្នកបានជ្រើសរើសភាសាខ្មែរ។')
    elif call.data == 'lang_en':
        bot.send_message(call.message.chat.id, 'You have selected English.')
    
    # ជម្រះការជូនដំណឹង Loading លើប៊ូតុង
    bot.answer_callback_query(call.id)

# បង្កើត Web Server តូចមួយដើម្បីកុំឲ្យ Railway Error
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
        # ដំណើរការ Web Server ស្របពេលជាមួយ Bot
        server_thread = threading.Thread(target=run_server)
        server_thread.start()
        
        print("Bot is polling for messages...")
        bot.infinity_polling()
