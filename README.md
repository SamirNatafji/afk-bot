# ECHO BOT - Discord AFK Bot

بوت Discord لنقل المستخدمين إلى قناة AFK بعد فترة عدم النشاط.

## المتطلبات

- Python 3.8+
- Discord.py
- python-dotenv

## التثبيت المحلي

```bash
pip install -r requirements.txt
```

## متغيرات البيئة

أنشئ ملف `.env` وأضف:

```
DISCORD_TOKEN=your_discord_token_here
AFK_CHANNEL_ID=your_channel_id_here
```

## التشغيل

```bash
python main.py
```

## النشر على Railway

### الخطوات:

1. **إنشء حساب على Railway**
   - اذهب إلى https://railway.app
   - سجل الدخول باستخدام GitHub

2. **رفع المشروع على GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/your_username/echo-bot.git
   git push -u origin main
   ```

3. **ربط المشروع مع Railway**
   - انتقل إلى https://railway.app/new
   - اختر "GitHub Repo"
   - حدد المشروع الخاص بك
   - أنقر على "Deploy Now"

4. **إضافة متغيرات البيئة على Railway**
   - في لوحة التحكم، انتقل إلى "Variables"
   - أضف:
     - `DISCORD_TOKEN`: رمز البوت الخاص بك
     - `AFK_CHANNEL_ID`: معرف القناة

5. **تفعيل الخادم**
   - سيبدأ التطبيق تلقائياً بعد الدفع

## الميزات

- نقل تلقائي للمستخدمين إلى قناة AFK بعد 7 دقائق من عدم النشاط
- إرسال رسالة تحية عند النقل
- تشغيل الموسيقى عند النقل
