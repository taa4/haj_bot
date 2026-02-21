# -*- coding: utf-8 -*-
import os
import sys
import math
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# إعداد logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# تحميل التوكن
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# إحداثيات الأماكن المقدسة
HARAM = (21.4225, 39.8262)
SAFA = (21.4229, 39.8257)
MARWA = (21.4237, 39.8267)

# ================= القوائم =================
main_menu = [
    ["الحج", "العمرة"],
    ["الأدعية", "الخريطة"],
    ["الأخطاء والكفارات", "ميقات الإحرام"]
]

dua_menu = [
    ["أدعية الإحرام", "أدعية الطواف"],
    ["أدعية السعي", "أدعية عرفة"],
    ["أدعية الجمرات", "أدعية عامة"],
    ["رجوع"]
]

mistakes_menu = [
    ["لبس المخيط", "التطيب بعد الإحرام"],
    ["قص الشعر أو الأظافر", "تغطية الرأس"],
    ["الطواف بدون وضوء", "نسي شوط"],
    ["السعي قبل الطواف", "ترك واجب"],
    ["الجماع"],
    ["رجوع"]
]

map_menu = [
    ["المسجد الحرام"],
    ["الصفا", "المروة"],
    ["موقعي الحالي"],
    ["رجوع"]
]

miqat_menu = [
    ["الشام (سوريا، لبنان، الأردن، فلسطين)"],
    ["مصر وشمال أفريقيا"],
    ["اليمن"],
    ["رجوع"]
]

back_menu = [["رجوع للقائمة الرئيسية"]]

# إنشاء لوحات المفاتيح
markup_main = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
markup_dua = ReplyKeyboardMarkup(dua_menu, resize_keyboard=True)
markup_mistakes = ReplyKeyboardMarkup(mistakes_menu, resize_keyboard=True)
markup_map = ReplyKeyboardMarkup(map_menu, resize_keyboard=True)
markup_miqat = ReplyKeyboardMarkup(miqat_menu, resize_keyboard=True)
markup_back = ReplyKeyboardMarkup(back_menu, resize_keyboard=True)

# زر مشاركة الموقع
location_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("إرسال موقعي", request_location=True)],
     ["رجوع"]],
    resize_keyboard=True
)

# ================= دوال المساعدة =================

def normalize_text(text):
    """تقنين النص وإزالة التشكيل"""
    text = text.strip().lower()
    replacements = {
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ة': 'ه', 'ى': 'ي',
        'ؤ': 'و', 'ئ': 'ي', 'ّ': '', 'َ': '', 'ُ': '', 'ِ': '',
        'ْ': '', 'ً': '', 'ٌ': '', 'ٍ': '',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def calculate_distance(lat1, lon1, lat2, lon2):
    """حساب المسافة بين نقطتين"""
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return int(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))))


def process_text(text):
    """معالجة النص وفهم القصد"""
    text_norm = normalize_text(text)
    
    # الميقات
    if any(word in text_norm for word in ['ميقات', 'احرام', 'احرم']):
        if any(word in text_norm for word in ['شام', 'سور', 'لبن', 'فلسطين', 'اردن']):
            return "miqat_sham"
        elif any(word in text_norm for word in ['مصر', 'مغرب', 'جزائر', 'تونس', 'ليبيا']):
            return "miqat_egypt"
        elif any(word in text_norm for word in ['يمن', 'عدن', 'صنعاء']):
            return "miqat_yemen"
        else:
            return "miqat_menu"
    
    # الحج والعمرة
    if 'حج' in text_norm:
        return "hajj"
    if 'عمر' in text_norm:
        return "umrah"
    
    # الأدعية
    if 'ادع' in text_norm or 'دعاء' in text_norm:
        if 'احرام' in text_norm:
            return "dua_ihram"
        if 'طواف' in text_norm:
            return "dua_tawaf"
        if 'سعي' in text_norm:
            return "dua_saee"
        if 'عرفه' in text_norm or 'عرفة' in text_norm:
            return "dua_arafah"
        if 'جمرات' in text_norm:
            return "dua_jamarat"
        return "dua_menu"
    
    # الأخطاء
    if any(word in text_norm for word in ['خطأ', 'غلط', 'كفارة']):
        return "mistakes_menu"
    
    # الخريطة
    if any(word in text_norm for word in ['خريطة', 'موقع', 'مكان']):
        if 'حرام' in text_norm:
            return "map_haram"
        if 'صفا' in text_norm:
            return "map_safa"
        if 'مروة' in text_norm:
            return "map_marwa"
        return "map_menu"
    
    # الرجوع
    if 'رجوع' in text_norm or 'عودة' in text_norm:
        return "back"
    
    return "unknown"

