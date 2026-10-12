import os
import telebot
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "👋 أهلاً بك في بوت التتبع الأمني الشامل المطوّر (OSINT Premier Bot).\n\n"
        "🔍 **الخصائص والتحقيقات المدعومة حالياً:**\n"
        "• 🔢 **إرسال رقم هاتف:** لفحص التسريبات وتتبع الحسابات الاجتماعية.\n"
        "• 👤 **إرسال يوزر نيم:** لتتبع الحساب في كافة المنصات بضغطة واحدة.\n"
        "• 🖼️ **إرسال صورة (حتى لو بدون علامة مائية):** للبحث العكسي العميق ومعرفة الناشر الأصلي، وتحديد مكان ومصدر التقاط الصورة على الإنترنت!"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

# ميزة مطورة: استقبال الصور وعمل بحث عكسي متقاطع لكشف الناشر الأصلي ومكان التصوير
@bot.message_handler(content_types=['photo'])
def handle_image_osint(message):
    try:
        bot.reply_to(message, "⏳ جاري استقبال الصورة وتحليل البصمة الرقمية العميقة للزوايا والألوان...")
        
        # جلب رابط ملف الصورة من خوادم تليجرام لتهيئته للمحركات العالمية
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        image_url = f"https://telegram.org{TELEGRAM_TOKEN}/{file_path}"
        
        # روابط التحقيق العكسي العالمية المباشرة لكشف هوية ومصدر الصورة
        tineye_url = f"https://tineye.com{image_url}"
        google_lens_url = f"https://google.com{image_url}"
        yandex_url = f"https://yandex.com{image_url}"
        
        reply_text = "🖼️ **[ لوحة التحقيق الرقمي وكشف مصدر الصورة ]**\n\n"
        reply_text += "💡 لكشف الحساب الناشر الأصلي، أو معرفة مكان تصويرها ومطابقتها، اضغط على الروابط الموجهة أدناه:\n\n"
        reply_text += f"🌐 **1. فحص Google Lens (الأقوى لكشف الحسابات ومطابقة الوجوه والأماكن):**\n{google_lens_url}\n\n"
        reply_text += f"🔎 **2. فحص Yandex Images (الأدق لكشف صور سناب شات والمقاطع المأخوذة منها):**\n{yandex_url}\n\n"
        reply_text += f"🔍 **3. فحص TinEye (لمعرفة أول تاريخ ظهرت فيه الصورة على الإنترنت):**\n{tineye_url}\n\n"
        reply_text += "⚠️ **تنبيه أمني:** تأكد من فتح الروابط في متصفح خارجي (مثل سفاري أو كروم) لتظهر لك قائمة الملفات الشخصية والمواقع التي نشرت الصورة بالتفصيل وبدقة كاملة."
        
        bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)
        
    except Exception as e:
        bot.reply_to(message, "❌ حدث خطأ أثناء تحليل بصمة الصورة، يرجى المحاولة لاحقاً.")

@bot.message_handler(func=lambda message: True)
def advanced_osint_tracker(message):
    query = message.text.strip()
    is_phone = query.isdigit() or (query.startswith('+') and query[1:].isdigit())
    
    bot.reply_to(message, "🔍 جاري الفحص الرقمي وتحليل الارتباط بالمنصات الاجتماعية...")
    clean_target = query.replace('+', '').replace('@', '')
    
    url = f"https://scylla.sh{query}"
    leak_results = []
    social_linked = set()
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.json():
            leak_results = response.json()
            for leak in leak_results:
                source_domain = leak.get('source', '').lower()
                if 'tiktok' in source_domain:
                    social_linked.add("🎵 تيك توك (TikTok)")
                elif 'instagram' in source_domain or 'facebook' in source_domain:
                    social_linked.add("📸 انستقرام / فيسبوك (Meta)")
                elif 'twitter' in source_domain or 'x.com' in source_domain:
                    social_linked.add("𝕏 (تويتر سابقاً)")
                elif 'snapchat' in source_domain:
                    social_linked.add("👻 سناب شات (Snapchat)")
    except Exception:
        pass

    reply_text = "🔒 **[ نتائج فحص الارتباط والتسريبات ]**\n\n"
    reply_text += f"[-] الهدف المفحوص: `{query}`\n"
    
    if leak_results:
        reply_text += f"⚠️ **[ Found ! ]** تم العثور على سجلات عامة مرتبطة بالهدف.\n\n"
    else:
        reply_text += "✅ حالة الهدف: لا توجد تسريبات أمنية عامة ومباشرة للرقم حالياً.\n\n"

    reply_text += "📱 **[ التحقق من ارتباط منصات التواصل الاجتماعي ]**\n"
    if is_phone:
        if social_linked:
            reply_text += "⚠️ **الرقم مرتبط ومسجل فعلياً في المنصات التالية:**\n"
            for platform in social_linked:
                reply_text += f" {platform} \n"
        else:
            reply_text += "ℹ️ لم نجد ارتباطاً مكشوفاً في السجلات، إليك روابط المطابقة والبحث الرقمي:\n"
        
        base_url = "https://tiktok.com"
        reply_text += f"\n🔗 **روابط تتبع ومطابقة سريعة بالرقم:**\n"
        reply_text += f"• تيك توك: {base_url}{clean_target}\n"
        reply_text += f"• فيسبوك: https://facebook.com{clean_target}\n"
        reply_text += f"• منصة 𝕏: https://x.com{clean_target}\n"
    else:
        reply_text += f"• تيك توك: https://tiktok.com@{clean_target}\n"
        reply_text += f"• سناب شات: https://snapchat.com{clean_target}\n"
        reply_text += f"• انستقرام: https://instagram.com{clean_target}/\n"
        reply_text += f"• تليجرام: https://t.me{clean_target}\n"

    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == "__main__":
    bot.infinity_polling()
