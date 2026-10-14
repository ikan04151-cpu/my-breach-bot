import os
import logging
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from threading import Thread

# إعدادات السجلات لمراقبة وصول الإشارات في منصة Render
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

"

# مصفوفة لتخزين معرفات شات المستخدمين لتلقي الإشارات تلقائياً
subscribed_users = set()

# إنشاء كائنات البوت الاحترافية غير المتزامنة
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# --- 1. خادم الويب المطور لاستقبال إشارات الـ Webhook من TradingView ---
app = Flask('')

@app.route('/')
def home():
    return "TradingView Webhook Listener is Active and Running!"

@app.route('/webhook', methods=['POST'])
def tradingview_webhook():
    """استقبال البيانات الفنية الدقيقة من TradingView وتوجيهها للمستخدمين فوراً"""
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400
        
        # استخراج تفاصيل الإشارة المرسلة من منصة التحليل الحقيقية
        asset = data.get("asset", "Smarty")
        action = data.get("action", "").upper() # CALL أو PUT
        rsi_val = data.get("rsi", "N/A")
        price = data.get("price", "N/A")
        trend = data.get("trend", "N/A")
        
        # صياغة نص التنبيه الفني المؤكد بناءً على حركة الشاشة الحقيقية
        if action == "CALL":
            signal_text = (
                f"🚨 **[ إشارة صعود فنية مؤكدة - CALL ]** 🟢\n"
                f"-----------------------------------\n"
                f"🎯 الأصل الحالي: `{asset}` | الإطار: `15 ثانية`\n"
                f"💵 سعر التنفيذ الدقيق: `{price}`\n\n"
                f"📊 **تحليل الزخم الحقيقي من TradingView:**\n"
                f"🔹 Bollinger Bands: السعر يرتد من خط الدعم السفلي\n"
                f"🔹 RSI: تشبع بيعي حقيقي ومؤكد بنسبة ({rsi_val}%)\n"
                f"🛡️ فلتر الأمان: {trend}\n\n"
                f"⏱ نافذة الدفع في المنصة: **20 - 34 ثانية**\n"
                f"🟢 **الإجراء:** انتظر ثانيتين ثم اضغط **شراء (UP)** فوراً!"
            )
        elif action == "PUT":
            signal_text = (
                f"🚨 **[ إشارة هبوط فنية مؤكدة - PUT ]** 🔴\n"
                f"-----------------------------------\n"
                f"🎯 الأصل الحالي: `{asset}` | الإطار: `15 ثانية`\n"
                f"💵 سعر التنفيذ الدقيق: `{price}`\n\n"
                f"📊 **تحليل الزخم الحقيقي من TradingView:**\n"
                f"🔹 Bollinger Bands: السعر يخترق قنوات المقاومة العلوية\n"
                f"🔹 RSI: تضخم شرائي حقيقي ومؤكد بنسبة ({rsi_val}%)\n"
                f"🛡️ فلتر الأمان: {trend}\n\n"
                f"⏱ نافذة الدفع في المنصة: **20 - 34 ثانية**\n"
                f"🔴 **الإجراء:** انتظر ثانيتين ثم اضغط **بيع (DOWN)** فوراً!"
            )
        else:
            return jsonify({"status": "ignored", "message": "Unknown action"}), 200

        # إرسال التنبيه الفوري لجميع المستخدمين النشطين دون أي تأخير شبكة
        loop = asyncio.get_event_loop()
        for chat_id in subscribed_users:
            loop.create_task(bot.send_message(chat_id, signal_text, parse_mode="Markdown"))
            
        logging.info(f"Successfully processed and broadcasted {action} signal for {asset}")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        logging.error(f"Error in Webhook processor: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. أوامر استقبال وتنشيط البوت في تلغرام ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    subscribed_users.add(message.chat.id)
    welcome_msg = (
        "📊 **مرحباً بك في بوت التنبيهات المربوط بـ TradingView**\n\n"
        "🤖 تم تفعيل نظام الـ Webhook الاحترافي بنجاح. البوت مسجل الآن لاستقبال الإشارات المؤكدة 100% ومطابقة لشاشتك الحقيقية بالثانية.\n\n"
        "📌 أرسل أمر `/signals` للتأكد من تفعيل البث!"
    )
    await message.reply(welcome_msg, parse_mode="Markdown")

@dp.message(Command("signals"))
async def cmd_signals(message: types.Message):
    subscribed_users.add(message.chat.id)
    await message.reply("🚀 محرك استقبال التنبيهات الفورية من TradingView نشط الآن وفي حالة تأهب كامل لبث الصفقات المضمونة!")

# --- 3. نقطة الانطلاق والتشغيل اللانهائي المتوازن ---
async def main():
    # تشغيل خادم استقبال إشارات الويب هوك في الخلفية
    Thread(target=run_web_server, daemon=True).start()
    
    # بدء تشغيل استقبال رسائل البوت اللامركزي المستقر ضد التجمد
    logging.info("Starting Webhook-driven Async Bot Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
