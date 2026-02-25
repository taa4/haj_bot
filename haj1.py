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

# ================= القوائم =================
main_menu = [
    ["الحج", "العمرة"],
    ["الأدعية", "الخريطة"],
    ["الأخطاء والكفارات", "ميقات الإحرام"]
]

mistakes_menu = [
    ["لبس المخيط", "التطيب بعد الإحرام"],
    ["قص الشعر أو الأظافر", "تغطية الرأس"],
    ["الطواف بدون وضوء", "نسي شوط"],
    ["السعي قبل الطواف", "ترك واجب"],
    ["الجماع"],
    ["رجوع"]
]

dua_menu = [
    ["أدعية الإحرام", "أدعية الطواف"],
    ["أدعية السعي", "أدعية عرفة"],
    ["أدعية الجمرات", "أدعية عامة"],
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
    ["الخليج العربي"],
    ["أمريكا وأوروبا"],
    ["آسيا"],
    ["رجوع"]
]

back_menu = [["رجوع للقائمة الرئيسية"]]
markup_dua = ReplyKeyboardMarkup(dua_menu, resize_keyboard=True)
markup_main = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
markup_back = ReplyKeyboardMarkup(back_menu, resize_keyboard=True)
markup_miqat = ReplyKeyboardMarkup(miqat_menu, resize_keyboard=True)
markup_map = ReplyKeyboardMarkup(map_menu, resize_keyboard=True)
markup_mistakes = ReplyKeyboardMarkup(mistakes_menu, resize_keyboard=True)

# زر مشاركة الموقع
location_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("إرسال موقعي", request_location=True)],
     ["رجوع"]],
    resize_keyboard=True
)


# ================= معالجة النصوص المتقدمة =================

def normalize_text(text):
    """تقنين النص وإزالة التشكيل والحركات"""
    text = text.strip().lower()

    # استبدال الأحرف المشابهة
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


