import telebot
from telebot import types
import requests
import qrcode
from io import BytesIO

# ================= CONFIGURATION =================
BOT_TOKEN = '8995177384:AAHkHgYeZP6a9mYwp-G6D6rnrIKrD607RDs' 
API_KEY = 'YOUR_SMM_API_KEY_HERE' 
API_URL = 'https://YOUR_SMM_PANEL_URL/api/v2' 
UPI_ID = 'YOUR_UPI_ID@upi' 
ADMIN_USERNAME = '@YourAdminUsername'
# =================================================

bot = telebot.TeleBot(BOT_TOKEN)

# --- Start Command & Main Menu ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('🛒 New Order')
    btn2 = types.KeyboardButton('💰 Add Funds')
    btn3 = types.KeyboardButton('👤 Account / Balance')
    btn4 = types.KeyboardButton('📞 Support')
    markup.add(btn1, btn2, btn3, btn4)
    
    welcome_text = (
        f"👋 Swagat hai *{message.from_user.first_name}*!\n\n"
        "🤖 *Main aapka SMM Service Bot hoon.*\n"
        "Niche diye gaye buttons se order lagayein ya funds add karein!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=markup)

# --- 1. Add Funds Option (Automated UPI QR) ---
@bot.message_handler(func=lambda message: message.text == '💰 Add Funds')
def add_funds(message):
    msg = bot.send_message(message.chat.id, "💵 Kitna amount add karna chahte hain? (e.g. 50, 100, 500):")
    bot.register_next_step_handler(msg, generate_qr)

def generate_qr(message):
    try:
        amount = float(message.text)
        upi_url = f"upi://pay?pa={UPI_ID}&pn=SMM_Services&am={amount}&cu=INR"
        
        # Generating Dynamic QR
        qr = qrcode.make(upi_url)
        bio = BytesIO()
        bio.name = 'qr.png'
        qr.save(bio, 'PNG')
        bio.seek(0)
        
        caption = (
            f"📥 *PAYMENT QR CODE*\n\n"
            f"💰 *Amount:* ₹{amount}\n"
            f"🆔 *UPI ID:* `{UPI_ID}`\n\n"
            "📌 *Steps:* QR scan karke payment karein aur Payment Screenshot/UTR ID Admin ko bhej dein."
        )
        bot.send_photo(message.chat.id, photo=bio, caption=caption, parse_mode='Markdown')
    except ValueError:
        bot.send_message(message.chat.id, "❌ Kripya sirf sahi number (digit) enter karein!")

# --- 2. Check SMM Balance ---
@bot.message_handler(func=lambda message: message.text == '👤 Account / Balance')
def account_info(message):
    try:
        response = requests.post(API_URL, data={'key': API_KEY, 'action': 'balance'}).json()
        balance = response.get('balance', 'N/A')
        currency = response.get('currency', 'INR')
        
        info = (
            f"👤 *Aapki Profile*\n\n"
            f"🆔 *User ID:* `{message.from_user.id}`\n"
            f"💼 *SMM Panel Balance:* {balance} {currency}"
        )
        bot.send_message(message.chat.id, info, parse_mode='Markdown')
    except Exception:
        bot.send_message(message.chat.id, "❌ SMM Panel API connect karne me error aa raha hai.")

# --- 3. New Order Info ---
@bot.message_handler(func=lambda message: message.text == '🛒 New Order')
def new_order(message):
    text = (
        "🛒 *New Order Guide*\n\n"
        "Direct Services lene ke liye niche diye gaye Admin username par contact karein ya Service ID bhejein.\n\n"
        f"👨‍💻 *Admin:* {ADMIN_USERNAME}"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

# --- 4. Support Button ---
@bot.message_handler(func=lambda message: message.text == '📞 Support')
def support_info(message):
    bot.send_message(message.chat.id, f"💬 Kisi bhi help ya enquiry ke liye contact karein:\n👉 {ADMIN_USERNAME}")

# --- Bot Runner ---
if __name__ == '__main__':
    print("Bot Successfully Started!")
    bot.infinity_polling()
