import os
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import threading
import datetime
import random

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ទិន្នន័យបណ្តោះអាសន្ន
user_orders = {}
user_balances = {}    
pending_deposits = {} 
user_purchase_history = {}

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
    username = f"@{user.username}" if user.username else "មិនមាន (None)"
    rank = "សមាជិកធម្មតា (Normal Member)"
    current_balance = user_balances.get(message.chat.id, 0.0)
    
    msg_text = (
        "📋 **ព័ត៌មានគណនីរបស់អ្នក / Your Account Info:**\n\n"
        f"👤 **Username:** {username}\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"🔰 **Rank:** {rank}\n"
        f"💰 **Balance:** ${current_balance:.2f}"
    )
    bot.send_message(message.chat.id, msg_text, parse_mode="Markdown")

# ---------------- មុខងារហាង (Store) ----------------
@bot.message_handler(func=lambda message: message.text in ['🛍 ហាង', '🛍 Store'])
def show_store(message):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('🎁 Facebook', callback_data='store_fb'),
        InlineKeyboardButton('🎁 Tik Tok', callback_data='store_tt')
    )
    bot.send_message(message.chat.id, "🛒 សូមជ្រើសរើសសេវាកម្មខាងក្រោម / Please select a service below:", reply_markup=markup)

# ---------------- មុខងារ Admin (Contact Support) ----------------
@bot.message_handler(func=lambda message: message.text in ['💬 Admin'])
def show_admin_contact(message):
    admin_text = (
        "👨‍💻 **ផ្នែកសេវាកម្មអតិថិជន (Customer Support)**\n\n"
        "ប្រសិនបើអ្នកមានបញ្ហា ឬមិនយល់កន្លែងណា អាចទាក់ទងក្រុមការងារយើងបាន៖\n\n"
        "💬 @Longzzsmmdigitall\n"
        "💬 @AdzayTER"
    )
    bot.send_message(message.chat.id, admin_text, parse_mode="Markdown")

# ---------------- មុខងាររបៀបប្រើប្រាស់ (How to use) ----------------
@bot.message_handler(func=lambda message: message.text in ['📚 របៀបប្រើប្រាស់', '📚 How to use'])
def show_how_to_use(message):
    tutorial_text = (
        "📚 **របៀបប្រើប្រាស់ (How to use):**\n\n"
        "សូមចូលទៅកាន់តំណភ្ជាប់ខាងក្រោមដើម្បីមើលការណែនាំពីរបៀបប្រើប្រាស់ Bot នេះ៖\n"
        "👉 https://t.me/MT5SMM/4"
    )
    # បិទ disable_web_page_preview ក្រែងលោចង់ឲ្យលោតរូបភាពរបស់ Link
    bot.send_message(message.chat.id, tutorial_text, parse_mode="Markdown")

# ---------------- មុខងារប្រវត្តិទិញ (Purchase History) ----------------
@bot.message_handler(func=lambda message: message.text in ['🕒 ប្រវត្តិទិញ', '🕒 Purchase history'])
def show_purchase_history(message):
    chat_id = message.chat.id
    history = user_purchase_history.get(chat_id, [])
    
    if not history:
        bot.send_message(chat_id, "📭 អ្នកមិនទាន់មានប្រវត្តិទិញនៅឡើយទេ / You have no purchase history yet.")
        return
        
    history_text = "🕒 **ប្រវត្តិទិញចុងក្រោយរបស់អ្នក / Your Recent Purchases:**\n\n"
    for item in reversed(history[-10:]):
        history_text += (
            f"🆔 **ID:** `{item['order_id']}`\n"
            f"🔹 **សេវាកម្ម:** {item['service']} (ចំនួន: {item['quantity']})\n"
            f"💵 **តម្លៃ:** ${item['price']:.2f}\n"
            f"⏰ **ពេលវេលា:** {item['time']}\n"
            "-----------------------\n"
        )
    bot.send_message(chat_id, history_text, parse_mode="Markdown")

# ---------------- មុខងារដាក់ប្រាក់ (Deposit Flow) ----------------
@bot.message_handler(func=lambda message: message.text in ['💸 ដាក់ប្រាក់', '💸 Deposit'])
def ask_deposit_amount(message):
    msg = bot.send_message(message.chat.id, "សូមបញ្ចូលចំនួនប្រាក់ដែលអ្នកចង់ដាក់ (ឧទាហរណ៍: 10, 50, 100):\n\nPlease enter the amount you want to deposit:")
    bot.register_next_step_handler(msg, process_amount_step)