# ================= وظائف الحج والعمرة =================

async def handle_hajj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = """**مناسك الحج خطوة بخطوة:**

📅 **اليوم 8 (التروية):** الإحرام والمبيت في منى

📅 **اليوم 9 (عرفة):**
🌅 الصباح: الذهاب إلى عرفة
☀️ الظهر: الوقوف والدعاء حتى الغروب
🌇 المساء: التوجه إلى مزدلفة

📅 **اليوم 10 (النحر):**
🌄 الفجر: الصلاة في مزدلفة وجمع الحصى
🌞 الصباح: رمي جمرة العقبة → الحلق → الذبح → الطواف

**أيام التشريق (11-13):**
📅 رمي الجمرات الثلاث → المبيت في منى

**أخيراً:** طواف الوداع عند المغادرة"""
    await update.message.reply_text(response, reply_markup=markup_back, parse_mode='Markdown')


async def handle_umrah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = """**خطوات العمرة:**

1️⃣ **الإحرام من الميقات**
   - النية: "اللهم إني أريد العمرة"
   - التلبية: "لبيك اللهم عمرة"

2️⃣ **الطواف حول الكعبة (7 أشواط)**

3️⃣ **صلاة ركعتين خلف مقام إبراهيم**

4️⃣ **السعي بين الصفا والمروة (7 أشواط)**

5️⃣ **الحلق أو التقصير**
   - الرجال: الحلق أفضل
   - النساء: تقصير قدر أنملة"""
    await update.message.reply_text(response, reply_markup=markup_back, parse_mode='Markdown')

# ================= وظائف الأدعية =================

async def duas_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("**📿 اختر نوع الدعاء:**", reply_markup=markup_dua, parse_mode='Markdown')


async def dua_ihram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """**أدعية الإحرام:**

📿 *النية:* اللهم إني نويت العمرة/الحج فيسره لي وتقبله مني.

📿 *التلبية:* لبيك اللهم لبيك، لبيك لا شريك لك لبيك، إن الحمد والنعمة لك والملك، لا شريك لك."""
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_tawaf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """**أدعية الطواف:**

📿 *في بداية كل شوط:* بسم الله والله أكبر

📿 *دعاء:* ربنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار."""
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_saee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """**أدعية السعي:**

📿 *عند الصفا:* إِنَّ الصَّفَا وَالْمَرْوَةَ مِن شَعَائِرِ اللَّهِ

📿 *أثناء السعي:* رب اغفر وارحم وتجاوز عما تعلم.

📿 *عند المروة:* اللهم اجعلني من المقبولين."""
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_arafah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """**أدعية يوم عرفة:**

📿 *أفضل الدعاء:* لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.

📿 *دعاء:* اللهم اغفر لي ولوالدي وللمؤمنين والمؤمنات."""
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_jamarat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """**أدعية رمي الجمرات:**

📿 *عند كل حصاة:* الله أكبر، رغماً للشيطان وحزبه.

📿 *بعد الرمي:* اللهم اجعله حجاً مبروراً وسعياً مشكوراً."""
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_general(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """**أدعية عامة:**

📿 *لتيسير الأمور:* رب اشرح لي صدري ويسر لي أمري.

📿 *لحسن الخاتمة:* اللهم حسن الخاتمة.

📿 *اللهم ارزقني حجاً مبروراً وسعياً مشكوراً."""
    await update.message.reply_text(text, parse_mode='Markdown')

# ================= وظائف الأخطاء =================

async def mistakes_menu_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("**⚠️ اختر الخطأ:**", reply_markup=markup_mistakes, parse_mode='Markdown')


async def mistake_detail(update: Update, text: str):
    await update.message.reply_text(text, parse_mode='Markdown')

# ================= وظائف الخرائط =================

async def map_menu_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("**🗺️ اختر الموقع:**", reply_markup=markup_map, parse_mode='Markdown')


async def send_haram_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_location(latitude=21.4225, longitude=39.8262)
    await update.message.reply_text(
        "**المسجد الحرام**\nمكة المكرمة\n\n• الكعبة المشرفة\n• الحجر الأسود\n• مقام إبراهيم",
        parse_mode='Markdown'
    )


async def send_safa_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_location(latitude=21.4229, longitude=39.8257)
    await update.message.reply_text(
        "**جبل الصفا**\nبداية السعي\n\nإِنَّ الصَّفَا وَالْمَرْوَةَ مِن شَعَائِرِ اللَّهِ",
        parse_mode='Markdown'
    )


async def send_marwah_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_location(latitude=21.4237, longitude=39.8267)
    await update.message.reply_text(
        "**جبل المروة**\nنهاية السعي",
        parse_mode='Markdown'
    )

# ================= وظائف الميقات =================

async def miqat_sham(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """**🕋 ميقات بلاد الشام**
(سوريا، لبنان، الأردن، فلسطين)

📍 **الميقات:** ذو الحليفة (أبيار علي)
📏 **المسافة:** 450 كم من مكة

**الإجراءات:**
• النية قبل الوصول للميقات
• لبس الإحرام في السيارة أو الطائرة"""
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=24.9167, longitude=39.6167)


async def miqat_egypt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """**🕋 ميقات مصر وشمال أفريقيا**
(مصر، ليبيا، تونس، الجزائر، المغرب، السودان)

📍 **الميقات:** الجحفة (رابغ)
📏 **المسافة:** 180 كم شمال غرب مكة

**✈️ للحجاج الجويين:**
• تحرم في الطائرة قبل الهبوط"""
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=26.3294, longitude=35.3123)