def process_text(text):
    """معالجة النص وفهم القصد منه مع دعم متعدد للكتابة"""
    text_norm = normalize_text(text)

    # ================= الميقات - تغطية شاملة =================
    miqat_keywords = [
        'ميقات', 'احرام', 'إحرام', 'احرم', 'أحرم',
        'من اين احرم', 'اين الميقات', 'متي احرم', 'متى احرم',
        'موعد الاحرام', 'مكان الاحرام', 'محل الاحرام',
        'ميقات الاحرام', 'دخول ميقات', 'خروج ميقات',
        'اين يحرم اهل', 'ميقات اهل', 'احرم من', 'احرم اذا',
        'أحرم من', 'كيف احرم', 'من وين احرم', 'وين الميقات'
    ]

    # بلاد الشام
    sham_countries = {
        'شام': 'miqat_sham',
        'سوريا': 'miqat_sham', 'سوري': 'miqat_sham', 'سوريه': 'miqat_sham',
        'لبنان': 'miqat_sham', 'لبناني': 'miqat_sham', 'لبنانيه': 'miqat_sham',
        'اردن': 'miqat_sham', 'اردني': 'miqat_sham', 'الاردن': 'miqat_sham',
        'فلسطين': 'miqat_sham', 'فلسطيني': 'miqat_sham', 'فلسطينيه': 'miqat_sham',
        'غزه': 'miqat_sham', 'غزة': 'miqat_sham', 'القدس': 'miqat_sham'
    }

    # مصر وشمال أفريقيا
    egypt_countries = {
        'مصر': 'miqat_egypt', 'مصري': 'miqat_egypt', 'مصريه': 'miqat_egypt',
        'القاهرة': 'miqat_egypt', 'اسكندرية': 'miqat_egypt', 'اسكندريه': 'miqat_egypt',
        'ليبا': 'miqat_egypt', 'ليبيا': 'miqat_egypt', 'ليبي': 'miqat_egypt',
        'تونس': 'miqat_egypt', 'تونسي': 'miqat_egypt', 'تونسيه': 'miqat_egypt',
        'جزاير': 'miqat_egypt', 'الجزاير': 'miqat_egypt', 'جزائر': 'miqat_egypt',
        'الجزائر': 'miqat_egypt', 'جزائري': 'miqat_egypt',
        'مغرب': 'miqat_egypt', 'المغرب': 'miqat_egypt', 'مغربي': 'miqat_egypt',
        'موريتانيا': 'miqat_egypt', 'موريتاني': 'miqat_egypt',
        'السودان': 'miqat_egypt', 'سوداني': 'miqat_egypt', 'سودان': 'miqat_egypt',
        'تشاد': 'miqat_egypt', 'تشادي': 'miqat_egypt'
    }

    # اليمن
    yemen_countries = {
        'يمن': 'miqat_yemen', 'اليمن': 'miqat_yemen', 'يمني': 'miqat_yemen',
        'صنعاء': 'miqat_yemen', 'عدن': 'miqat_yemen', 'حضرموت': 'miqat_yemen'
    }

    # الخليج العربي
    gulf_countries = {
        'سعوديه': 'miqat_saudi', 'السعوديه': 'miqat_saudi', 'السعودية': 'miqat_saudi',
        'سعودي': 'miqat_saudi', 'الرياض': 'miqat_saudi', 'جده': 'miqat_saudi',
        'جدة': 'miqat_saudi', 'مكة': 'miqat_saudi', 'مكه': 'miqat_saudi',
        'المدينة': 'miqat_saudi', 'المدينه': 'miqat_saudi', 'الدمام': 'miqat_saudi',
        'امارات': 'miqat_saudi', 'الامارات': 'miqat_saudi', 'دبي': 'miqat_saudi',
        'ابوظبي': 'miqat_saudi', 'عجمان': 'miqat_saudi', 'الشارقة': 'miqat_saudi',
        'قطر': 'miqat_saudi', 'قطري': 'miqat_saudi', 'الدوحة': 'miqat_saudi',
        'كويت': 'miqat_saudi', 'الكويت': 'miqat_saudi', 'كويتي': 'miqat_saudi',
        'بحرين': 'miqat_saudi', 'البحرين': 'miqat_saudi', 'المنامة': 'miqat_saudi',
        'عمان': 'miqat_saudi', 'سلطنة عمان': 'miqat_saudi', 'مسقط': 'miqat_saudi'
    }

    # بلدان أخرى
    other_countries = {
        'تركيا': 'miqat_general', 'تركي': 'miqat_general', 'استانبول': 'miqat_general',
        'ايران': 'miqat_general', 'ايراني': 'miqat_general',
        'افغانستان': 'miqat_asia', 'افغاني': 'miqat_asia',
        'باكستان': 'miqat_asia', 'باكستاني': 'miqat_asia',
        'الهند': 'miqat_asia', 'هندي': 'miqat_asia',
        'اندونيسيا': 'miqat_asia', 'اندونيسي': 'miqat_asia',
        'ماليزيا': 'miqat_asia', 'ماليزي': 'miqat_asia',
        'امريكا': 'miqat_america', 'الولايات المتحدة': 'miqat_america',
        'كندا': 'miqat_america', 'كندي': 'miqat_america',
        'بريطانيا': 'miqat_america', 'المملكة المتحدة': 'miqat_america',
        'فرنسا': 'miqat_america', 'فرنسي': 'miqat_america',
        'المانيا': 'miqat_america', 'الماني': 'miqat_america'
    }

    # التحقق من الميقات أولاً
    if any(keyword in text_norm for keyword in miqat_keywords):
        # البحث في جميع قوائم البلدان
        all_countries = {**sham_countries, **egypt_countries,
                         **yemen_countries, **gulf_countries, **other_countries}

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
        elif 'خليج' in text_norm or 'سعود' in text_norm or 'امارات' in text_norm or 'دبي' in text_norm:
            return "miqat_saudi"
        else:
            return "miqat_menu"

    # ================= بقية المعالجات =================
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

    if "ادعية طواف" in text_norm:
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
        if 'لبس المخيط' in text_norm or 'مخيط' in text_norm or 'لبس ملابس عادية' in text_norm:
            return "mistake_clothes"

    if 'تطيب' in text_norm or 'عطر' in text_norm or 'رش العطر' in text_norm:
        return "mistake_perfume"

    if 'قص شعر' in text_norm or 'قص اظافر' in text_norm or 'الشعر' in text_norm or 'الاظافر' in text_norm:
        return "mistake_hair_nails"

    if 'تغطية الراس' in text_norm:
        return "mistake_cover_head"

    if 'طواف بدون وضوء' in text_norm:
        return "mistake_tawaf_no_wudu"

    if 'نسي شوط' in text_norm or 'شوط' in text_norm or 'نسي شوط واحد' in text_norm:
        return "mistake_miss_shawt"

    if 'السعي قبل الطواف' in text_norm or 'نسيان طواف' in text_norm :
        return "mistake_saee_before_tawaf"
 
    if 'ترك واجب' in text_norm or 'نسيان واجب' in text_norm:
        return "mistake_leave_wajib"

    if 'جماع' in text_norm:
        return "mistake_intercourse"
    

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
    text = update.message.text.lower()

    if "اركان" in text:
        response = """**أركان الحج:**
1️⃣ **الإحرام**: النية والدخول في النسك
2️⃣ **الوقوف بعرفة**: من زوال الشمس يوم عرفة إلى فجر يوم النحر
3️⃣ **طواف الإفاضة**: بعد الوقوف بعرفة
4️⃣ **السعي بين الصفا والمروة**: بعد الطواف
"""
    elif "واجبات" in text:
        response = """**واجبات الحج:**
1. الإحرام من الميقات
2. المبيت بمزدلفة
3. المبيت بمنى
4. رمي الجمرات
5. الحلق أو التقصير
6. طواف الوداع
"""
    else:
        response = """**مناسك الحج خطوة بخطوة:**

**الأيام الثلاثة الأولى (8-10 ذي الحجة):**
📅 **اليوم 8 (التروية):** الإحرام والمبيت في منى

📅 **اليوم 9 (عرفة):**
🌅 الصباح: الذهاب إلى عرفة
☀️ الظهر: الوقوف والدعاء حتى الغروب
🌇 المساء: التوجه إلى مزدلفة

📅 **اليوم 10 (النحر):**
🌄 الفجر: الصلاة في مزدلفة وجمع الحصى
🌞 الصباح: رمي جمرة العقبة ← الحلق ← الذبح ← الطواف

**أيام التشريق (11-13 ذي الحجة):**
📅 رمي الجمرات الثلاث ← المبيت في منى ← تكرار لمدة 2-3 أيام

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
   - تكبر عند المرور بالحجر الأسود

3️⃣ **صلاة ركعتين خلف مقام إبراهيم**

4️⃣ **السعي بين الصفا والمروة (7 أشواط)**
   - تبدأ من الصفا وتنتهي بالمروة
   - الهرولة بين العلمين الأخضرين (للرجال)

5️⃣ **الحلق أو التقصير**
   - الرجال: الحلق أفضل أو التقصير
   - النساء: تقصير قدر أنملة من الشعر

📅 **متى تؤدى؟**
في أي وقت من السنة، وأفضلها في رمضان.
"""
    await update.message.reply_text(response, reply_markup=markup_back, parse_mode='Markdown')

