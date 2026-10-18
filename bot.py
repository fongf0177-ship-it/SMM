import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os

# យក Token របស់ Bot ពី Environment Variables
TOKEN = os.environ.get('BOT_TOKEN', 'ដាក់_TOKEN_របស់អ្នកនៅទីនេះ')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # ទាញយកឈ្មោះរបស់អ្នកប្រើប្រាស់ (First Name)
    # បើចង់បាន @username អាចប្រើ message.from_user.username ប៉ុន្តែអ្នកប្រើខ្លះអត់បានដាក់ username ទេ
    user_name = message.from_user.first_name 
    if not user_name:
        user_name = "អតិថិជន" # ដាក់ឈ្មោះបម្រុង បើករណីរកឈ្មោះមិនឃើញ

    # បង្កើតផ្ទាំង Keyboard សម្រាប់ផ្ទុកប៊ូតុង
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("👨🏻‍💻 គ្រប់គ្រងគណនី")
    btn2 = KeyboardButton("ជួលសេវាកម្ម")
    markup.add(btn1, btn2)
    
    # បង្កើតអត្ថបទ Caption ដែលមានបញ្ចូលឈ្មោះ
    caption_text = f"សួស្តី! {user_name} សូមជ្រើសរើសសេវាកម្មខាងក្រោម៖"
    
    # URL រូបភាពដែលអ្នកបានផ្តល់ឱ្យ
    image_url = "https://img.sanishtech.com/u/23589ed30a9f482112e591c0f4c9fa18.png"
    
    # ប្រើ bot.send_photo ដើម្បីផ្ញើរូបភាពព្រមទាំងអក្សរនៅខាងក្រោមរូប (Caption) និងប៊ូតុង
    bot.send_photo(
        chat_id=message.chat.id,
        photo=image_url,
        caption=caption_text,
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == "👨🏻‍💻 គ្រប់គ្រងគណនី":
        bot.reply_to(message, "នេះគឺជាទំព័រសម្រាប់ គ្រប់គ្រងគណនី របស់អ្នក។")
    elif message.text == "ជួលសេវាកម្ម":
        bot.reply_to(message, "សូមជ្រើសរើសសេវាកម្មដែលអ្នកចង់ជួល។")

print("Bot កំពុងដំណើរការ...")
bot.polling()
