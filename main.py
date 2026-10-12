import os
import telebot
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "👋 أهلاً بك في بوت التتبع الأمني الذكي (OSINT Bot).\n\n"
        "🔍 **ماذا يمكنك أن تفعل هنا؟**\n"
        "1️⃣ أرسل بريد إلكتروني أو رقم هاتف لفحصه أمنياً من التسريبات.\n"
        "2️⃣ أرسل رقم هاتف أو اسم مستخدم (Username) لتتبع حساباته في وسائل التواصل الاجتماعي تلقائياً."
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def osint_tracker(message):
    query = message.text.strip()
    
    # التحقق برمجياً من نوع المدخلات (رقم هاتف أو اسم/إيميل)
    is_phone = query.isdigit() or (query.startswith('+') and query[1:].isdigit())
    
    bot.reply_to(message, "🔍 جاري بدء عملية الفحص الأمني الرقمي (OSINT) وحصد السجلات المفتوحة...")
    
    # --- 1. شق فحص التسريبات الأمنية العامة ---
    url = f"https://scylla.sh{query}"
    reply_text = "🔒 **[ نتائج الفحص الأمني ]**\n"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.json():
            results = response.json()
            reply_text += f"⚠️ **[ Found ! ]** تم العثور على سجلات مسربة.\n"
            reply_text += f"[-] الهدف: `{query}`\n"
            reply_text += f"[-] إجمالي التسريبات: {len(results)}\n\n"
            
            for leak in results[:2]:
                source = leak.get('source', 'قاعدة بيانات عامة')
                reply_text += f"📍 المصدر: {source}\n"
                reply_text += f"🔒 نوع البيانات المتضررة: إيميل / كلمة مرور\n"
                reply_text += "-------------------------\n"
        else:
            reply_text += f"✅ الفحص الأمني: لا توجد سجلات مسربة عامة حالياً لهذا الهدف (`{query}`).\n\n"
    except Exception:
        reply_text += "✅ الفحص الأمني: الهدف آمن أو قواعد بيانات الفحص السريع قيد التحديث حالياً.\n\n"

    # --- 2. شق توليد لوحة التتبع الرقمي (OSINT Social Media Tracker) ---
    clean_target = query.replace('+', '').replace('@', '')
    
    reply_text += "📱 **[ لوحة تتبع وسائل التواصل الاجتماعي ]**\n"
    reply_text += f"Target Name/Phone: `{clean_target}`\n\n"
    
    if is_phone:
        # روابط تعتمد على رقم الهاتف
        reply_text += f"🎵 تيك توك: https://tiktok.com{clean_target}\n"
        reply_text += f"💬 فيسبوك: https://facebook.com{clean_target}\n"
        reply_text += f"𝕏 (تويتر): https://x.com{clean_target}\n\n"
        reply_text += "💡 (ملاحظة: اضغط على الروابط أعلاه لفتح التطبيقات والبحث بالرقم مباشرة)."
    else:
        # روابط تعتمد على اسم المستخدم (Username) في حال لم يكن المدخل رقماً
        reply_text += f"🎵 تيك توك: https://tiktok.com@{clean_target}\n"
        reply_text += f"📸 انستقرام: https://instagram.com{clean_target}/\n"
        reply_text += f"👻 سناب شات: https://snapchat.com{clean_target}\n"
        reply_text += f"𝕏 (تويتر): https://x.com{clean_target}\n"
        reply_text += f"💬 فيسبوك: https://facebook.com{clean_target}\n\n"
        reply_text += "💡 (ملاحظة: إذا أرسلت اسم مستخدم، الروابط أعلاه ستوجهك مباشرة للملف الشخصي للهدف في حال كان الحساب موجوداً بنفس الاسم)."

    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == "__main__":
    bot.infinity_polling()