# ================= وظائف الأدعية =================

async def duas_menu(update, context):
    text = (
        "**أدعية الحج والعمرة:**\n\n"
        "اكتب ما تريد:\n"
        "• 'أدعية الإحرام'\n"
        "• 'دعاء الطواف'\n"
        "• 'أدعية السعي'\n"
        "• 'دعاء عرفة'\n"
        "• 'أدعية الجمرات'\n"
        "• 'أدعية عامة'"
    )
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')


async def dua_ihram(update, context):
    text = (
        "**أدعية الإحرام:**\n\n"
        "📿 *النية:*\n"
        "اللهم إني نويت العمرة/الحج فيسره لي وتقبله مني.\n\n"
        "📿 *الدعاء:*\n"
        "اللهم إني أسألك رضاك والجنة، وأعوذ بك من سخطك والنار.\n\n"
        "📿 *التلبية:*\n"
        "لبيك اللهم لبيك، لبيك لا شريك لك لبيك، إن الحمد والنعمة لك والملك، لا شريك لك."
    )
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_tawaf(update, context):
    text = (
        "**أدعية الطواف:**\n\n"
        "📿 *في بداية كل شوط:*\n"
        "بسم الله والله أكبر\n\n"
        "📿 *دعاء عام:*\n"
        "ربنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار.\n\n"
        "📿 *دعاء آخر:*\n"
        "اللهم اغفر وارحم واعف عما تعلم، إنك أنت الأعز الأكرم."
    )
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_saee(update, context):
    text = (
        "**أدعية السعي:**\n\n"
        "📿 *عند الصفا:*\n"
        "إِنَّ الصَّفَا وَالْمَرْوَةَ مِن شَعَائِرِ اللَّهِ\n\n"
        "📿 *أثناء السعي:*\n"
        "رب اغفر وارحم وتجاوز عما تعلم.\n\n"
        "📿 *عند المروة:*\n"
        "اللهم اجعلني من المقبولين."
    )
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_arafah(update, context):
    text = (
        "**أدعية يوم عرفة:**\n\n"
        "📿 *أفضل الدعاء:*\n"
        "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.\n\n"
        "📿 *دعاء عام:*\n"
        "اللهم اغفر لي ولوالدي وللمؤمنين والمؤمنات.\n\n"
        "📿 *دعاء شامل:*\n"
        "اللهم أصلح لي ديني ودنياي وآخرتي."
    )
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_jamarat(update, context):
    text = (
        "**أدعية رمي الجمرات:**\n\n"
        "📿 *عند كل حصاة:*\n"
        "الله أكبر، رغما للشيطان وحزبِه.\n\n"
        "📿 *بعد الرمي:*\n"
        "اللهم اجعله حجًا مبرورًا وسعيًا مشكورًا.\n\n"
        "📿 *دعاء عام:*\n"
        "اللهم تقبل مني إنك أنت السميع العليم."
    )
    await update.message.reply_text(text, parse_mode='Markdown')


async def dua_general(update, context):
    text = (
        "**أدعية عامة:**\n\n"
        "📿 *لتيسير الأمور:*\n"
        "رب اشرح لي صدري ويسر لي أمري.\n\n"
        "📿 *لحسن الخاتمة:*\n"
        "اللهم حسن الخاتمة.\n\n"
        "📿 *أدعية جميلة:*\n"
        "• اللهم اجعل آخر كلامنا من الدنيا لا إله إلا الله.\n"
        "• اللهم ارزقني حجًا مبرورًا وسعيًا مشكورًا.\n"
        "• اللهم اغفر لي ذنبي كله دقه وجله."
    )
    await update.message.reply_text(text, parse_mode='Markdown')

# ================= وظائف الأخطاء =================

async def mistakes_menu_show(update, context):
    text = (
        "**الأخطاء الشائعة وكفاراتها:**\n\n"
        "اكتب الخطأ الذي تريد معرفته:\n"
        "• 'لبس المخيط'\n"
        "• 'التطيب بعد الإحرام'\n"
        "• 'قص الشعر أو الأظافر'\n"
        "• 'تغطية الرأس'\n"
        "• 'الطواف بدون وضوء'\n"
        "• 'نسي شوط'\n"
        "• 'السعي قبل الطواف'\n"
        "• 'ترك واجب'\n"
        "• 'الجماع'"
    )
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')


