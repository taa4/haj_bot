# -*- coding: utf-8 -*-
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import math
import os
import sys
from dotenv import load_dotenv

# تحميل التوكن من ملف .env
load_dotenv()
# إصلاح مشكلة الترميز
sys.stdout.reconfigure(encoding='utf-8')
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

HARAM = (21.4225, 39.8262)
SAFA = (21.4229, 39.8257)
MARWA = (21.4237, 39.8267)

# ================= القوائم (مرة واحدة فقط) =================
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
    """تقنين النص وإزالة التشكيل والحركات"""
    text = text.strip().lower()

    # استبدال الأحلام المشابهة
    replacements = {
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا',
        'ة': 'ه', 'ى': 'ي', 'ؤ': 'و',
        'ئ': 'ي', 'ّ': '', 'َ': '',
        'ُ': '', 'ِ': '', 'ْ': '',
        'ً': '', 'ٌ': '', 'ٍ': '',
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

    a = math.sin(dphi/2)**2 + math.cos(phi1) * \
        math.cos(phi2)*math.sin(dlambda/2)**2
    return int(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))))


def process_text(text):
    """معالجة النص وفهم القصد منه مع دعم متعدد للكتابة"""
    text_norm = normalize_text(text)

    # ================= الميقات =================
    miqat_keywords = ['ميقات', 'احرام', 'إحرام', 'احرم', 'أحرم',
                      'من اين احرم', 'اين الميقات', 'متي احرم', 'متى احرم',
                      'موعد الاحرام', 'مكان الاحرام', 'محل الاحرام',
                      'ميقات الاحرام', 'دخول ميقات', 'خروج ميقات',
                      'اين يحرم اهل', 'ميقات اهل', 'احرم من', 'احرم اذا',
                      'أحرم من', 'كيف احرم', 'من وين احرم', 'وين الميقات']

    # بلاد الشام
    sham_countries = {'شام': 'miqat_sham', 'سوريا': 'miqat_sham', 'سوري': 'miqat_sham', 'سوريه': 'miqat_sham',
                      'لبنان': 'miqat_sham', 'لبناني': 'miqat_sham', 'لبنانيه': 'miqat_sham',
                      'اردن': 'miqat_sham', 'اردني': 'miqat_sham', 'الاردن': 'miqat_sham',
                      'فلسطين': 'miqat_sham', 'فلسطيني': 'miqat_sham', 'فلسطينيه': 'miqat_sham',
                      'غزه': 'miqat_sham', 'غزة': 'miqat_sham', 'القدس': 'miqat_sham'}

    # مصر وشمال أفريقيا
    egypt_countries = {'مصر': 'miqat_egypt', 'مصري': 'miqat_egypt', 'مصريه': 'miqat_egypt',
                       'القاهرة': 'miqat_egypt', 'اسكندرية': 'miqat_egypt', 'اسكندريه': 'miqat_egypt',
                       'ليبا': 'miqat_egypt', 'ليبيا': 'miqat_egypt', 'ليبي': 'miqat_egypt',
                       'تونس': 'miqat_egypt', 'تونسي': 'miqat_egypt', 'تونسيه': 'miqat_egypt',
                       'جزاير': 'miqat_egypt', 'الجزاير': 'miqat_egypt', 'جزائر': 'miqat_egypt',
                       'الجزائر': 'miqat_egypt', 'جزائري': 'miqat_egypt',
                       'مغرب': 'miqat_egypt', 'المغرب': 'miqat_egypt', 'مغربي': 'miqat_egypt',
                       'موريتانيا': 'miqat_egypt', 'موريتاني': 'miqat_egypt',
                       'السودان': 'miqat_egypt', 'سوداني': 'miqat_egypt', 'سودان': 'miqat_egypt',
                       'تشاد': 'miqat_egypt', 'تشادي': 'miqat_egypt'}

    # اليمن
    yemen_countries = {'يمن': 'miqat_yemen', 'اليمن': 'miqat_yemen', 'يمني': 'miqat_yemen',
                       'صنعاء': 'miqat_yemen', 'عدن': 'miqat_yemen', 'حضرموت': 'miqat_yemen'}

    # التحقق من الميقات أولاً
    if any(keyword in text_norm for keyword in miqat_keywords):
        # البحث في جميع قوائم البلدان
        all_countries = {**sham_countries, **egypt_countries, **yemen_countries}

        for country_keyword, miqat_type in all_countries.items():
            if country_keyword in text_norm:
                return miqat_type

        # إذا ذكر ميقات بدون بلد
        if 'شام' in text_norm or 'سور' in text_norm or 'لبن' in text_norm or 'فلسطين' in text_norm or 'اردن' in text_norm:
            return "miqat_sham"
        elif 'مصر' in text_norm or 'شمال' in text_norm or 'افريقيا' in text_norm:
            return "miqat_egypt"
        elif 'يمن' in text_norm:
            return "miqat_yemen"
        else:
            return "miqat_menu"

    # الحج
    hajj_keywords = ['حج', 'حجاج', 'الحج', 'حجج', 'حجه', 'حجا']
    if any(keyword in text_norm for keyword in hajj_keywords):
        return "hajj"

    # العمرة
    umrah_keywords = ['عمره', 'عمرة', 'عمر', 'العمرة', 'العمره']
    if any(keyword in text_norm for keyword in umrah_keywords):
        return "umrah"

    # الأدعية
    if text_norm in ["ادعيه", "ادعية", "دعاء", "الادعيه", "الادعية"]:
        return "dua_menu"

    if "احرام" in text_norm:
        return "dua_ihram"

    if "طواف" in text_norm:
        return "dua_tawaf"

    if "سعي" in text_norm:
        return "dua_saee"

    if "عرفه" in text_norm or "عرفة" in text_norm:
        return "dua_arafah"

    if "جمرات" in text_norm or "رمي" in text_norm:
        return "dua_jamarat"

    # الأخطاء
    mistakes_keywords = ['خطاء', 'خطا', 'غلط', 'كفارة']
    if any(keyword in text_norm for keyword in mistakes_keywords):
        if 'لبس مخيط' in text_norm:
            return "mistake_clothes"
        elif 'طيب' in text_norm:
            return "mistake_perfume"
        elif 'قص شعر' in text_norm or 'قص اظافر' in text_norm:
            return "mistake_hair_nails"
        elif 'تغطية الرأس' in text_norm:
            return "mistake_cover_head"
        elif 'طواف بدون وضوء' in text_norm:
            return "mistake_tawaf_no_wudu"
        elif 'نسي شوط' in text_norm:
            return "mistake_miss_shawt"
        else:
            return "mistakes_menu"

    # المواقع
    map_keywords = ['خريطة', 'موقع', 'مكان', 'اين', 'وين']
    if any(keyword in text_norm for keyword in map_keywords):
        if 'حرام' in text_norm:
            return "map_haram"
        elif 'صفا' in text_norm:
            return "map_safa"
        elif 'مروه' in text_norm:
            return "map_marwa"
        else:
            return "map_menu"

    # الترحيب والعودة
    if any(word in text_norm for word in ['اهلا', 'مرحبا', 'سلام']):
        return "start"
    elif any(word in text_norm for word in ['رجوع', 'رجع', 'عوده']):
        return "back"

    return "unknown"

