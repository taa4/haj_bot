# استخدام صورة Python 3.11 المستقرة رسمياً
FROM python:3.11-slim

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات أولاً للاستفادة من خاصية Cache
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملف البوت
COPY bot.py .

# تشغيل البوت (سيتم استبدال هذا الأمر إذا تم تعيين Start Command في Render)
CMD ["python", "bot.py"]