async def mistake_detail(update, text):
    await update.message.reply_text(text, parse_mode='Markdown')

# ================= وظائف الخرائط =================

async def map_menu_show(update, context):
    text = (
        "**المواقع المقدسة:**\n\n"
        "اكتب الموقع الذي تريد:\n"
        "• 'المسجد الحرام'\n"
        "• 'الصفا'\n"
        "• 'المروة'\n"
        "• 'موقعي الحالي'"
    )
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')


async def send_haram_location(update, context):
    await update.message.reply_location(latitude=21.4225, longitude=39.8262)
    await update.message.reply_text(
        "**المسجد الحرام:**\n"
        "مكة المكرمة، المملكة العربية السعودية\n\n"
        "💎 *أهم الأماكن:*\n"
        "• الكعبة المشرفة\n"
        "• الحجر الأسود\n"
        "• مقام إبراهيم\n"
        "• بئر زمزم",
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

# ================= معالجة الميقات للبلدان المختلفة =================

async def miqat_sham(update, context):
    """ميقات بلاد الشام"""
    text = (
        "**🕋 ميقات بلاد الشام**\n"
        "(سوريا، لبنان، الأردن، فلسطين، غزة، القدس)\n\n"

        "📍 **الميقات:** ذو الحليفة (أبيار علي)\n"
        "🌍 **الموقع:** شمال غرب المدينة المنورة، على طريق مكة.\n"
        "📏 **المسافة:** حوالي 450 كم من مكة\n\n"

        "**🚍 طريقة الوصول:**\n"
        "1. عبر الطرق البرية من الشمال\n"
        "2. عن طريق المدينة المنورة\n"
        "3. معظم الحجاج يمرون عبر الأردن\n\n"

        "**📋 الإجراءات:**\n"
        "• النية قبل الوصول للميقات\n"
        "• لبس الإحرام في السيارة أو الطائرة\n"
        "• بدء التلبية: 'لبيك اللهم حجاً'\n\n"

        "**💡 ملاحظات هامة:**\n"
        "• الميقات حدودي، لا يجوز تجاوزه دون إحرام\n"
        "• إذا نسي الحاج، يرجع للإحرام منه\n"
        "• يجوز الإحرام قبل الميقات استحباباً"
    )
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=24.9167, longitude=39.6167)


async def miqat_egypt(update, context):
    """ميقات مصر وشمال أفريقيا"""
    text = (
        "**🕋 ميقات مصر وشمال أفريقيا**\n"
        "(مصر، ليبيا، تونس، الجزائر، المغرب، السودان، موريتانيا، تشاد)\n\n"

        "📍 **الميقات:** الجحفة (رابغ)\n"
        "🌍 **الموقع:** على الطريق الساحلي إلى مكة، قرب البحر الأحمر\n"
        "📏 **المسافة:** حوالي 180 كم شمال غرب مكة\n\n"

        "**✈️ للحجاج الجويين:**\n"
        "1. **إذا هبطت في جدة:**\n"
        "   • تحرم في المطار أو قبل النزول\n"
        "   • لا يجوز تأخير الإحرام\n\n"

        "2. **إذا هبطت في المدينة:**\n"
        "   • تحرم من ذي الحليفة (أبيار علي)\n\n"

        "**🚢 للحجاج البحريين:**\n"
        "• يحرمون عند محاذاة الجحفة\n"
        "• أو قبل وصول السفينة للميقات\n\n"

        "**📋 تنبيهات:**\n"
        "• حجاج مصر عادة يذهبون جواً إلى جدة\n"
        "• لا يجوز تجاوز الميقات دون إحرام\n"
        "• من نسي يرجع أو يذبح فدية"
    )
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=26.3294, longitude=35.3123)


async def miqat_yemen(update, context):
    """ميقات اليمن"""
    text = (
        "**🕋 ميقات اليمن**\n"
        "(اليمن، حضرموت، صنعاء، عدن)\n\n"

        "📍 **الميقات:** يَلَمّ\n"
        "🌍 **الموقع:** شرق مكة على حدود نجد\n"
        "📏 **المسافة:** حوالي 100 كم شرق مكة\n\n"

        "**🚍 طرق الوصول:**\n"
        "1. الطريق البري عبر نجران\n"
        "2. بعض المناطق تحرم من قرن المنازل\n"
        "3. حجاج الجنوب قد يمرون من الساحل\n\n"

        "**✈️ للحجاج الجويين:**\n"
        "• إذا هبطت في جدة: تحرم في المطار\n"
        "• إذا هبطت في أبها: تحرم في الميقات\n\n"

        "**📋 ملاحظات:**\n"
        "• ميقات يلملم خاص بأهل اليمن\n"
        "• مناطق الجنوب قد تحرم من قرن\n"
        "• الاستعلام من العلماء المحليين"
    )
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=21.4167, longitude=40.6000)