# ================= وظائف الحج والعمرة =================

async def handle_hajj(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = """**مناسك الحج خطوة بخطوة:**

**الأيام الثلاثة الأولى (8-10 ذي الحجة):**
📅 **اليوم 8 (التروية):** الإحرام والمبيت في منى

📅 **اليوم 9 (عرفة):**
🌅 الصباح: الذهاب إلى عرفة
☀️ الظهر: الوقوف والدعاء حتى الغروب
🌇 المساء: التوجه إلى مزدلفة

📅 **اليوم 10 (النحر):**
🌄 الفجر: الصلاة في مزدلفة وجمع الحصى
🌞 الصباح: رمي جمرة العقبة → الحلق → الذبح → الطواف

**أيام التشريق (11-13 ذي الحجة):**
📅 رمي الجمرات الثلاث → المبيت في منى → تكرار لمدة 2-3 أيام

**أخيراً:** طواف الوداع عند المغادرة
"""
    await update.message.reply_text(response, reply_markup=markup_back, parse_mode='Markdown')


async def handle_umrah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = """**معلومات شاملة عن العمرة:**

🕋 **ما هي العمرة؟**
زيارة بيت الله الحرام لأداء نسك مخصوص من طواف وسعي وحلق.

**خطوات العمرة بالترتيب:**
1️⃣ **الإحرام من الميقات**
   - النية: "اللهم إني أريد العمرة"
   - التلبية: "لبيك اللهم عمرة"

2️⃣ **الطواف حول الكعبة (7 أشواط)**
   - تبدأ من الحجر الأسود
   - تدور عكس عقارب الساعة

3️⃣ **صلاة ركعتين خلف مقام إبراهيم**

4️⃣ **السعي بين الصفا والمروة (7 أشواط)**
   - تبدأ من الصفا وتنتهي بالمروة

5️⃣ **الحلق أو التقصير**
   - الرجال: الحلق أفضل أو التقصير
   - النساء: تقصير قدر أنملة من الشعر
"""
    await update.message.reply_text(response, reply_markup=markup_back, parse_mode='Markdown')

# ================= وظائف الأدعية =================

async def duas_menu(update, context):
    text = "**📿 اختر نوع الدعاء:**"
    await update.message.reply_text(text, reply_markup=markup_dua, parse_mode='Markdown')


async def dua_ihram(update, context):
    text = """**أدعية الإحرام:**

📿 *النية:*
اللهم إني نويت العمرة/الحج فيسره لي وتقبله مني.

📿 *الدعاء:*
اللهم إني أسألك رضاك والجنة، وأعوذ بك من سخطك والنار.

📿 *التلبية:*
لبيك اللهم لبيك، لبيك لا شريك لك لبيك، إن الحمد والنعمة لك والملك، لا شريك لك."""
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_tawaf(update, context):
    text = """**أدعية الطواف:**

📿 *في بداية كل شوط:*
بسم الله والله أكبر

📿 *دعاء عام:*
ربنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار.

📿 *دعاء آخر:*
اللهم اغفر وارحم واعف عما تعلم، إنك أنت الأعز الأكرم."""
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_saee(update, context):
    text = """**أدعية السعي:**

📿 *عند الصفا:*
إِنَّ الصَّفَا وَالْمَرْوَةَ مِن شَعَائِرِ اللَّهِ

📿 *أثناء السعي:*
رب اغفر وارحم وتجاوز عما تعلم.

📿 *عند المروة:*
اللهم اجعلني من المقبولين."""
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_arafah(update, context):
    text = """**أدعية يوم عرفة:**

📿 *أفضل الدعاء:*
لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.

📿 *دعاء عام:*
اللهم اغفر لي ولوالدي وللمؤمنين والمؤمنات.

📿 *دعاء شامل:*
اللهم أصلح لي ديني ودنياي وآخرتي."""
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_jamarat(update, context):
    text = """**أدعية رمي الجمرات:**

📿 *عند كل حصاة:*
الله أكبر، رغما للشيطان وحزبِه.

📿 *بعد الرمي:*
اللهم اجعله حجًا مبرورًا وسعيًا مشكورًا.

📿 *دعاء عام:*
اللهم تقبل مني إنك أنت السميع العليم."""
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_general(update, context):
    text = """**أدعية عامة:**

📿 *لتيسير الأمور:*
رب اشرح لي صدري ويسر لي أمري.

📿 *لحسن الخاتمة:*
اللهم حسن الخاتمة.

📿 *أدعية جميلة:*
• اللهم اجعل آخر كلامنا من الدنيا لا إله إلا الله.
• اللهم ارزقني حجًا مبرورًا وسعيًا مشكورًا."""
    await update.message.reply_text(text, parse_mode='Markdown')

# ================= وظائف الأخطاء =================

async def mistakes_menu_show(update, context):
    text = "**⚠️ اختر الخطأ الذي وقعت فيه:**"
    await update.message.reply_text(text, reply_markup=markup_mistakes, parse_mode='Markdown')


async def mistake_detail(update, text):
    await update.message.reply_text(text, parse_mode='Markdown')

# ================= وظائف الخرائط =================

async def map_menu_show(update, context):
    text = "**🗺️ اختر الموقع:**"
    await update.message.reply_text(text, reply_markup=markup_map, parse_mode='Markdown')


async def send_haram_location(update, context):
    await update.message.reply_location(latitude=21.4225, longitude=39.8262)
    await update.message.reply_text(
        "**المسجد الحرام:**\n"
        "مكة المكرمة، المملكة العربية السعودية\n\n"
        "💎 *أهم الأماكن:*\n"
        "• الكعبة المشرفة\n• الحجر الأسود\n• مقام إبراهيم\n• بئر زمزم",
        parse_mode='Markdown'
    )


async def send_safa_location(update, context):
    await update.message.reply_location(latitude=21.4229, longitude=39.8257)
    await update.message.reply_text(
        "**جبل الصفا:**\n"
        "يبدأ منه السعي بين الصفا والمروة\n\n"
        "💎 *عند الصعود عليه:*\n"
        "يقرأ: إِنَّ الصَّفَا وَالْمَرْوَةَ مِن شَعَائِرِ اللَّهِ",
        parse_mode='Markdown'
    )


async def send_marwah_location(update, context):
    await update.message.reply_location(latitude=21.4237, longitude=39.8267)
    await update.message.reply_text(
        "**جبل المروة:**\n"
        "ينتهي إليه السعي بين الصفا والمروة\n\n"
        "💎 *بعد الانتهاء من السعي:*\n"
        "يقوم الحاج بالحلق أو التقصير",
        parse_mode='Markdown'
    )

# ================= وظائف الميقات =================

async def miqat_sham(update, context):
    text = """**🕋 ميقات بلاد الشام**
(سوريا، لبنان، الأردن، فلسطين)

📍 **الميقات:** ذو الحليفة (أبيار علي)
🌍 **الموقع:** شمال غرب المدينة المنورة
📏 **المسافة:** حوالي 450 كم من مكة

**📋 الإجراءات:**
• النية قبل الوصول للميقات
• لبس الإحرام في السيارة أو الطائرة
• بدء التلبية: 'لبيك اللهم حجاً'"""
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=24.9167, longitude=39.6167)


