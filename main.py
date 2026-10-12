import os
import telebot
import requests
import re

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def extract_username_from_tiktok(url):
    """دالة ذكية لاستخراج اليوزر نيم الحقيقي من روابط تيك توك بجميع أنواعها"""
    try:
        # إذا كان الرابط قصير (vt.tiktok.com) نقوم بتتبعه لجلب الرابط الأصلي
        if "vt.tiktok.com" in url or "vm.tiktok.com" in url:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            url = response.url
        
        # استخراج اليوزر نيم المسبوق بعلامة @ من الرابط الكامل
        match = re.search(r'@([a-zA-Z0-9_\.]+)', url)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        "👋 أهلاً بك في بوت التتبع الأمني والـ OSINT المتكامل.\n\n"
        "🔍 **القدرات الذكية المتاحة:**\n"
        "• 🔢 **إرسال رقم هاتف:** لفحص التسريبات وتوليد روابط المطابقة.\n"
        "• 👤 **إرسال يوزر نيم:** لتتبع الحساب في المنصات الاجتماعية.\n"
        "• 🔗 **إرسال رابط تيك توك:** سيقوم البوت تلقائياً باستخراج يوزر صاحب الرابط وفحص كافة حساباته الأخرى وتتبعها!"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def advanced_osint_tracker(message):
    query = message.text.strip()
    
    # 1. فحص إذا كان المستخدم قد أرسل رابط تيك توك
    if "tiktok.com" in query:
        bot.reply_to(message, "🔗 تم رصد رابط تيك توك.. جاري فك الرابط واستخراج اسم المستخدم...")
        extracted_user = extract_username_from_tiktok(query)
        if extracted_user:
            query = extracted_user
            bot.reply_to(message, f"👤 تم استخراج اليوزر بنجاح: `@{query}`\nجاري بدء عملية التتبع المتقاطع...")
        else:
            bot.reply_to(message, "❌ لم نتمكن من استخراج اليوزر من الرابط، يرجى إرسال اليوزر نيم مجرداً.")
            return

    # التحقق برمجياً إذا كانت المدخلات رقم هاتف
    is_phone = query.isdigit() or (query.startswith('+') and query[1:].isdigit())
    clean_target = query.replace('+', '').replace('@', '')
    
    # استدعاء خادم الفحص الأمني
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
        reply_text += "✅ حالة الهدف: لا توجد تسريبات أمنية عامة ومباشرة للبيانات حالياً.\n\n"

    reply_text += "📱 **[ التحقق من ارتباط منصات التواصل الاجتماعي ]**\n"
    if is_phone:
        if social_linked:
            reply_text += "⚠️ **الرقم مرتبط ومسجل فعلياً في المنصات التالية:**\n"
            for platform in social_linked:
                reply_text += f" {platform} \n"
        else:
            reply_text += "ℹ️ لم نجد ارتباطاً مكشوفاً في السجلات، إليك روابط المطابقة الرقمية:\n"
        
        base_url = "https://tiktok.com"
        reply_text += f"\n🔗 **روابط تتبع سريعة بالرقم:**\n"
        reply_text += f"• تيك توك: {base_url}{clean_target}\n"
        reply_text += f"• فيسبوك: https://facebook.com{clean_target}\n"
        reply_text += f"• منصة 𝕏: https://x.com{clean_target}\n"
    else:
        # اللوحة النظيفة عند إرسال يوزر نيم أو استخراجه من رابط تيك توك
        reply_text += f"• تيك توك: https://www.tiktok.com/@{clean_target}\n"
        reply_text += f"• سناب شات: https://snapchat.com{clean_target}\n"
        reply_text += f"• انستقرام: https://instagram.com{clean_target}/\n"
        reply_text += f"• تليجرام: https://t.me{clean_target}\n"

    bot.reply_to(message, reply_text, parse_mode="Markdown", disable_web_page_preview=True)

if __name__ == "__main__":
    bot.infinity_polling()