async def miqat_saudi(update, context):
    """ميقات السعودية ودول الخليج"""
    text = (
        "**🕋 ميقات السعودية ودول الخليج**\n"
        "(السعودية، الإمارات، قطر، الكويت، البحرين، عُمان)\n\n"

        "📍 **الميقات العام:** قرن المنازل (السيل الكبير)\n"
        "🌍 **الموقع:** شرق مكة على طريق الطائف\n"
        "📏 **المسافة:** حوالي 75 كم شرق مكة\n\n"

        "**🏠 لأهل مكة والمدينة:**\n"
        "• **مكة:** يحرمون من بيوتهم\n"
        "• **المدينة:** ذو الحليفة (أبيار علي)\n"
        "• **الطائف:** يلملم أو قرن المنازل\n\n"

        "**🌐 حسب المدينة:**\n"
        "1. **الرياض والشرقية:** قرن المنازل\n"
        "2. **الجنوب (نجران):** يلملم\n"
        "3. **الشمال (حائل):** ذات عرق\n"
        "4. **الغرب (جدة):** يحرم من منزله\n\n"

        "**💡 للإمارات وقطر والكويت:**\n"
        "• يمرون عادة عبر الرياض\n"
        "• ميقاتهم قرن المنازل\n"
        "• أو يحرمون عند اقترابهم منه"
    )
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=21.3500, longitude=40.2000)


async def miqat_america(update, context):
    """ميقات أمريكا وكندا وأوروبا"""
    text = (
        "**🕋 ميقات أمريكا وكندا وأوروبا الغربية**\n"
        "(الولايات المتحدة، كندا، بريطانيا، فرنسا، ألمانيا، إيطاليا)\n\n"

        "📍 **الميقات:** الجحفة (للقادمين جواً)\n"
        "🌍 **معظم الحجاج يصلون عن طريق:**\n"
        "• مطار الملك عبدالعزيز بجدة\n"
        "• مطار الأمير محمد بن عبدالعزيز بالمدينة\n\n"

        "**✈️ إجراءات الإحرام:**\n"
        "1. **إذا هبطت في جدة:**\n"
        "   • تحرم في الطائرة قبل الهبوط\n"
        "   • وقت مناسب: قبل الهبوط بساعة\n"
        "   • التلبية في الطائرة جائزة\n\n"
        "2. **إذا هبطت في المدينة:**\n"
        "   • تنتقل إلى مكة براً\n"
        "   • تحرم من ذو الحليفة (أبيار علي)\n\n"

        "**💡 نصائح:**\n"
        "• خذ ملابس الإحرام في حقيبة اليد\n"
        "• استشر خط الطيران عن وقت الإحرام\n"
        "• معظم شركات الطيران تنبه الحجاج"
    )
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')


async def miqat_asia(update, context):
    """ميقات آسيا (الهند، باكستان، إندونيسيا، ماليزيا)"""
    text = (
        "**🕋 ميقات دول آسيا**\n"
        "(الهند، باكستان، إندونيسيا، ماليزيا، بنغلاديش، أفغانستان)\n\n"

        "📍 **الميقات:** يلملم (للقادمين بحراً)\n"
        "📍 **للقادمين جواً:** يحرمون في الطائرة\n\n"

        "**✈️ للحجاج الجويين:**\n"
        "• **الهند وباكستان:**\n"
        "   - تحرمون في الطائرة قبل دخول الأجواء السعودية\n"
        "   - وقت الإحرام: قبل الهبوط بساعتين تقريباً\n\n"

        "• **إندونيسيا وماليزيا:**\n"
        "   - الإحرام في الطائرة\n"
        "   - الميقات يقع في البحر\n"
        "   - خطوط الطيران تنبه عادة\n\n"

        "**🚢 للحجاج البحريين:**\n"
        "• ميقاتهم يلملم\n"
        "• يحرمون عند محاذاة الساحل\n"
        "• أو قبل الوصول إلى الميقات\n\n"

        "**💡 تنبيه:**\n"
        "• استعلم من مكتب الحج في بلدك\n"
        "• شركات الطيران توضح وقت الإحرام\n"
        "• لا تنتظر حتى المطار"
    )
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')


async def miqat_general(update, context):
    """معلومات عامة عن الميقات"""
    text = (
        "**🕋 معلومات عامة عن مواقيت الإحرام**\n\n"

        "**📌 المواقيت المكانية الخمسة:**\n"
        "1. **ذي الحليفة:** لأهل المدينة والشام\n"
        "2. **الجحفة:** لأهل مصر وشمال أفريقيا\n"
        "3. **يلملم:** لأهل اليمن والجنوب\n"
        "4. **قرن المنازل:** لأهل نجد والشرق\n"
        "5. **ذات عرق:** لأهل العراق والشمال\n\n"

        "**❓ أسئلة شائعة:**\n"
        "• **من نسي الإحرام؟** يرجع للميقات أو يذبح\n"
        "• **الحائض؟** تحرم وتتوقف عن التلبية\n"
        "• **المريض؟** يحرم ويرخص له\n"
        "• **من داخل المواقيت؟** يحرم من مكانه\n\n"

        "**💡 قاعدة عامة:**\n"
        "أي شخص قاصد مكة للحج أو العمرة:\n"
        "1. لا يجوز له تجاوز الميقات دون إحرام\n"
        "2. يستحب الإحرام من الميقات\n"
        "3. يجوز الإحرام قبله استحباباً\n"
        "4. من نسي يرجع أو عليه الفدية"
    )
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')