async def miqat_egypt(update, context):
    text = """**🕋 ميقات مصر وشمال أفريقيا**
(مصر، ليبيا، تونس، الجزائر، المغرب، السودان)

📍 **الميقات:** الجحفة (رابغ)
🌍 **الموقع:** على الطريق الساحلي إلى مكة
📏 **المسافة:** حوالي 180 كم شمال غرب مكة

**✈️ للحجاج الجويين:**
• تحرم في الطائرة قبل الهبوط
• لا يجوز تأخير الإحرام"""
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=26.3294, longitude=35.3123)


async def miqat_yemen(update, context):
    text = """**🕋 ميقات اليمن**
(اليمن، حضرموت)

📍 **الميقات:** يَلَمْلم
🌍 **الموقع:** شرق مكة على حدود نجد
📏 **المسافة:** حوالي 100 كم شرق مكة

**✈️ للحجاج الجويين:**
• إذا هبطت في جدة: تحرم في المطار
• لا تجاوز الميقات دون إحرام"""
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=21.4167, longitude=40.6000)


async def miqat_general(update, context):
    text = """**🕋 معلومات عامة عن مواقيت الإحرام**

**📌 المواقيت المكانية الخمسة:**
1. **ذي الحليفة:** لأهل المدينة والشام
2. **الجحفة:** لأهل مصر وشمال أفريقيا
3. **يلملم:** لأهل اليمن والجنوب
4. **قرن المنازل:** لأهل نجد والشرق
5. **ذات عرق:** لأهل العراق والشمال

**💡 قاعدة عامة:**
أي شخص قاصد مكة للحج أو العمرة لا يجوز له تجاوز الميقات دون إحرام"""
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')