def process_amount_step(message):
    try:
        amount = float(message.text)
        if amount <= 0: raise ValueError
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ សូមបញ្ចូលចំនួនប្រាក់ជាលេខឲ្យបានត្រឹមត្រូវ! សាកល្បងម្តងទៀត៖")
        bot.register_next_step_handler(msg, process_amount_step)
        return

    pending_deposits[message.chat.id] = amount
    qr_url = "https://img.sanishtech.com/u/0408236e7a40ead82aa09cd34e876f46.jpeg"
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('❌ បោះបង់ / Cancel', callback_data='cancel_deposit'),
        InlineKeyboardButton('✅ បញ្ជាក់ / Confirm', callback_data='confirm_deposit')
    )
    
    caption = f"ចំនួនទឹកប្រាក់ដែលត្រូវបង់ / Amount to pay: **${amount:.2f}**\n\nសូមស្កេន QR Code ខាងក្រោមដើម្បីធ្វើការទូទាត់ប្រាក់។\nPlease scan the QR code below to make a payment."
    bot.send_photo(message.chat.id, photo=qr_url, caption=caption, parse_mode="Markdown", reply_markup=markup)

# ---------------- មុខងារបញ្ជាទិញសេវាកម្ម (Order Flow) ----------------
def process_url_step(message):
    chat_id = message.chat.id
    if chat_id not in user_orders: return
    user_orders[chat_id]['url'] = message.text
    msg = bot.send_message(chat_id, "🔢 សូមបញ្ចូលចំនួនដែលអ្នកចង់បាន (ឧទាហរណ៍: 1000):\n\nPlease enter the quantity:")
    bot.register_next_step_handler(msg, process_quantity_step)

