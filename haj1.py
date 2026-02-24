# -*- coding: utf-8 -*- **
import os       # للوصول للمتغيرات البيئية
import sys      # لاستخدام sys.exit
import math     # لحساب المسافات
import requests
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
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

map_menu = [
    ["المسجد الحرام"],
    ["الصفا", "المروة"],
    ["موقعي الحالي"],
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

        'امارات': 'miqat_uae', 'الامارات': 'miqat_uae', 'دبي': 'miqat_uae',
        'ابوظبي': 'miqat_uae', 'عجمان': 'miqat_uae', 'الشارقة': 'miqat_uae',

        'قطر': 'miqat_qatar', 'قطري': 'miqat_qatar', 'الدوحة': 'miqat_qatar',

        'كويت': 'miqat_kuwait', 'الكويت': 'miqat_kuwait', 'كويتي': 'miqat_kuwait',

        'بحرين': 'miqat_bahrain', 'البحرين': 'miqat_bahrain', 'المنامة': 'miqat_bahrain',

        'عمان': 'miqat_oman', 'سلطنة عمان': 'miqat_oman', 'مسقط': 'miqat_oman'
    }

    # بلدان أخرى
    other_countries = {
        'تركيا': 'miqat_turkey', 'تركي': 'miqat_turkey', 'استانبول': 'miqat_turkey',
        'انقرة': 'miqat_turkey', 'أنقرة': 'miqat_turkey',

        'ايران': 'miqat_iran', 'ايراني': 'miqat_iran', 'طهران': 'miqat_iran',

        'افغانستان': 'miqat_afghanistan', 'افغاني': 'miqat_afghanistan',
        'كابل': 'miqat_afghanistan',

        'باكستان': 'miqat_pakistan', 'باكستاني': 'miqat_pakistan',
        'اسلام اباد': 'miqat_pakistan', 'كراتشي': 'miqat_pakistan',

        'الهند': 'miqat_india', 'هندي': 'miqat_india', 'نيودلهي': 'miqat_india',
        'مومباي': 'miqat_india',

        'اندونيسيا': 'miqat_indonesia', 'اندونيسي': 'miqat_indonesia',
        'جاكرتا': 'miqat_indonesia',

        'ماليزيا': 'miqat_malaysia', 'ماليزي': 'miqat_malaysia',
        'كوالالمبور': 'miqat_malaysia',

        'امريكا': 'miqat_america', 'الولايات المتحدة': 'miqat_america',
        'امريكي': 'miqat_america', 'نيويورك': 'miqat_america',
        'واشنطن': 'miqat_america',

        'كندا': 'miqat_canada', 'كندي': 'miqat_canada', 'تورنتو': 'miqat_canada',
        'فانكوفر': 'miqat_canada',

        'بريطانيا': 'miqat_uk', 'المملكة المتحدة': 'miqat_uk',
        'انجلترا': 'miqat_uk', 'لندن': 'miqat_uk',

        'فرنسا': 'miqat_france', 'فرنسي': 'miqat_france', 'باريس': 'miqat_france',

        'المانيا': 'miqat_germany', 'الماني': 'miqat_germany', 'برلين': 'miqat_germany',

        'ايطاليا': 'miqat_italy', 'ايطالي': 'miqat_italy', 'روما': 'miqat_italy',

        'استراليا': 'miqat_australia', 'استرالي': 'miqat_australia',
        'سيدني': 'miqat_australia', 'ملبورن': 'miqat_australia',

        'اليابان': 'miqat_japan', 'ياباني': 'miqat_japan', 'طوكيو': 'miqat_japan',

        'كوريا': 'miqat_korea', 'كوري': 'miqat_korea', 'سيول': 'miqat_korea',

        'الصين': 'miqat_china', 'صيني': 'miqat_china', 'بكين': 'miqat_china',

        'روسيا': 'miqat_russia', 'روسي': 'miqat_russia', 'موسكو': 'miqat_russia',

        'البرازيل': 'miqat_brazil', 'برازيلي': 'miqat_brazil',
        'ريو دي جانيرو': 'miqat_brazil',

        'اريتريا': 'miqat_eritrea', 'اريتري': 'miqat_eritrea',
        'اثيوبيا': 'miqat_ethiopia', 'اثيوبي': 'miqat_ethiopia',
        'الصومال': 'miqat_somalia', 'صومالي': 'miqat_somalia',
        'جيبوتي': 'miqat_djibouti', 'جيبوتي': 'miqat_djibouti',

        'نيجيريا': 'miqat_nigeria', 'نيجيري': 'miqat_nigeria',
        'جنوب افريقيا': 'miqat_south_africa', 'جنوب افريقي': 'miqat_south_africa',

        'المكسيك': 'miqat_mexico', 'مكسيكي': 'miqat_mexico',
        'الارجنتين': 'miqat_argentina', 'ارجنتيني': 'miqat_argentina'
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
async def mistakes_menu_show(update, context):
    await update.message.reply_text(
        "اختر الخطأ الذي وقعت فيه:",
        reply_markup=markup_mistakes
    )


async def mistake_detail(update, text):
    await update.message.reply_text(text, reply_markup=markup_mistakes)
    
    
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
    # ================= الأدعية =================
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
        "اكتب موقع مع المكان الذي تريده:\n"
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
    """ميقات أمريكا وكندا"""
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
    elif intent in ["miqat_uae", "miqat_qatar", "miqat_kuwait", "miqat_bahrain", "miqat_oman"]:
        await miqat_saudi(update, context)  # كل الخليج نفس الميقات

    # الدول الأخرى
    elif intent in ["miqat_america", "miqat_canada", "miqat_uk", "miqat_france",
                    "miqat_germany", "miqat_italy", "miqat_australia"]:
        await miqat_america(update, context)

    elif intent in ["miqat_india", "miqat_pakistan", "miqat_indonesia",
                    "miqat_malaysia", "miqat_afghanistan", "miqat_bangladesh",
                    "miqat_china", "miqat_japan", "miqat_korea"]:
        await miqat_asia(update, context)

    elif intent in ["miqat_turkey", "miqat_iran", "miqat_russia", "miqat_brazil",
                    "miqat_argentina", "miqat_mexico", "miqat_ethiopia",
                    "miqat_somalia", "miqat_nigeria", "miqat_south_africa"]:
        await miqat_general(update, context)

    elif intent == "miqat_menu":
        # عرض قائمة بالمقاطات الرئيسية
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

    # الأدعية
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

    # الأخطاء
    elif intent == "mistakes_menu":
        await mistakes_menu_show(update, context)
    elif intent == "mistake_clothes":
        await mistake_detail(update,
                             "**👕 لبس المخيط (للرجل)**\n\n"
                             "❌ **جميع الصيغ:** لبس مخيط، لبس ملابس، ارتداء ثياب\n"
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

    # المواقع
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

    # الأزرار الأساسية
    elif text == "رجوع للقائمة الرئيسية" or intent == "back":
        await start(update, context)
    elif text == "الأدعية":
        await duas_menu(update, context)
    elif text == "الأخطاء والكفارات":
        await mistakes_menu_show(update, context)
    elif text == "الخريطة":
        await map_menu_show(update, context)
    elif text == "ميقات الإحرام":
        await update.message.reply_text(
            "**🌍 ميقات الإحرام للبلدان المختلفة**\n\n"
            "اكتب اسم بلدك مثل:\n"
            "• 'مصر' أو 'المغرب' أو 'الجزائر'\n"
            "• 'سوريا' أو 'لبنان' أو 'فلسطين'\n"
            "• 'السعودية' أو 'الإمارات' أو 'قطر'\n"
            "• 'أمريكا' أو 'كندا' أو 'بريطانيا'\n"
            "• 'الهند' أو 'باكستان' أو 'إندونيسيا'\n\n"
            "أو اختر من القائمة",
            reply_markup=markup_back,
            parse_mode='Markdown'
        )

    # معالجة موقع المستخدم
    elif update.message.location:
        await send_current_location(update, context)

    elif intent == "dua_menu":
        await duas_menu(update, context)

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
    elif intent == "start":
        await start(update, context)
# ================= دعم جميع الأزرار =================

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
    elif text == "التطيب بعد الإحرام":
        await mistake_detail(update,
                             "الخطأ: استعمال الطيب بعد الإحرام\n\n"
                             "الحكم: محظور إحرام\n"
                             "الكفارة: فدية أذى\n"
                             "تنبيه: الطيب قبل الإحرام جائز."
                             )

    elif text == "قص الشعر أو الأظافر":
        await mistake_detail(update,
                             "الخطأ: قص الشعر أو الأظافر\n\n"
                             "الحكم: محظور إحرام\n"
                             "الكفارة: فدية أذى\n"
                             "تنبيه: الجاهل والناسي عليه فدية عند الجمهور."
                             )

    elif text == "تغطية الرأس":
        await mistake_detail(update,
                             "الخطأ: تغطية الرأس (للرجل)\n\n"
                             "الحكم: محظور إحرام\n"
                             "الكفارة: فدية أذى\n"
                             "ملاحظة: المظلة لا تُعد تغطية."
                             )

    elif text == "الطواف بدون وضوء":
        await mistake_detail(update,
                             "الخطأ: الطواف بدون وضوء\n\n"
                             "الحكم: الطواف غير صحيح عند جمهور العلماء\n"
                             "ما العمل؟ يجب إعادة الطواف فقط\n"
                             "كفارة: لا يوجد"
                             )

    elif text == "نسي شوط":
        await mistake_detail(update,
                             "الخطأ: نسي شوط في الطواف أو السعي\n\n"
                             "الحكم: إن تذكرت قريبًا أكمل\n"
                             "إن طال الفصل: أعد الطواف\n"
                             "كفارة: لا يوجد"
                             )
    elif text == "لبس المخيط":
        await mistake_detail(update,
                             "الخطأ: لبس المخيط (للرجل)\n\n"
                             "الحكم: محظور إحرام ولا يبطل النسك\n"
                             "الكفارة: فدية أذى (اختيار واحد)\n"
                             "- ذبح شاة\n- أو إطعام 6 مساكين\n- أو صيام 3 أيام\n\n"
                             "ماذا تفعل؟ اخلعه فورًا وادفع الفدية."
                             )
    elif text == "السعي قبل الطواف":
        await mistake_detail(update,
                             "الخطأ: السعي قبل الطواف\n\n"
                             "الحكم: السعي غير صحيح\n"
                             "ما العمل؟ أعد السعي بعد الطواف\n"
                             "كفارة: لا يوجد"
                             )

    elif text == "ترك واجب":
        await mistake_detail(update,
                             "الخطأ: ترك واجب (مبيت، رمي)\n\n"
                             "الحكم: النسك صحيح\n"
                             "الكفارة: دم (ذبح شاة)\n"
                             "تنبيه: لا صيام بديل"
                             )

    elif text == "الجماع":
        await mistake_detail(update,
                             "الخطأ: الجماع قبل التحلل الأول\n\n"
                             "الحكم: يفسد النسك\n"
                             "ما يجب:\n"
                             "- إكمال الحج\n"
                             "- القضاء من عام قادم\n"
                             "- ذبح بدنة (جمل)"
                             )
  
    # ================= أزرار الأخطاء =================

    elif text == "لبس المخيط":
        await mistake_detail(update, "👕 لبس المخيط محظور... (نفس النص عندك)")
        return

    elif text == "التطيب بعد الإحرام":
        await mistake_detail(update, "🌹 التطيب بعد الإحرام محظور... (نفس النص)")
        return

    # ================= أزرار الميقات =================

    elif text == "الشام (سوريا، لبنان، الأردن، فلسطين)":
        await miqat_sham(update, context)
        return
    
    elif text =="رجوع":
        await start(update, context)
    elif text == "مصر وشمال أفريقيا":
        await miqat_egypt(update, context)
        return

    elif text == "اليمن":
        await miqat_yemen(update, context)
        return

# ================= الدالة الرئيسية =================


 def main():
    print("🚀 بدء تشغيل البوت...")
    print(f"🐍 Python version: {sys.version}")

    PORT = int(os.environ.get("PORT", 5000))

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"https://haj-bot.onrender.com/{TOKEN}"
    )


if __name__ == "__main__":
    main()

