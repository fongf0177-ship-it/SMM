import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os

# យក Token ពី Environment Variable (សម្រាប់ Railway)
TOKEN = os.environ.get('BOT_TOKEN', 'ដាក់_TOKEN_របស់អ្នកនៅទីនេះ')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # បង្កើតប៊ូតុង
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("👨🏻‍💻 គ្រប់គ្រងគណនី")
    btn2 = KeyboardButton("ជួលសេវាកម្ម")
    markup.add(btn1, btn2)
    
    bot.reply_to(message, "សួស្តី! សូមជ្រើសរើសសេវាកម្មខាងក្រោម៖", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == "👨🏻‍💻 គ្រប់គ្រងគណនី":
        bot.reply_to(message, "នេះគឺជាទំព័រសម្រាប់ គ្រប់គ្រងគណនី របស់អ្នក។")
    elif message.text == "ជួលសេវាកម្ម":
        bot.reply_to(message, "សូមជ្រើសរើសសេវាកម្មដែលអ្នកចង់ជួល។")

print("Bot កំពុងដំណើរការ...")
bot.polling()
