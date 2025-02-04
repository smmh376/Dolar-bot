import requests
import re
import time

# تنظیمات
URL = "https://fa.navasan.net/dayRates.php?item=usd"
BOT_TOKEN = "8140868224:AAGl-Oe__eQjEJ1q8cC4jf9-oJTo5LRxDLA"
CHAT_ID = "-1002484852011"

# متغیر برای ذخیره آخرین قیمت
previous_price = None

def fetch_dollar_price():
    """
    دریافت قیمت دلار از سایت navasan.net
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept-Language": "fa-IR,fa;q=0.9"
        }

        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()

        html_text = response.text

        # جستجوی اولین عدد ۵ رقمی در محدوده ۷۵۰۰۰ تا ۹۱۰۰۰
        match = re.search(r'\b(7[5-9]\d{3}|8\d{4}|9[0-1]\d{3})\b', html_text)
        
        if match:
            return int(match.group(0))  # مقدار قیمت را به عدد صحیح تبدیل می‌کند
        return None

    except Exception as e:
        print(f"⚠ خطا در دریافت قیمت: {str(e)}")
        return None

def get_price_change_icon(current_price, previous_price):
    """
    تعیین وضعیت قیمت: افزایش، کاهش یا بدون تغییر
    """
    if previous_price is None:
        return "⚪"  # اولین اجرا
    elif current_price > previous_price:
        return "🟢"  # افزایش قیمت
    elif current_price < previous_price:
        return "🔴"  # کاهش قیمت
    else:
        return "⚪"  # بدون تغییر

def send_text(message):
    """
    ارسال پیام به کانال تلگرام
    """
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("✅ پیام ارسال شد")
        else:
            print("❌ ارسال پیام ناموفق", response.text)
    except Exception as e:
        print(f"⚠ خطا در ارسال پیام: {str(e)}")

# **حلقه مانیتورینگ**
print("🟢 شروع مانیتورینگ لحظه‌ای...")
while True:
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    current_price = fetch_dollar_price()

    if current_price is None:
        price_display = "N/A"
        icon = "⚪"
    else:
        price_display = "{:,}".format(current_price)  # نمایش عدد با جداکننده هزارگان
        icon = get_price_change_icon(current_price, previous_price)
        previous_price = current_price  # ذخیره قیمت برای مقایسه بعدی

    # قالب‌بندی پیام
    message = (
        f"<b>💵 نرخ لحظه‌ای دلار</b>\n\n"
        f"{icon} قیمت: <code>{price_display}</code> تومان\n"
        f"🕒 آخرین بروزرسانی: {current_time}"
    )

    send_text(message)
    time.sleep(180)  # هر ۳ دقیقه یک‌بار بررسی می‌شود
