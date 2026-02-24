# -*- coding: utf-8 -*-

import os
import math
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

# ================= الإحداثيات =================

HARAM = (21.4225, 39.8262)
SAFA = (21.4229, 39.8257)
MARWA = (21.4237, 39.8267)

# ================= القوائم =================

main_menu = ReplyKeyboardMarkup([
    ["الحج", "العمرة"],
    ["الأدعية", "الخريطة"],
    ["ميقات الإحرام"]
], resize_keyboard=True)

map_menu = ReplyKeyboardMarkup([
    ["المسجد الحرام"],
    ["الصفا", "المروة"],
    ["موقعي الحالي"],
    ["رجوع"]
], resize_keyboard=True)

location_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("إرسال موقعي", request_location=True)],
     ["رجوع"]],
    resize_keyboard=True
)

# ================= start =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕋 مرحباً بك في مساعد الحج والعمرة\nاختر من القائمة 👇",
        reply_markup=main_menu
    )

# ================= الحج =================

async def handle_hajj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🕋 مناسك الحج باختصار:

1️⃣ الإحرام  
2️⃣ الوقوف بعرفة  
3️⃣ طواف الإفاضة  
4️⃣ السعي  
5️⃣ رمي الجمرات  
6️⃣ الحلق أو التقصير  
7️⃣ طواف الوداع
"""
    await update.message.reply_text(text)

# ================= العمرة =================

async def handle_umrah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """🌙 خطوات العمرة:

1️⃣ الإحرام من الميقات  
2️⃣ الطواف 7 أشواط  
3️⃣ السعي 7 أشواط  
4️⃣ الحلق أو التقصير
"""
    await update.message.reply_text(text)

# ================= الميقات =================

async def handle_miqat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌍 اكتب اسم بلدك مثل:\nمصر - سوريا - السعودية - أمريكا"
    )

# ================= الخرائط =================

async def send_haram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_location(*HARAM)
    await update.message.reply_text("📍 المسجد الحرام")

async def send_safa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_location(*SAFA)
    await update.message.reply_text("📍 جبل الصفا")

async def send_marwa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_location(*MARWA)
    await update.message.reply_text("📍 جبل المروة")

async def send_current_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.location:
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        dist = distance_m(lat, lon, HARAM[0], HARAM[1])
        await update.message.reply_text(f"📍 موقعك الحالي\nالمسافة من الحرم: {dist} متر")
    else:
        await update.message.reply_text(
            "اضغط زر إرسال موقعي 👇",
            reply_markup=location_keyboard
        )

def distance_m(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return int(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))))

# ================= الرد =================

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "الحج":
        await handle_hajj(update, context)

    elif text == "العمرة":
        await handle_umrah(update, context)

    elif text == "ميقات الإحرام":
        await handle_miqat(update, context)

    elif text == "الخريطة":
        await update.message.reply_text("🗺 اختر:", reply_markup=map_menu)

    elif text == "المسجد الحرام":
        await send_haram(update, context)

    elif text == "الصفا":
        await send_safa(update, context)

    elif text == "المروة":
        await send_marwa(update, context)

    elif text == "موقعي الحالي":
        await send_current_location(update, context)

    elif text == "رجوع":
        await start(update, context)

    else:
        await update.message.reply_text("لم أفهم سؤالك 🤔")

# ================= التشغيل =================

def main():
    if not TOKEN:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN غير موجود")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.LOCATION, reply))

    print("🚀 البوت يعمل...")
    app.run_polling()

if __name__ == "__main__":
    main()
