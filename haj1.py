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

back_menu = [["رجوع للقائمة الرئيسية"]]
location_menu = [
    [KeyboardButton("إرسال موقعي", request_location=True)],
    ["رجوع للقائمة الرئيسية"]
]

markup_main = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
markup_back = ReplyKeyboardMarkup(back_menu, resize_keyboard=True)
markup_location = ReplyKeyboardMarkup(location_menu, resize_keyboard=True)

# ================= دوال المساعدة =================
def normalize_text(text):
    """تقنين النص وإزالة التشكيل والحركات"""
    text = text.strip().lower()
    
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
    """حساب المسافة بين نقطتين بالأمتار"""
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return int(R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))))

# ================= معالج البداية =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب والقائمة الرئيسية"""
    welcome_text = """
🌙 *مرحبا بك في مساعد الحج والعمرة* 🤲

*يمكنك:*
• معرفة مناسك الحج والعمرة
• أدعية مكتوبة لكل منسك
• معلومات عن مواقيت الإحرام حسب بلدك
• تحديد مواقع الأماكن المقدسة
• معرفة كفارات الأخطاء

*اختر من القائمة أدناه:* 👇
"""
    await update.message.reply_text(welcome_text, reply_markup=markup_main, parse_mode='Markdown')

# ================= معالج النصوص الرئيسي =================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة جميع الرسائل النصية"""
    text = update.message.text.strip()
    
    # التعامل مع أزرار القائمة
    if text == "رجوع للقائمة الرئيسية":
        await start(update, context)
        return
        
    normalized_text = normalize_text(text)
    
    # ===== الحج =====
    if "حج" in normalized_text or text == "الحج":
        await show_hajj_info(update, context)
    
    # ===== العمرة =====
    elif "عمره" in normalized_text or "عمرة" in normalized_text or text == "العمرة":
        await show_umrah_info(update, context)
    
    # ===== الأدعية =====
    elif "ادعيه" in normalized_text or "ادعية" in normalized_text or "دعاء" in normalized_text or text == "الأدعية":
        await show_duas_menu(update, context)
    
    # ===== الخريطة =====
    elif "خريطه" in normalized_text or "خارطه" in normalized_text or "خرائط" in normalized_text or "موقع" in normalized_text or text == "الخريطة":
        await show_map_menu(update, context)
    
    # ===== الأخطاء والكفارات =====
    elif "خطا" in normalized_text or "كفاره" in normalized_text or "غلط" in normalized_text or text == "الأخطاء والكفارات":
        await show_mistakes_menu(update, context)
    
    # ===== ميقات الإحرام =====
    elif "ميقات" in normalized_text or "احرام" in normalized_text or text == "ميقات الإحرام":
        await show_miqat_menu(update, context)
    
    # معالجة الكلمات المفتاحية للأدعية
    elif "احرام" in normalized_text and "دعاء" in normalized_text:
        await dua_ihram(update, context)
    elif "طواف" in normalized_text and "دعاء" in normalized_text:
        await dua_tawaf(update, context)
    elif "سعي" in normalized_text and "دعاء" in normalized_text:
        await dua_saee(update, context)
    elif "عرفه" in normalized_text or "عرفة" in normalized_text:
        await dua_arafah(update, context)
    elif "جمرات" in normalized_text or "رمي" in normalized_text:
        await dua_jamarat(update, context)
    
    # معالجة الكلمات المفتاحية للمواقع
    elif "حرم" in normalized_text or "الكعبة" in normalized_text:
        await send_haram_location(update, context)
    elif "صفا" in normalized_text:
        await send_safa_location(update, context)
    elif "مروه" in normalized_text or "مروة" in normalized_text:
        await send_marwah_location(update, context)
    
    # معالجة طلب الموقع الحالي
    elif normalized_text == "موقعي" or "موقعي الحالي" in normalized_text:
        await request_location(update, context)
    
    # معالجة أسماء البلدان للميقات
    elif any(country in normalized_text for country in ['مصر', 'ليبيا', 'تونس', 'جزائر', 'مغرب', 'سودان']):
        await miqat_egypt(update, context)
    elif any(country in normalized_text for country in ['سوريا', 'لبنان', 'اردن', 'فلسطين']):
        await miqat_sham(update, context)
    elif any(country in normalized_text for country in ['يمن', 'صنعاء', 'عدن']):
        await miqat_yemen(update, context)
    elif any(country in normalized_text for country in ['سعوديه', 'امارات', 'قطر', 'كويت', 'بحرين', 'عمان']):
        await miqat_gulf(update, context)
    elif any(country in normalized_text for country in ['امريكا', 'كندا', 'بريطانيا', 'فرنسا', 'المانيا']):
        await miqat_west(update, context)
    elif any(country in normalized_text for country in ['هند', 'باكستان', 'اندونيسيا', 'ماليزيا']):
        await miqat_asia(update, context)
    
    else:
        # رسالة افتراضية إذا لم يتم التعرف على الطلب
        await update.message.reply_text(
            "🤔 لم أفهم طلبك.\n\n"
            "*يمكنك:*\n"
            "• اختيار أحد الأزرار في الأسفل\n"
            "• كتابة اسم بلدك لمعرفة ميقات الإحرام\n"
            "• كتابة 'حج' أو 'عمرة' للمناسك\n"
            "• كتابة 'دعاء' للأدعية\n"
            "• كتابة 'خريطة' للمواقع",
            reply_markup=markup_main,
            parse_mode='Markdown'
        )