# ================= start =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """🌙 *مرحبا بك في مساعد الحج والعمرة* 🤲

*للاستعلام عن الميقات، اكتب اسم بلدك مثل:*
• "مصر" أو "المغرب" أو "الجزائر"
• "سوريا" أو "لبنان" أو "فلسطين"

*أو اكتب أي مما يلي:*
• "عمره" أو "حج"
• "دعاء طواف" أو "أدعية السعي"
• "خريطة الحرم" أو "موقع الصفا"

*أو اختر من القائمة:* 👇"""
    await update.message.reply_text(welcome_text, reply_markup=markup_main, parse_mode='Markdown')


async def send_current_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يرسل موقع الحاج الحالي"""
    if update.message.location:
        lat = update.message.location.latitude
        lon = update.message.location.longitude

        # حساب المسافة من الحرم
        dist_haram = calculate_distance(lat, lon, 21.4225, 39.8262)

        await update.message.reply_location(latitude=lat, longitude=lon)
        await update.message.reply_text(
            f"**موقعك الحالي:**\n"
            f"📍 خط العرض: {lat:.4f}\n"
            f"📍 خط الطول: {lon:.4f}\n\n"
            f"**المسافة من الحرم:** {dist_haram:,} متر\n\n"
            f"💡 *إذا كنت في مكة، يمكنك الإحرام من مكانك*",
            reply_markup=markup_main,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "📍 **يرجى الضغط على زر 'إرسال موقعي' للحصول على موقعك:**",
            reply_markup=location_keyboard,
            parse_mode='Markdown'
        )