# ================= start محسّن =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🌙 *مرحبا بك في مساعد الحج والعمرة* 🤲

*للاستعلام عن الميقات، اكتب اسم بلدك مثل:*
• "مصر" أو "المغرب" أو "الجزائر"
• "سوريا" أو "لبنان" أو "فلسطين"
• "السعودية" أو "الإمارات" أو "قطر"
• "أمريكا" أو "كندا" أو "بريطانيا"
• "الهند" أو "باكستان" أو "إندونيسيا"

*أو اكتب أي مما يلي:*
• "عمره" أو "عمرة" أو "العمرة"
• "حج" أو "الحج" أو "حجاج"
• "دعاء طواف" أو "أدعية السعي"
• "خريطة الحرم" أو "موقع الصفا"
• "خطأ لبس مخيط" أو "كفارة قص شعر"

*أو اختر من القائمة:* 👇
"""
    await update.message.reply_text(welcome_text, reply_markup=markup_main, parse_mode='Markdown')


async def send_current_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    يرسل موقع الحاج الحالي
    """
    if update.message.location:
        lat = update.message.location.latitude
        lon = update.message.location.longitude

        # حساب المسافة من الحرم
        dist_haram = distance_m(lat, lon, 21.4225, 39.8262)

        await update.message.reply_location(latitude=lat, longitude=lon)
        await update.message.reply_text(
            f"**موقعك الحالي:**\n"
            f"📍 خط العرض: {lat}\n"
            f"📍 خط الطول: {lon}\n\n"
            f"**المسافة من الحرم:** {dist_haram} متر\n\n"
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


def distance_m(lat1, lon1, lat2, lon2):
    """حساب المسافة بين نقطتين"""
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * \
        math.cos(phi2)*math.sin(dlambda/2)**2
    return int(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))))

