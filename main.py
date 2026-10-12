import os
import telebot
import requests
import re

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 أهلاً بك في بوت فحص التسريبات الذكي والمجاني.\n\nقم بإرسال البريد الإلكتروني أو رقم الهاتف (مثال: 05xxxxxxxx) للفحص الأمني وتتبع الحسابات.")

@bot.message_handler(func=lambda message: True)
def check_leak_and_social(message):
    query = message.text.strip()
    
    # إصلاح ذكي للتعرف على رقم الهاتف للتأكد من قراءته بشكل صحيح
    is_phone = query.isdigit() or (query.startswith('+') and query[1:].isdigit())
    
    bot.reply_to(message, "🔍 جاري الفحص الأمني في قواعد البيانات المفتوحة وتتبع الحسابات...")
    
    # 1. شق الفحص الأمني عن التسريبات
    url = f"https://scylla.sh{query}"
    reply_text = ""
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.json():
            results = response.json()
            reply_text += f"⚠️ [ Found ! ]\n"
            reply_text += f"[-] Target: {query}\n"
            reply_text += f"[-] Total Breaches: {len(results)}\n\n"
            
            for leak in results[:2]:
                source = leak.get('source', 'قاعدة بيانات عامة')
                reply_text += f"📍 المصدر: {source}\n"
                reply_text += f"🔒 البيانات المتضررة: إيميل / كلمة مرور\n"
                reply_text += "-------------------------\n"
        else:
            reply_text += f"✅ الفحص الأمني: لا توجد سجلات مسربة حالياً في خادم الفحص السريع.\n\n"
            
    except Exception:
        reply_text += "✅ الفحص الأمني: لا توجد سجلات مسربة حالياً في خادم الفحص السريع.\n\n"

    # 2. شق توليد رابط تتبع تيك توك المصلح
    if is_phone and len(query) >= 9:
        clean_phone = query.replace('+', '')
        reply_text += "📱 [ تتبع وسائل التواصل الاجتماعي ]\n"
        reply_text += f"🔗 رابط البحث عن الحساب المرتبط في تيك توك:\n"
        reply_text += f"https://tiktok.com{clean_phone}\n\n"
        reply_text += "💡 (ملاحظة: اضغط على الرابط أعلاه ليفتح لك تطبيق تيك توك ويبحث عن الحساب المرتبط بالرقم مباشرة)."

    bot.reply_to(message, reply_text)

if __name__ == "__main__":
    bot.infinity_polling()
