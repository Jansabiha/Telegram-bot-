import os
import subprocess
import sys
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ⚙️ আপনার মাস্টার বটের টোকেন এখানে দিন
MASTER_BOT_TOKEN = "8170423668:AAFt9yTJZk3gA2wUAV8peI1exzb-pysJ9qs"
master_bot = telebot.TeleBot(MASTER_BOT_TOKEN)

HOSTED_FOLDER = "hosted_bots"
if not os.path.exists(HOSTED_FOLDER):
    os.makedirs(HOSTED_FOLDER)

# রান হওয়া প্রসেসগুলো ট্র্যাক করার জন্য
active_hosted_bots = {}

@master_bot.message_handler(commands=['start'])
def master_start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📂 চলমান বট লিস্ট", callback_data="list_hosted"))
    
    master_bot.send_message(
        message.chat.id,
        "🤖 **Master Bot Hosting Panel-এ স্বাগতম!**\n\n"
        "আপনার যেকোনো পাইথন বট (`.py` ফাইল) সরাসরি এই চ্যাটে ডকুমেন্ট হিসেবে পাঠান। "
        "আমি সেটিকে হোস্টিং এবং ব্যাকগ্রাউন্ডে রান করে দেবো।",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@master_bot.callback_query_handler(func=lambda call: call.data == "list_hosted")
def list_hosted_bots(call):
    master_bot.answer_callback_query(call.id)
    if not active_hosted_bots:
        master_bot.send_message(call.message.chat.id, "⚠️ বর্তমানে কোনো সাব-বট চালু নেই।")
        return
    
    text = "🟢 **হোস্টেড বটসমূহের তালিকা:**\n\n"
    for b_name in active_hosted_bots.keys():
        text += f"- `{b_name}`\n"
    master_bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

# ফাইল আপলোড হ্যান্ডলার (এখানেই আপনার বট হোস্টিং হবে)
@master_bot.message_handler(content_types=['document'])
def handle_hosted_file(message):
    chat_id = message.chat.id
    file_info = master_bot.get_file(message.document.file_id)
    file_name = message.document.file_name

    if not file_name.endswith('.py'):
        master_bot.reply_to(message, "❌ শুধু পাইথন (`.py`) ফাইল আপলোড করুন!")
        return

    downloaded_file = master_bot.download_file(file_info.file_path)
    file_path = os.path.join(HOSTED_FOLDER, file_name)
    
    with open(file_path, 'wb') as f:
        f.write(downloaded_file)

    master_bot.reply_to(message, f"📁 `{file_name}` সফলভাবে আপলোড হয়েছে!\n⚙️ প্রয়োজনীয় লাইব্রেরি চেক ও বট রান করা হচ্ছে...")

    try:
        # সাব-বট চালানোর জন্য প্রয়োজনীয় লাইব্রেরি অটো ইন্সটল করার কমান্ড (যদি কোডে থাকে)
        # পাইথনের নিজস্ব পরিবেশ থেকে সাব-প্রসেস চালু করা
        process = subprocess.Popen([sys.executable, file_path])
        active_hosted_bots[file_name] = process
        
        master_bot.send_message(
            chat_id, 
            f"🚀 **সাফল্য!** আপনার Thanatos সিগন্যাল বট `{file_name}` ব্যাকগ্রাউন্ডে সফলভাবে রান হচ্ছে।"
        )
    except Exception as e:
        master_bot.send_message(chat_id, f"❌ বট রান করতে গিয়ে সমস্যা হয়েছে: {str(e)}")

if __name__ == "__main__":
    print("🎯 Master Hosting Bot চালু হয়েছে...")
    master_bot.infinity_polling()