# ================= الرد على الرسائل النصية =================

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # ================= معالجة الأزرار أولاً =================
    
    # القائمة الرئيسية
    if text == "الحج":
        await handle_hajj(update, context)
        return

    elif text == "العمرة":
        await handle_umrah(update, context)
        return

    elif text == "الأدعية":
        await update.message.reply_text("📿 اختر نوع الدعاء:", reply_markup=markup_dua)
        return

    elif text == "الخريطة":
        await update.message.reply_text("🗺 اختر الموقع:", reply_markup=markup_map)
        return

    elif text == "الأخطاء والكفارات":
        await update.message.reply_text("⚠ اختر الخطأ:", reply_markup=markup_mistakes)
        return

    elif text == "ميقات الإحرام":
        await update.message.reply_text("🌍 اختر منطقتك:", reply_markup=markup_miqat)
        return

    # ================= أزرار الأدعية =================

    elif text == "أدعية الإحرام":
        await dua_ihram(update, context)
        return

    elif text == "أدعية الطواف":
        await dua_tawaf(update, context)
        return

    elif text == "أدعية السعي":
        await dua_saee(update, context)
        return

    elif text == "أدعية عرفة":
        await dua_arafah(update, context)
        return

    elif text == "أدعية الجمرات":
        await dua_jamarat(update, context)
        return

    elif text == "أدعية عامة":
        await dua_general(update, context)
        return

    # ================= أزرار الخريطة =================

    elif text == "المسجد الحرام":
        await send_haram_location(update, context)
        return

    elif text == "الصفا":
        await send_safa_location(update, context)
        return

    elif text == "المروة":
        await send_marwah_location(update, context)
        return

    elif text == "موقعي الحالي":
        await send_current_location(update, context)
        return
    
    # ================= أزرار الأخطاء =================

    elif text == "لبس المخيط":
        await mistake_detail(update,
                             "**👕 لبس المخيط (للرجل)**\n\n"
                             "❌ **الخطأ:** لبس المخيط، لبس ملابس، ارتداء ثياب\n"
                             "⚖️ **الحكم:** محظور إحرام\n💰 **الكفارة:** فدية أذى\n\n"
                             "**ماذا تفعل؟**\n1. اخلعه فوراً\n2. ادفع الفدية\n3. استمر في مناسكك"
                             )
        return

    elif text == "التطيب بعد الإحرام":
        await mistake_detail(update,
                             "**🌹 التطيب بعد الإحرام**\n\n"
                             "❌ **الخطأ:** استعمال الطيب أو العطر بعد الإحرام\n\n"
                             "⚖️ **الحكم:** محظور إحرام\n\n"
                             "💰 **الكفارة:** فدية أذى"
                             )
        return

    elif text == "قص الشعر أو الأظافر":
        await mistake_detail(update,
                             "**💇 قص الشعر أو الأظافر**\n\n"
                             "❌ **الخطأ:** قص الشعر أو الأظافر\n\n"
                             "⚖️ **الحكم:** محظور إحرام\n"
                             "💰 **الكفارة:** فدية أذى\n"
                             "تنبيه: الجاهل والناسي عليه فدية عند الجمهور."
                             )
        return

    elif text == "تغطية الرأس":
        await mistake_detail(update,
                             "**🧢 تغطية الرأس (للرجل)**\n\n"
                             "❌ **الخطأ:** تغطية الرأس (للرجل)\n\n"
                             "⚖️ **الحكم:** محظور إحرام\n"
                             "💰 **الكفارة:** فدية أذى\n"
                             "ملاحظة: المظلة لا تُعد تغطية."
                             )
        return

    elif text == "الطواف بدون وضوء":
        await mistake_detail(update,
                             "**🚿 الطواف بدون وضوء**\n\n"
                             "❌ **الخطأ:** الطواف بدون وضوء\n\n"
                             "⚖️ **الحكم:** الطواف غير صحيح عند جمهور العلماء\n"
                             "ما العمل؟ يجب إعادة الطواف فقط\n"
                             "💰 **كفارة:** لا يوجد"
                             )
        return

    elif text == "نسي شوط":
        await mistake_detail(update,
                             "**🔄 نسي شوط في الطواف أو السعي**\n\n"
                             "❌ **الخطأ:** نسي شوط في الطواف أو السعي\n\n"
                             "⚖️ **الحكم:** إن تذكرت قريبًا أكمل\n"
                             "إن طال الفصل: أعد الطواف\n"
                             "💰 **كفارة:** لا يوجد"
                             )
        return

    elif text == "السعي قبل الطواف":
        await mistake_detail(update,
                             "**🏃 السعي قبل الطواف**\n\n"
                             "❌ **الخطأ:** السعي قبل الطواف\n\n"
                             "⚖️ **الحكم:** السعي غير صحيح\n"
                             "ما العمل؟ أعد السعي بعد الطواف\n"
                             "💰 **كفارة:** لا يوجد"
                             )
        return

    elif text == "ترك واجب":
        await mistake_detail(update,
                             "**⚠️ ترك واجب**\n\n"
                             "❌ **الخطأ:** ترك واجب (مبيت، رمي)\n\n"
                             "⚖️ **الحكم:** النسك صحيح\n"
                             "💰 **الكفارة:** دم (ذبح شاة)\n"
                             "تنبيه: لا صيام بديل"
                             )
        return

    elif text == "الجماع":
        await mistake_detail(update,
                             "**💔 الجماع قبل التحلل الأول**\n\n"
                             "❌ **الخطأ:** الجماع قبل التحلل الأول\n\n"
                             "⚖️ **الحكم:** يفسد النسك\n"
                             "ما يجب:\n"
                             "- إكمال الحج\n"
                             "- القضاء من عام قادم\n"
                             "- ذبح بدنة (جمل)"
                             )
        return

    # ================= أزرار الميقات =================

    elif text == "الشام (سوريا، لبنان، الأردن، فلسطين)":
        await miqat_sham(update, context)
        return
    
    elif text == "رجوع" or text == "رجوع للقائمة الرئيسية":
        await start(update, context)
        return
    
    elif text == "مصر وشمال أفريقيا":
        await miqat_egypt(update, context)
        return

    elif text == "اليمن":
        await miqat_yemen(update, context)
        return
        
    elif text == "الخليج العربي":
        await miqat_saudi(update, context)
        return
        
    elif text == "أمريكا وأوروبا":
        await miqat_america(update, context)
        return
        
    elif text == "آسيا":
        await miqat_asia(update, context)
        return

    # ================= معالجة النصوص =================
    
    intent = process_text(text)

    # ================= معالجة الميقات =================
    if intent == "miqat_sham":
        await miqat_sham(update, context)
    elif intent == "miqat_egypt":
        await miqat_egypt(update, context)
    elif intent == "miqat_yemen":
        await miqat_yemen(update, context)
    elif intent == "miqat_saudi":
        await miqat_saudi(update, context)
    elif intent == "miqat_america":
        await miqat_america(update, context)
    elif intent == "miqat_asia":
        await miqat_asia(update, context)
    elif intent == "miqat_general":
        await miqat_general(update, context)
    elif intent == "miqat_menu":
        menu_text = (
            "**🌍 اختر منطقتك أو اكتب اسم بلدك:**\n\n"
            "**🇸🇾 بلاد الشام:**\n"
            "• سوريا، لبنان، الأردن، فلسطين\n\n"
            "**🇪🇬 مصر وشمال أفريقيا:**\n"
            "• مصر، ليبيا، تونس، الجزائر، المغرب، السودان\n\n"
            "**🇾🇪 اليمن:**\n"
            "• اليمن، حضرموت\n\n"
            "**🇸🇦 الخليج العربي:**\n"
            "• السعودية، الإمارات، قطر، الكويت، البحرين، عُمان\n\n"
            "**🇺🇸 أمريكا وأوروبا:**\n"
            "• أمريكا، كندا، بريطانيا، فرنسا، ألمانيا\n\n"
            "**🇮🇳 آسيا:**\n"
            "• الهند، باكستان، إندونيسيا، ماليزيا\n\n"
            "**💡 اكتب مباشرة مثل:**\n"
            "• 'مصر' أو 'أحرم من مصر'\n"
            "• 'سوريا' أو 'لبنان'\n"
            "• 'أمريكا' أو 'الهند'\n"
            "• 'الإمارات' أو 'السعودية'"
        )
        await update.message.reply_text(menu_text, reply_markup=markup_back, parse_mode='Markdown')

    # ================= معالجة باقي النوايا =================
    elif intent == "hajj":
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
    elif intent == "dua_general":
        await dua_general(update, context)
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
    elif intent == "map_current":
        await update.message.reply_text(
            "📍 **يرجى الضغط على زر 'إرسال موقعي' للحصول على موقعك:**",
            reply_markup=location_keyboard,
            parse_mode='Markdown'
        )
    elif intent == "back":
        await start(update, context)
    elif intent == "start":
        await start(update, context)

    # الرد على النصوص غير المعروفة
    elif intent == "unknown":
        await update.message.reply_text(
            "🤔 لم أفهم سؤالك.\n\n"
            "*للميقات، اكتب:*\n"
            "• 'مصر' أو 'سوريا' أو 'السعودية'\n"
            "• 'أمريكا' أو 'الهند' أو 'بريطانيا'\n"
            "• 'أحرم من المغرب' أو 'ميقات اليمن'\n\n"
            "*أو اكتب:*\n"
            "• 'عمرة' أو 'حج'\n"
            "• 'دعاء طواف'\n"
            "• 'خريطة الحرم'\n\n"
            "أو استخدم الأزرار في الأسفل 👇",
            reply_markup=markup_main,
            parse_mode='Markdown'
        )