def process_quantity_step(message):
    chat_id = message.chat.id
    if chat_id not in user_orders: return
        
    quantity = message.text
    if not quantity.isdigit() or int(quantity) <= 0:
        msg = bot.send_message(chat_id, "❌ សូមបញ្ចូលចំនួនជាលេខឲ្យបានត្រឹមត្រូវ! សូមបញ្ចូលម្តងទៀត៖")
        bot.register_next_step_handler(msg, process_quantity_step)
        return

    user_orders[chat_id]['quantity'] = int(quantity)
    order = user_orders[chat_id]
    total_price = (order['quantity'] / 1000) * order['price_per_1k']
    order['total_price'] = total_price
    
    current_balance = user_balances.get(chat_id, 0.0)
    
    if current_balance < total_price:
        bot.send_message(
            chat_id, 
            f"❌ **ទឹកប្រាក់របស់អ្នកមិនគ្រប់គ្រាន់ទេ!**\n\n"
            f"💵 តម្លៃសរុប (Total): **${total_price:.2f}**\n"
            f"💰 ទឹកប្រាក់ក្នុងគណនី (Balance): **${current_balance:.2f}**\n\n"
            "សូមធ្វើការដាក់ប្រាក់ (Deposit) ជាមុនសិន។",
            parse_mode="Markdown"
        )
        del user_orders[chat_id]
        return
    
    summary = (
        f"🛒 **ពិនិត្យការបញ្ជាទិញរបស់អ្នក / Order Summary:**\n\n"
        f"🔹 **សេវាកម្ម (Service):** {order['service']}\n"
        f"🔗 **លីង (URL):** {order['url']}\n"
        f"🔢 **ចំនួន (Quantity):** {order['quantity']}\n"
        f"💵 **តម្លៃសរុប (Total Price):** ${total_price:.2f}\n\n"
        "តើអ្នកចង់បន្តការទិញនេះទេ?"
    )
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton('❌ បោះបង់', callback_data='cancel_order'),
        InlineKeyboardButton('✅ បញ្ជាក់ទិញ', callback_data='confirm_order')
    )
    bot.send_message(chat_id, summary, parse_mode="Markdown", reply_markup=markup, disable_web_page_preview=True)

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
        
    elif call.data == 'store_main':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton('🎁 Facebook', callback_data='store_fb'), InlineKeyboardButton('🎁 Tik Tok', callback_data='store_tt'))
        bot.edit_message_text("🛒 សូមជ្រើសរើសសេវាកម្មខាងក្រោម / Please select a service below:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == 'store_fb':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton('👥 Followers', callback_data='fb_followers_options'))
        markup.row(InlineKeyboardButton('🔙 ត្រឡប់ក្រោយ / Back', callback_data='store_main'))
        bot.edit_message_text("📘 ជ្រើសរើសសេវាកម្ម Facebook / Select Facebook service:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data == 'fb_followers_options':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton('✅ ធានា 10ថ្ងៃ (1K / 0.80$)', callback_data='service_fbf_10'))
        markup.row(InlineKeyboardButton('✅ ធានា 5ថ្ងៃ (1K / 0.65$)', callback_data='service_fbf_5'))
        markup.row(InlineKeyboardButton('❌ មិនធានា (1K / 0.58$)', callback_data='service_fbf_0'))
        markup.row(InlineKeyboardButton('🔙 ត្រឡប់ក្រោយ / Back', callback_data='store_fb'))
        bot.edit_message_text("👥 សូមជ្រើសរើសប្រភេទ Followers ដែលអ្នកចង់បាន:", chat_id, call.message.message_id, reply_markup=markup)

    elif call.data == 'store_tt':
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton('❤️ Like', callback_data='service_tt_like'), InlineKeyboardButton('👁 Views', callback_data='service_tt_views'))
        markup.row(InlineKeyboardButton('🔙 ត្រឡប់ក្រោយ / Back', callback_data='store_main'))
        bot.edit_message_text("🎵 ជ្រើសរើសសេវាកម្ម Tik Tok / Select Tik Tok service:", chat_id, call.message.message_id, reply_markup=markup)
        
    elif call.data.startswith('service_'):
        if call.data == 'service_fbf_10': service_name, price_per_1k = "Facebook Followers (ធានា 10ថ្ងៃ)", 0.80
        elif call.data == 'service_fbf_5': service_name, price_per_1k = "Facebook Followers (ធានា 5ថ្ងៃ)", 0.65
        elif call.data == 'service_fbf_0': service_name, price_per_1k = "Facebook Followers (មិនធានា)", 0.58
        elif call.data == 'service_tt_like': service_name, price_per_1k = "Tik Tok Like", 1.00
        elif call.data == 'service_tt_views': service_name, price_per_1k = "Tik Tok Views", 0.50 
        
        user_orders[chat_id] = {'service': service_name, 'price_per_1k': price_per_1k}
        msg = bot.send_message(chat_id, f"🔗 សូមបញ្ចូលលីង (URL) សម្រាប់សេវាកម្ម **{service_name}**:\n\nPlease enter the URL:", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_url_step)

    elif call.data == 'cancel_order':
        bot.edit_message_text("❌ ការបញ្ជាទិញត្រូវបានបោះបង់!\nOrder cancelled!", chat_id, call.message.message_id)
        if chat_id in user_orders: del user_orders[chat_id] 
            
    elif call.data == 'confirm_order':
        if chat_id in user_orders:
            order = user_orders[chat_id]
            total_price = order['total_price']
            current_balance = user_balances.get(chat_id, 0.0)
            
            if current_balance >= total_price:
                user_balances[chat_id] -= total_price
                new_balance = user_balances[chat_id]
                
                order_id = f"OD{random.randint(100000, 999999)}"
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if chat_id not in user_purchase_history:
                    user_purchase_history[chat_id] = []
                user_purchase_history[chat_id].append({
                    'order_id': order_id,
                    'service': order['service'],
                    'quantity': order['quantity'],
                    'price': total_price,
                    'time': current_time
                })
                
                success_msg = (
                    f"✅ ការបញ្ជាទិញទទួលបានជោគជ័យ!\n\n"
                    f"🆔 លេខកូដ (Order ID): `{order_id}`\n"
                    f"ទឹកប្រាក់ **${total_price:.2f}** ត្រូវបានកាត់ពីគណនីរបស់អ្នក។\n"
                    f"💰 សល់ទឹកប្រាក់: **${new_balance:.2f}**\n\n"
                    "អ្នកអាចឆែកមើលក្នុង '🕒 ប្រវត្តិទិញ' បាន។"
                )
                bot.edit_message_text(success_msg, chat_id, call.message.message_id, parse_mode="Markdown")
            else:
                bot.edit_message_text("❌ ទឹកប្រាក់របស់អ្នកមិនគ្រប់គ្រាន់ទេ!", chat_id, call.message.message_id)
            del user_orders[chat_id] 

    elif call.data == 'cancel_deposit':
        bot.edit_message_caption(chat_id=chat_id, message_id=call.message.message_id, caption="❌ ប្រតិបត្តិការដាក់ប្រាក់ត្រូវបានបោះបង់!\nDeposit transaction cancelled!")
        if chat_id in pending_deposits: del pending_deposits[chat_id]
            
    elif call.data == 'confirm_deposit':
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        msg = bot.send_message(chat_id, "សូមផ្ញើរូបភាពវិក្កយបត្រ (Screenshot) នៃការផ្ទេរប្រាក់របស់អ្នកមកកាន់ទីនេះ ខាងយើងខ្ញុំនឹងធ្វើការពិនិត្យ៖\n\nPlease send your payment screenshot here:")
        bot.register_next_step_handler(msg, process_receipt_step)
        
    bot.answer_callback_query(call.id)

def process_receipt_step(message):
    chat_id = message.chat.id
    if message.content_type == 'photo':
        amount = pending_deposits.get(chat_id, 0.0)
        user_balances[chat_id] = user_balances.get(chat_id, 0.0) + amount
        
        if chat_id in pending_deposits: del pending_deposits[chat_id]
        bot.send_message(chat_id, f"✅ យើងទទួលបានវិក្កយបត្ររបស់អ្នកហើយ! ទឹកប្រាក់ **${amount:.2f}** ត្រូវបានបញ្ចូលទៅក្នុងគណនីរបស់អ្នក។\n\nសូមឆែកមើល '🥷 គណនី' របស់អ្នក។", parse_mode="Markdown")
    else:
        msg = bot.send_message(message.chat.id, "❌ សូមបញ្ជូនជា **រូបភាពវិក្កយបត្រ (Screenshot)** ប៉ុណ្ណោះ។ សូមព្យាយាមផ្ញើម្តងទៀត៖")
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
