import os
import telebot
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "👋 أهلاً بك في بوت التتبع الأمني الشامل المطوّر (OSINT Premier Bot).\n\n"
        "🔍 **كيف يعمل البوت الآن؟**\n"
        "• **عند إرسال بريد أو يوزر:** يولد لك روابط تتبع مباشرة للملفات الشخصية.\n"
        "• **عند إرسال رقم هاتف:** يقوم بفحص قواعد البيانات المفتوحة فوراً، ويستخرج لك المنصات الاجتماعية (تيك توك، سناب، انستقرام... إلخ) المرتبطة بهذا الرقم حقيقياً وحالة أمانه!"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def advanced_osint_tracker(message):
    query = message.text.strip()
    
    # التحقق إذا كانت المدخلات عبارة عن رقم هاتف
    is_phone = query.isdigit() or (query.startswith('+') and query[1:].isdigit())
    
    bot.reply_to(message, "🔍 جاري الفحص الرقمي العميق وتحليل الارتباط بالمنصات الاجتماعية...")
    
    # تنظيف المدخلات للروابط والفلترة
    clean_target = query.replace('+', '').replace('@', '')
    
    # استدعاء خادم الفحص المفتوح
    url = f"https://scylla.sh{query}"
    
    leak_results = []
    social_linked = set() # مصفوفة فريدة لحفظ المنصات المكتشفة حقيقياً
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200 and response.json():
            leak_results = response.json()
            
            # تحليل السجلات المفتوحة ذكياً للبحث عن كلمات دلالية للمواقع المرتبطة بالرقم
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
                elif 'telegram' in source_domain:
                    social_linked.add("✈️ تليجرام (Telegram)")
                elif 'linkedin' in source_domain:
                    social_linked.add("💼 لينكد إن (LinkedIn)")
    except Exception:
        pass

    # بناء رسالة الرد النهائية بشكل منظم جداً
    reply_text = "🔒 **[ نتائج فحص الارتباط والتسريبات ]**\n\n"
    reply_text += f"[-] الهدف المفحوص: `{query}`\n"
    
    if leak_results:
        reply_text += f"⚠️ **[ Found ! ]** تم العثور على سجلات عامة مرتبطة بالهدف.\n"
        reply_text += f"[-] إجمالي السجلات المكشوفة: {len(leak_results)}\n\n"
    else:
        reply_text += "✅ حالة الهدف: لا توجد تسريبات أمنية عامة ومباشرة للرقم حالياً.\n\n"

    # عرض المنصات المرتبطة بالرقم حقيقياً بناءً على فحص السجلات
    reply_text += "📱 **[ التحقق من ارتباط منصات التواصل الاجتماعي ]**\n"
    if is_phone:
        if social_linked:
            reply_text += "⚠️ **الرقم مرتبط ومسجل فعلياً في المنصات التالية:**\n"
            for platform in social_linked:
                reply_text += f" {platform} \n"
        else:
            reply_text += "ℹ️ لم نجد ارتباطاً مباشراً ومكشوفاً في السجلات العامة، إليك روابط التتبع اليدوية المباشرة للفحص الرقمي:\n"
        
        # إضافة روابط الفحص والفتح التلقائي داخل التطبيقات كدعم إضافي
        reply_text += f"\n🔗 **روابط تتبع ومطابقة سريعة بالرقم:**\n"
        reply_text += f"• تيك توك: https://tiktok.com{clean_target}\n"
        reply_text += f"• فيسبوك: https://facebook.com{clean_target}\n"
        reply_text += f"• منصة 𝕏: https://x.com{clean_target}\n"
    else:
        # لوحة التتبع باليوزر نيم في حال لم يكن المدخل رقماً
        reply_text += f"• تيك توك: https://www.tiktok.com/@{clean_target}\n"
        reply_text += f"• سناب شات: https://snapchat.com{clean_target}\n"
        reply_text += f"• انستقرام: https://www.instagram.com/{clean_target}/\n"
        reply_text += f"• تليجرام: https://t.me{clean_target}\n"
        reply_text += f"• يوتيوب: https://youtube.com@{clean_target}\n"

    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == "__main__":
    bot.infinity_polling()