# ================= دوال الحج والعمرة =================
async def show_hajj_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض معلومات الحج"""
    text = """🕋 *معلومات شاملة عن الحج*

*أركان الحج:*
1️⃣ الإحرام: النية والدخول في النسك
2️⃣ الوقوف بعرفة
3️⃣ طواف الإفاضة
4️⃣ السعي بين الصفا والمروة

*واجبات الحج:*
• الإحرام من الميقات
• المبيت بمزدلفة
• المبيت بمنى
• رمي الجمرات
• الحلق أو التقصير
• طواف الوداع

*أيام الحج:*
📅 8 ذو الحجة: يوم التروية (المبيت في منى)
📅 9 ذو الحجة: يوم عرفة (الوقوف بعرفة)
📅 10-13 ذو الحجة: أيام التشريق (رمي الجمرات)"""
    
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')

async def show_umrah_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض معلومات العمرة"""
    text = """🕋 *معلومات شاملة عن العمرة*

*خطوات العمرة:*
1️⃣ **الإحرام من الميقات**
   - النية: "اللهم إني أريد العمرة"
   - التلبية: "لبيك اللهم عمرة"

2️⃣ **الطواف (7 أشواط)**
   - يبدأ من الحجر الأسود
   - يكون الكعبة على اليسار

3️⃣ **صلاة ركعتين** خلف مقام إبراهيم

4️⃣ **السعي (7 أشواط)** بين الصفا والمروة

5️⃣ **الحلق أو التقصير**
   - الرجال: الحلق أفضل
   - النساء: تقصر قدر أنملة

*ملاحظة:* العمرة جائزة في أي وقت من السنة"""
    
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')

# ================= دوال الأدعية =================
async def show_duas_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة الأدعية"""
    text = """📿 *أدعية الحج والعمرة*

اختر نوع الدعاء:
• دعاء الإحرام
• دعاء الطواف
• دعاء السعي
• دعاء عرفة
• دعاء رمي الجمرات

*اكتب ما تريد مثلاً:* "دعاء الطواف" """
    
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')

async def dua_ihram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """📿 *أدعية الإحرام*

*عقد النية:*
"اللهم إني نويت العمرة/الحج فيسره لي وتقبله مني"

*الدعاء المأثور:*
"اللهم إني أسألك رضاك والجنة، وأعوذ بك من سخطك والنار"

*التلبية:*
"لبيك اللهم لبيك، لبيك لا شريك لك لبيك، إن الحمد والنعمة لك والملك، لا شريك لك"

*عند دخول المسجد الحرام:*
"اللهم افتح لي أبواب رحمتك" """
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def dua_tawaf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """📿 *أدعية الطواف*

*عند بداية كل شوط:*
"بسم الله والله أكبر"

*بين الركن اليماني والحجر الأسود:*
"ربنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار"

*دعاء عام في الطواف:*
"اللهم اغفر وارحم واعف عما تعلم، إنك أنت الأعز الأكرم"

*عند شرب ماء زمزم:*
"اللهم إني أسألك علماً نافعاً، ورزقاً واسعاً، وشفاء من كل داء" """
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def dua_saee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """📿 *أدعية السعي*

*عند الصعود على الصفا:*
"إِنَّ الصَّفَا وَالْمَرْوَةَ مِن شَعَائِرِ اللَّهِ، أبدأ بما بدأ الله به"

*أثناء السعي:*
"رب اغفر وارحم وتجاوز عما تعلم، إنك أنت الأعز الأكرم"

*بين العلمين الأخضرين (للرجال):*
"رب اغفر وارحم، واهدني السبيل الأقوم"

*عند المروة:*
"اللهم اجعلني من المقبولين، واغفر لي ولوالدي وللمؤمنين" """
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def dua_arafah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """📿 *أدعية يوم عرفة*