async def miqat_yemen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """**🕋 ميقات اليمن**
(اليمن، حضرموت)

📍 **الميقات:** يَلَمْلم
📏 **المسافة:** 100 كم شرق مكة

**✈️ للحجاج الجويين:**
• إذا هبطت في جدة: تحرم في المطار"""
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=21.4167, longitude=40.6000)

# ================= دالة start =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """🌙 *مرحبا بك في مساعد الحج والعمرة* 🤲

*للاستعلام عن الميقات، اكتب اسم بلدك:*
• "مصر" أو "سوريا" أو "اليمن"

*أو اختر من القائمة:* 👇"""
    await update.message.reply_text(welcome_text, reply_markup=markup_main, parse_mode='Markdown')


async def send_current_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يرسل موقع المستخدم الحالي"""
    if update.message.location:
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        dist_haram = calculate_distance(lat, lon, 21.4225, 39.8262)
        await update.message.reply_location(latitude=lat, longitude=lon)
        await update.message.reply_text(
            f"**موقعك الحالي:**\n📍 {lat:.4f}, {lon:.4f}\n\n📏 **المسافة من الحرم:** {dist_haram:,} متر",
            reply_markup=markup_main,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "📍 اضغط على زر 'إرسال موقعي'",
            reply_markup=location_keyboard,
            parse_mode='Markdown'
        )

