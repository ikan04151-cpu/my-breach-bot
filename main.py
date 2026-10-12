import os
import telebot
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "👋 أهلاً بك في بوت التحقيق الرقمي المتقدم (Deep Breach Bot).\n\n"
        "🔍 **الأوامر المتاحة للبحث العكسي:**\n"
        "• قم بكتابة الأمر التالي متبوعاً باليوزر نيم لكشف الرقم المرتبط به:\n"
        " `/telegram username` \n\n"
        "• أو أرسل رقماً أو إيميل مباشرة لإجراء فحص شامل للمنصات والصور!"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

# الميزة المطلوبة: فحص يوزر التليجرام وعكسه لاستخراج رقم الهاتف المرتبط
@bot.message_handler(commands=['telegram'])
def handle_telegram_lookup(message):
    try:
        # استخراج اليوزر نيم وتطهيره من المسافات وعلامة @
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "⚠️ يرجى كتابة اليوزر نيم بعد الأمر. مثال:\n`/telegram rayan`", parse_mode="Markdown")
            return
            
        username = args[1].replace('@', '').strip()
        
        # إرسال رسالة جاري جلب البيانات المحاكية للبوت الأصلي
        status_msg = bot.reply_to(message, "📁 Getting data ..")
        
        # الاستعلام من خادم السجلات المفتوحة المتقاطعة
        url = f"https://scylla.sh{username}"
        response = requests.get(url, timeout=10)
        
        phone_number = None
        total_records = 0
        
        if response.status_code == 200 and response.json():
            results = response.json()
            total_records = len(results)
            
            # البحث الذكي داخل السجلات عن أي حقل يحتوي على رقم هاتف مرتبط باليوزر
            for leak in results:
                # محاولة استخراج الحقول التي قد تحتوي على أرقام هواتف مسربة
                phone = leak.get('phone') or leak.get('phone_number') or leak.get('mobile')
                if phone:
                    phone_number = phone
                    break
                
                # فحص باطني داخل نص السجل بالكامل في حال دمج الرقم مع البيانات
                raw_data = str(leak.values())
                phone_match = re.search(r'\b(966|971|20|965)\d{7,10}\b', raw_data)
                if phone_match:
                    phone_number = phone_match.group(0)
                    break
        
        # بناء التقرير النهائي المطابق تماماً للصورة المعروضة
        if phone_number:
            # إضافة علامة الزائد الدولية للرقم إذا لم تكن موجودة
            if not phone_number.startswith('+'):
                phone_number = f"+{phone_number}"
                
            reply_text = (
                f"📂 **All Information Related To**\n"
                f"[ @{username} ]\n\n"
                f"• 💡 **Total Records :** {total_records}\n"
                f"• 📞 **Phone Number :** {phone_number}\n"
                f"• ✈️ **Type :** Telegram"
            )
        else:
            # رد بديل ذكي في حال لم يُكشف الرقم في التسريبات العامة
            reply_text = (
                f"📂 **All Information Related To**\n"
                f"[ @{username} ]\n\n"
                f"• 💡 **Total Records :** 0\n"
                f"• 📞 **Phone Number :** لم يعثر على ارتباط مكشوف حالياً\n"
                f"• ✈️ **Type :** Telegram"
            )
            
        # تحديث الرسالة المؤقتة بالتقرير النهائي المكتمل
        bot.edit_message_text(reply_text, chat_id=message.chat.id, message_id=status_msg.message_id, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, "❌ الخادم مشغول حالياً أو قواعد بيانات العكس قيد التحديث، يرجى المحاولة لاحقاً.")

@bot.message_handler(func=lambda message: True)
def general_osint(message):
    # الحفاظ على ميزات فحص الحسابات والصور السابقة ليعمل البوت كأداة متكاملة
    query = message.text.strip()
    clean_target = query.replace('+', '').replace('@', '')
    is_phone = query.isdigit() or (query.startswith('+') and query[1:].isdigit())
    
    reply_text = "📱 **[ لوحة تتبع وسائل التواصل الاجتماعي ]**\n\n"
    if is_phone:
        base_url = "https://tiktok.com"
        reply_text += f"• تيك توك: {base_url}{clean_target}\n"
        reply_text += f"• فيسبوك: https://facebook.com{clean_target}\n"
    else:
        reply_text += f"• تيك توك: https://tiktok.com@{clean_target}\n"
        reply_text += f"• سناب شات: https://snapchat.com{clean_target}\n"
        reply_text += f"• تليجرام: https://t.me{clean_target}\n"
        
    bot.reply_to(message, reply_text, disable_web_page_preview=True)

if __name__ == "__main__":
    bot.infinity_polling()