# ================= معالج الرسائل الرئيسي =================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة جميع الرسائل النصية"""
    text = update.message.text.strip()
    
    # التحقق من الأزرار أولاً
    if text == "رجوع للقائمة الرئيسية" or text == "رجوع":
        await start(update, context)
        return
    
    # القائمة الرئيسية
    elif text == "الحج":
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
        await update.message.reply_text(
            "**🌍 ميقات الإحرام للبلدان المختلفة**\n\nاختر منطقتك:",
            reply_markup=markup_miqat,
            parse_mode='Markdown'
        )
    
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
        await mistake_detail(update,
            """**👕 لبس المخيط (للرجل)**

❌ **الخطأ:** لبس مخيط بعد الإحرام
⚖️ **الحكم:** محظور إحرام
💰 **الكفارة:** فدية أذى (اختيار واحد)
- ذبح شاة
- أو إطعام 6 مساكين
- أو صيام 3 أيام

**ماذا تفعل؟** اخلعه فوراً وادفع الفدية.""")
    elif text == "التطيب بعد الإحرام":
        await mistake_detail(update,
            """**🌹 التطيب بعد الإحرام**

❌ **الخطأ:** استعمال الطيب أو العطر بعد الإحرام
⚖️ **الحكم:** محظور إحرام
💰 **الكفارة:** فدية أذى""")
    elif text == "قص الشعر أو الأظافر":
        await mistake_detail(update,
            """**✂️ قص الشعر أو الأظافر**

❌ **الخطأ:** قص الشعر أو الأظافر أثناء الإحرام
⚖️ **الحكم:** محظور إحرام
💰 **الكفارة:** فدية أذى""")
    elif text == "تغطية الرأس":
        await mistake_detail(update,
            """**🧢 تغطية الرأس (للرجل)**

❌ **الخطأ:** تغطية الرأس بعد الإحرام
⚖️ **الحكم:** محظور إحرام
💰 **الكفارة:** فدية أذى
📌 **ملاحظة:** المظلة لا تُعد تغطية.""")
    elif text == "الطواف بدون وضوء":
        await mistake_detail(update,
            """**💧 الطواف بدون وضوء**

❌ **الخطأ:** الطواف بدون وضوء
⚖️ **الحكم:** الطواف غير صحيح عند جمهور العلماء
**ما العمل؟** يجب إعادة الطواف فقط
💰 **كفارة:** لا يوجد""")
    elif text == "نسي شوط":
        await mistake_detail(update,
            """**🔄 نسي شوط**

❌ **الخطأ:** نسي شوط في الطواف أو السعي
⚖️ **الحكم:** إن تذكرت قريبًا أكمل، إن طال الفصل أعد الطواف
💰 **كفارة:** لا يوجد""")
    elif text == "السعي قبل الطواف":
        await mistake_detail(update,
            """**🚶 السعي قبل الطواف**

❌ **الخطأ:** السعي قبل الطواف
⚖️ **الحكم:** السعي غير صحيح
**ما العمل؟** أعد السعي بعد الطواف
💰 **كفارة:** لا يوجد""")
    elif text == "ترك واجب":
        await mistake_detail(update,
            """**⚠️ ترك واجب**

❌ **الخطأ:** ترك واجب (مبيت، رمي)
⚖️ **الحكم:** النسك صحيح
💰 **الكفارة:** دم (ذبح شاة)
📌 **تنبيه:** لا صيام بديل""")
    elif text == "الجماع":
        await mistake_detail(update,
            """**💔 الجماع قبل التحلل الأول**

❌ **الخطأ:** الجماع قبل التحلل الأول
⚖️ **الحكم:** يفسد النسك
**ما يجب:**
- إكمال الحج
- القضاء من عام قادم
- ذبح بدنة (جمل)""")
    
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
            await update.message.reply_text(
                "**🌍 ميقات الإحرام للبلدان المختلفة**\n\nاختر منطقتك:",
                reply_markup=markup_miqat,
                parse_mode='Markdown'
            )
        elif intent == "start":
            await start(update, context)
        elif intent == "back":
            await start(update, context)
        elif intent == "unknown":
            await update.message.reply_text(
                "🤔 لم أفهم سؤالك.\n\n"
                "*للميقات، اكتب:*\n"
                "• 'مصر' أو 'سوريا'\n"
                "*أو استخدم الأزرار* 👇",
                reply_markup=markup_main,
                parse_mode='Markdown'
            )

# ================= معالج الموقع =================

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الموقع المرسل من المستخدم"""
    await send_current_location(update, context)

# ================= الدالة الرئيسية =================

def main():
    """تشغيل البوت"""
    # بناء التطبيق
    app = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    
    print("🤖 البوت يعمل...")
    app.run_polling()


if __name__ == "__main__":
    main()