# ================= المعالج الرئيسي =================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة جميع الرسائل النصية"""
    text = update.message.text.strip()
    
    # أزرار الرجوع
    if text in ["رجوع", "رجوع للقائمة الرئيسية"]:
        await start(update, context)
        return
    
    # القائمة الرئيسية
    if text == "الحج":
        await handle_hajj(update, context)
    elif text == "العمرة":
        await handle_umrah(update, context)
    elif text == "الأدعية":
        await duas_menu(update, context)
    elif text == "الخريطة":
        await map_menu_show(update, context)
    elif text == "الأخطاء والكفارات":
        await mistakes_menu_show(update, context)
    elif text == "ميقات الإحرام":
        await update.message.reply_text("**🌍 اختر منطقتك:**", reply_markup=markup_miqat, parse_mode='Markdown')
    
    # أزرار الأدعية
    elif text == "أدعية الإحرام":
        await dua_ihram(update, context)
    elif text == "أدعية الطواف":
        await dua_tawaf(update, context)
    elif text == "أدعية السعي":
        await dua_saee(update, context)
    elif text == "أدعية عرفة":
        await dua_arafah(update, context)
    elif text == "أدعية الجمرات":
        await dua_jamarat(update, context)
    elif text == "أدعية عامة":
        await dua_general(update, context)
    
    # أزرار الخريطة
    elif text == "المسجد الحرام":
        await send_haram_location(update, context)
    elif text == "الصفا":
        await send_safa_location(update, context)
    elif text == "المروة":
        await send_marwah_location(update, context)
    elif text == "موقعي الحالي":
        await send_current_location(update, context)
    
    # أزرار الأخطاء
    elif text == "لبس المخيط":
        await mistake_detail(update, "**👕 لبس المخيط**\n❌ محظور\n💰 الكفارة: فدية أذى (شاة أو إطعام 6 مساكين أو صيام 3 أيام)")
    elif text == "التطيب بعد الإحرام":
        await mistake_detail(update, "**🌹 التطيب بعد الإحرام**\n❌ محظور\n💰 الكفارة: فدية أذى")
    elif text == "قص الشعر أو الأظافر":
        await mistake_detail(update, "**✂️ قص الشعر أو الأظافر**\n❌ محظور\n💰 الكفارة: فدية أذى")
    elif text == "تغطية الرأس":
        await mistake_detail(update, "**🧢 تغطية الرأس (للرجل)**\n❌ محظور\n💰 الكفارة: فدية أذى")
    elif text == "الطواف بدون وضوء":
        await mistake_detail(update, "**💧 الطواف بدون وضوء**\n❌ الطواف غير صحيح\n📌 يجب إعادة الطواف")
    elif text == "نسي شوط":
        await mistake_detail(update, "**🔄 نسي شوط**\n📌 إن تذكرت قريباً أكمل، وإلا أعد الطواف")
    elif text == "السعي قبل الطواف":
        await mistake_detail(update, "**🚶 السعي قبل الطواف**\n❌ السعي غير صحيح\n📌 أعد السعي بعد الطواف")
    elif text == "ترك واجب":
        await mistake_detail(update, "**⚠️ ترك واجب**\n💰 الكفارة: دم (ذبح شاة)")
    elif text == "الجماع":
        await mistake_detail(update, "**💔 الجماع قبل التحلل**\n❌ يفسد الحج\n📌 يجب: إكمال الحج + القضاء + بدنة")
    
    # أزرار الميقات
    elif text == "الشام (سوريا، لبنان، الأردن، فلسطين)":
        await miqat_sham(update, context)
    elif text == "مصر وشمال أفريقيا":
        await miqat_egypt(update, context)
    elif text == "اليمن":
        await miqat_yemen(update, context)
    
    # معالجة النصوص الذكية
    else:
        intent = process_text(text)
        if intent == "hajj":
            await handle_hajj(update, context)
        elif intent == "umrah":
            await handle_umrah(update, context)
        elif intent == "dua_menu":
            await duas_menu(update, context)
        elif intent == "dua_ihram":
            await dua_ihram(update, context)
        elif intent == "dua_tawaf":
            await dua_tawaf(update, context)
        elif intent == "dua_saee":
            await dua_saee(update, context)
        elif intent == "dua_arafah":
            await dua_arafah(update, context)
        elif intent == "dua_jamarat":
            await dua_jamarat(update, context)
        elif intent == "mistakes_menu":
            await mistakes_menu_show(update, context)
        elif intent == "map_menu":
            await map_menu_show(update, context)
        elif intent == "map_haram":
            await send_haram_location(update, context)
        elif intent == "map_safa":
            await send_safa_location(update, context)
        elif intent == "map_marwa":
            await send_marwah_location(update, context)
        elif intent == "miqat_sham":
            await miqat_sham(update, context)
        elif intent == "miqat_egypt":
            await miqat_egypt(update, context)
        elif intent == "miqat_yemen":
            await miqat_yemen(update, context)
        elif intent == "miqat_menu":
            await update.message.reply_text("**🌍 اختر منطقتك:**", reply_markup=markup_miqat, parse_mode='Markdown')
        elif intent == "back":
            await start(update, context)
        else:
            await update.message.reply_text(
                "🤔 لم أفهم.\nاكتب اسم بلدك أو اختر من القائمة 👇",
                reply_markup=markup_main,
                parse_mode='Markdown'
            )

# ================= معالج الموقع =================

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_current_location(update, context)

# ================= الدالة الرئيسية =================

def main():
    """تشغيل البوت"""
    print(f"🚀 بدء تشغيل البوت...")
    print(f"📱 التوكن: {TOKEN[:5]}...{TOKEN[-5:] if TOKEN else 'غير موجود'}")
    
    if not TOKEN:
        print("❌ خطأ: التوكن غير موجود!")
        return
    
    # بناء التطبيق
    app = Application.builder().token(TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    
    print("✅ البوت جاهز للتشغيل...")
    
    # تشغيل البوت
    app.run_polling()

if __name__ == "__main__":
    main()
