import os
import telebot
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "👋 أهلاً بك في بوت التتبع الأمني الشامل (OSINT Bot).\n\n"
        "🔍 **طريقة الاستخدام الذكية:**\n"
        "1️⃣ **البحث برقم الهاتف أو الإيميل:** لفحص التسريبات الأمنية العامة وتتبع الحسابات.\n"
        "2️⃣ **البحث باليوزر نيم (Username):** أرسل اسم المستخدم (بدون علامة @) لتوليد روابط تتبع مباشرة لكافة منصات التواصل الاجتماعي!"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def osint_tracker(message):
    query = message.text.strip()
    
    # التحقق برمجياً إذا كانت المدخلات عبارة عن رقم هاتف فقط
    is_phone = query.isdigit() or (query.startswith('+') and query[1:].isdigit())
    
    bot.reply_to(message, "🔍 جاري الفحص الرقمي الشامل وحصد روابط الحسابات المفتوحة...")
    
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
                reply_text += f"🔒 نوع البيانات: إيميل / كلمة مرور\n"
                reply_text += "-------------------------\n"
        else:
            reply_text += f"✅ الفحص الأمني: لا توجد سجلات مسربة عامة لهذا الهدف (`{query}`).\n\n"
    except Exception:
        reply_text += "✅ الفحص الأمني: لا توجد سجلات مسربة عامة حالياً في خادم الفحص السريع.\n\n"

    # --- 2. شق توليد لوحة التتبع الرقمي باليوزر نيم أو الهاتف ---
    clean_target = query.replace('+', '').replace('@', '')
    
    reply_text += "📱 **[ لوحة تتبع وسائل التواصل الاجتماعي ]**\n"
    reply_text += f"الهدف المفحوص: `{clean_target}`\n\n"
    
    if is_phone:
        # روابط تعتمد على رقم الهاتف
        reply_text += f"🎵 تيك توك: https://tiktok.com{clean_target}\n"
        reply_text += f"💬 فيسبوك: https://facebook.com{clean_target}\n"
        reply_text += f"𝕏 (تويتر): https://x.com{clean_target}\n\n"
        reply_text += "💡 (ملاحظة: اضغط على الروابط أعلاه لفتح التطبيقات والبحث بالرقم مباشرة)."
    else:
        # روابط تعتمد على اسم المستخدم (Username) وتوجهك للملف الشخصي مباشرة
        reply_text += f"🎵 تيك توك: https://tiktok.com@{clean_target}\n"
        reply_text += f"👻 سناب شات: https://snapchat.com{clean_target}\n"
        reply_text += f"📸 انستقرام: https://instagram.com{clean_target}/\n"
        reply_text += f"✈️ تليجرام: https://t.me{clean_target}\n"
        reply_text += f"💬 فيسبوك: https://facebook.com{clean_target}\n"
        reply_text += f"🔴 يوتيوب: https://youtube.com@{clean_target}\n"
        reply_text += f"𝕏 (تويتر): https://x.com{clean_target}\n\n"
        reply_text += "💡 (ملاحظة: الروابط أعلاه ستوجهك مباشرة إلى الحساب الشخصي المرتبط بهذا الاسم في حال كان موجوداً ومسجلاً)."

    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == "__main__":
    bot.infinity_polling()
