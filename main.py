import os
import telebot
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LEAKCHECK_API_KEY = os.getenv("LEAKCHECK_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 أهلاً بك في بوت فحص التسريبات الأمني.\n\nارسلي البريد الإلكتروني أو رقم الهاتف المراد فحصه.")

@bot.message_handler(func=lambda message: True)
def check_leak(message):
    query = message.text.strip()
    bot.reply_to(message, "🔍 جاري البحث في قواعد البيانات المسربة...")
    
    url = f"https://leakcheck.io{query}?key={LEAKCHECK_API_KEY}"
    
    try:
        response = requests.get(url).json()
        
        if response.get('success') and response.get('result'):
            results = response['result']
            reply_text = f"⚠️ [ Found ! ]\n"
            reply_text += f"[-] Target: {query}\n"
            reply_text += f"[-] Total Breaches: {len(results)}\n\n"
            
            for leak in results[:3]:
                reply_text += f"📍 المصدر: {leak.get('source', 'غير معروف')}\n"
                reply_text += f"🗓️ تاريخ الاختراق: {leak.get('date', 'غير معروف')}\n"
                reply_text += f"🔒 البيانات المسربة: {', '.join(leak.get('fields', []))}\n"
                reply_text += "-------------------------\n"
                
            bot.reply_to(message, reply_text)
        else:
            bot.reply_to(message, "✅ لم يتم العثور على أي تسريبات لهذه البيانات في قاعدة البيانات الحالية.")
            
    except Exception as e:
        bot.reply_to(message, "❌ حدث خطأ أثناء الاتصال بالخادم، تأكد من صلاحية مفتاح API.")

if __name__ == "__main__":
    bot.infinity_polling()