#**************++++++++++++++****************
    elif intent == "mistake_clothes":
        await mistake_detail(update,
                             "**👕 لبس المخيط (للرجل)**\n\n"
                             "❌ **الخطأ:** لبس المخيط، لبس ملابس، ارتداء ثياب\n"
                             "⚖️ **الحكم:** محظور إحرام\n💰 **الكفارة:** فدية أذى\n\n"
                             "**ماذا تفعل؟**\n1. اخلعه فوراً\n2. ادفع الفدية\n3. استمر في مناسكك"
                             )
    elif intent == "mistake_perfume":
        await mistake_detail(update,
                             "**🌹 التطيب بعد الإحرام**\n\n"
                             "❌ **الخطأ:** استعمال الطيب أو العطر بعد الإحرام\n\n"
                             "⚖️ **الحكم:** محظور إحرام\n\n"
                             "💰 **الكفارة:** فدية أذى"
                             )

    elif intent == "mistake_hair_nails":
        await mistake_detail(update,
                             "**💇 قص الشعر أو الأظافر**\n\n"
                             "❌ **الخطأ:** قص الشعر أو الأظافر\n\n"
                             "⚖️ **الحكم:** محظور إحرام\n"
                             "💰 **الكفارة:** فدية أذى\n"
                             "تنبيه: الجاهل والناسي عليه فدية عند الجمهور."
                             )

    elif intent == "mistake_cover_head":
        await mistake_detail(update,
            "⚠️ تغطية الرأس للرجل\n\n"
            "لا يجوز للرجل المحرم تغطية رأسه بغطاء ملاصق.\n"
            "🔹 الحكم: فدية.\n"
            "🔹 المرأة يجب عليها تغطية رأسها لكن لا تلبس النقاب."
        )

    elif intent == "mistake_tawaf_no_wudu":
        await mistake_detail(update,
            "⚠️ الطواف بدون وضوء\n\n"
            "يشترط الوضوء لصحة الطواف عند جمهور العلماء.\n"
            "🔹 يجب إعادة الطواف.\n"
            "🔹 لا تجب فدية إذا أعاد الطواف."
        )

    elif intent == "mistake_miss_shawt":
        await mistake_detail(update,
            "⚠️ نسيان شوط في الطواف أو السعي\n\n"
            "إذا نسي شوطًا يجب إكماله متى تذكر.\n"
            "🔹 إن طال الفصل يعيد الطواف أو السعي كاملًا.\n"
            "🔹 لا فدية إذا تم التصحيح."
        )

    elif intent == "mistake_saee_before_tawaf":
        await mistake_detail(update,
            "⚠️ السعي قبل الطواف\n\n"
            "الترتيب الصحيح: الطواف أولًا ثم السعي.\n"
            "🔹 إذا سعى قبل الطواف فعليه إعادة السعي بعد الطواف.\n"
            "🔹 لا فدية عند التصحيح."
        )

    elif intent == "mistake_leave_wajib":
        await mistake_detail(update,
            "⚠️ ترك واجب من واجبات الحج\n\n"
            "مثل ترك المبيت بمزدلفة أو رمي الجمرات.\n"
            "🔹 الحكم: دم (ذبح شاة توزع على فقراء الحرم).\n"
            "🔹 لا يسقط الواجب إلا بعذر شرعي."
        )

    elif intent == "mistake_intercourse":
        await mistake_detail(update,
            "⚠️ الجماع قبل التحلل الأول\n\n"
            "من أعظم محظورات الإحرام.\n"
            "🔹 يفسد الحج إن كان قبل التحلل الأول.\n"
            "🔹 يجب إكمال الحج والقضاء في العام القادم + ذبح بدنة."
        )
# ================= تشغيل البوت =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.add_handler(MessageHandler(filters.LOCATION, send_current_location))

    print("🤖 البوت يعمل الآن مع معالجة متقدمة للغة العربية...")
    print("✨ يدعم الآن جميع بلدان العالم للميقات!")
    app.run_polling()

if __name__ == "__main__":
    main()