*أفضل الدعاء يوم عرفة:*
"لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير"

*دعاء النبي ﷺ بعرفة:*
"اللهم لك الحمد كالذي نقول وخيراً مما نقول، اللهم لك صلاتي ونسكي ومحياي ومماتي، وإليك مآبي"

*دعاء عام:*
"اللهم اغفر لي ولوالدي وللمؤمنين والمؤمنات الأحياء منهم والأموات"

*الدعاء الشامل:*
"اللهم إني أسألك من الخير كله عاجله وآجله، ما علمت منه وما لم أعلم" """
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def dua_jamarat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """📿 *أدعية رمي الجمرات*

*عند رمي كل جمرة:*
"الله أكبر" (مع كل حصاة)

*بعد رمي الجمرة الصغرى:*
يتقدم قليلاً ويدعو الله مستقبل القبلة

*بعد رمي الجمرة الوسطى:*
يتقدم ويدعو الله طويلاً

*عند رمي جمرة العقبة:*
يكبر مع كل حصاة ولا يقف للدعاء

*دعاء عام:*
"اللهم اجعله حجاً مبروراً وسعياً مشكوراً وذنباً مغفوراً" """
    
    await update.message.reply_text(text, parse_mode='Markdown')

# ================= دوال المواقع =================
async def show_map_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة المواقع"""
    text = """🗺 *المواقع المقدسة*

اختر الموقع:
• المسجد الحرام
• جبل الصفا
• جبل المروة
• موقعي الحالي

*اكتب ما تريد مثلاً:* "موقع الحرم" """
    
    await update.message.reply_text(text, reply_markup=markup_location, parse_mode='Markdown')

async def request_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طلب موقع المستخدم"""
    await update.message.reply_text(
        "📍 **يرجى الضغط على زر 'إرسال موقعي'**",
        reply_markup=markup_location,
        parse_mode='Markdown'
    )

async def send_haram_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال موقع المسجد الحرام"""
    await update.message.reply_location(latitude=21.4225, longitude=39.8262)
    await update.message.reply_text(
        """📍 **المسجد الحرام**
مكة المكرمة

*أهم المعالم:*
• الكعبة المشرفة
• الحجر الأسود
• مقام إبراهيم
• بئر زمزم
• الصفا والمروة

💡 *الموقع: قلب مكة المكرمة""",
        parse_mode='Markdown'
    )

async def send_safa_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال موقع الصفا"""
    await update.message.reply_location(latitude=21.4229, longitude=39.8257)
    await update.message.reply_text(
        """📍 **جبل الصفا**
يبدأ منه السعي

💡 *يُقرأ عند الصعود:*
"إِنَّ الصَّفَا وَالْمَرْوَةَ مِن شَعَائِرِ اللَّهِ" """,
        parse_mode='Markdown'
    )

async def send_marwah_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال موقع المروة"""
    await update.message.reply_location(latitude=21.4237, longitude=39.8267)
    await update.message.reply_text(
        """📍 **جبل المروة**
ينتهي إليه السعي

💡 *عند الوصول:*
يُسن الدعاء والذكر""",
        parse_mode='Markdown'
    )

# ================= دوال الأخطاء والكفارات =================
async def show_mistakes_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة الأخطاء والكفارات"""
    text = """⚠️ *الأخطاء الشائعة وكفاراتها*

*محظورات الإحرام:*
1️⃣ لبس المخيط (للرجال) - فدية
2️⃣ التطيب - فدية
3️⃣ قص الشعر أو الأظافر - فدية
4️⃣ تغطية الرأس (للرجال) - فدية
5️⃣ قتل الصيد - جزاء

*كفارة المحظور:*
• ذبح شاة
• أو إطعام 6 مساكين
• أو صيام 3 أيام

*ملاحظة:* من ترك واجباً فعليه دم (شاة)"""
    
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')

# ================= دوال مواقيت الإحرام =================
async def show_miqat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة مواقيت الإحرام"""
    text = """🌍 *مواقيت الإحرام حسب البلد*

*اكتب اسم بلدك:*

🇸🇾 **بلاد الشام:**
سوريا، لبنان، الأردن، فلسطين

🇪🇬 **مصر وشمال أفريقيا:**
مصر، ليبيا، تونس، الجزائر، المغرب، السودان

🇾🇪 **اليمن:**
اليمن

🇸🇦 **الخليج العربي:**
السعودية، الإمارات، قطر، الكويت، البحرين، عُمان

🌎 **أمريكا وأوروبا:**
أمريكا، كندا، بريطانيا، فرنسا، ألمانيا

🌏 **آسيا:**
الهند، باكستان، إندونيسيا، ماليزيا

*أو اكتب مباشرة:* "مصر" أو "سوريا" أو "السعودية" """
    
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')

async def miqat_egypt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ميقات مصر وشمال أفريقيا"""
    text = """🇪🇬 *ميقات مصر وشمال أفريقيا*
(مصر، ليبيا، تونس، الجزائر، المغرب، السودان)

📍 **الميقات:** الجحفة (رابغ)
📏 **المسافة:** ~180 كم من مكة

✈️ **للحجاج الجويين:**
• الإحرام في الطائرة قبل الوصول لجدة
• وقت الإحرام: قبل الهبوط بساعة

🚗 **للحجاج البريين:**
• الإحرام من الجحفة

💡 *تنبيه:* لا يجوز تجاوز الميقات بدون إحرام"""
    
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=26.3294, longitude=35.3123)

async def miqat_sham(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ميقات بلاد الشام"""
    text = """🇸🇾 *ميقات بلاد الشام*
(سوريا، لبنان، الأردن، فلسطين)

📍 **الميقات:** ذو الحليفة (أبيار علي)
📏 **المسافة:** ~450 كم من مكة

🏕 **الموقع:** شمال غرب المدينة المنورة

💡 *ملاحظات:*
• الميقات حدودي
• لا تجاوزه بدون إحرام
• يستحب الإحرام قبله"""
    
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=24.9167, longitude=39.6167)

async def miqat_yemen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ميقات اليمن"""
    text = """🇾🇪 *ميقات اليمن*

📍 **الميقات:** يَلَمْلم
📏 **المسافة:** ~100 كم من مكة

🏔 **الموقع:** جنوب مكة

✈️ **للحجاج الجويين:**
• الإحرام قبل الوصول لجدة

💡 *خاص بأهل اليمن ومن جاء من جهتهم"""
    
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=21.4167, longitude=40.6000)

async def miqat_gulf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ميقات دول الخليج"""
    text = """🇸🇦 *ميقات الخليج العربي*
(السعودية، الإمارات، قطر، الكويت، البحرين، عُمان)

📍 **الميقات:** قرن المنازل (السيل الكبير)
📏 **المسافة:** ~75 كم من مكة

🏠 **لأهل مكة:** يحرمون من بيوتهم
🏠 **لأهل المدينة:** ذو الحليفة
🏠 **لأهل الطائف:** قرن المنازل أو يلملم

💡 *القادمون من الخليج:*
• ميقاتهم قرن المنازل
• يحرمون عند الوصول إليه"""
    
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')
    await update.message.reply_location(latitude=21.3500, longitude=40.2000)

async def miqat_west(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ميقات الدول الغربية"""
    text = """🌎 *ميقات أمريكا وأوروبا*
(أمريكا، كندا، بريطانيا، فرنسا، ألمانيا)

✈️ **للحجاج الجويين:**
• الإحرام في الطائرة قبل الوصول للسعودية
• وقت الإحرام: قبل الهبوط بساعة

🏨 **إذا هبطت في جدة:**
• تحرم في المطار أو قبله

🏨 **إذا هبطت في المدينة:**
• تذهب إلى ذي الحليفة للإحرام

💡 *نصائح:*
• جهز ملابس الإحرام في حقيبة اليد
• استشر شركة الطيران عن وقت الإحرام"""
    
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')

async def miqat_asia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ميقات دول آسيا"""
    text = """🌏 *ميقات آسيا*
(الهند، باكستان، إندونيسيا، ماليزيا)

✈️ **للحجاج الجويين:**
• الإحرام في الطائرة
• وقت الإحرام: قبل الوصول بساعتين

🚢 **للحجاج البحريين:**
• ميقاتهم يلملم
• يحرمون عند محاذاة الميقات

💡 *تنبيه:*
• استعلم من مكتب الحج في بلدك
• شركات الطيران تنبه عادة لوقت الإحرام"""
    
    await update.message.reply_text(text, reply_markup=markup_back, parse_mode='Markdown')

# ================= معالج الموقع الجغرافي =================
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الموقع المرسل من المستخدم"""
    if update.message.location:
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        
        # حساب المسافة من الحرم
        distance = calculate_distance(lat, lon, 21.4225, 39.8262)
        
        await update.message.reply_text(
            f"📍 **موقعك الحالي:**\n"
            f"• خط العرض: {lat:.4f}\n"
            f"• خط الطول: {lon:.4f}\n\n"
            f"📏 **المسافة من الحرم:** {distance:,} متر\n\n"
            f"💡 *إذا كنت في مكة، يمكنك الإحرام من مكانك*",
            reply_markup=markup_main,
            parse_mode='Markdown'
        )

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
