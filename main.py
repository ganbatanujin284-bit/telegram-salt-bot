from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import qrcode
from io import BytesIO
import requests

# === Эдгээрийг ӨӨРИЙНХӨӨРӨӨ солиорой ===
TOKEN = "8449746552:AAGEgAhr7fJE-Scqijs4tovIpqo-vQtRGzQ"
BTC_ADDRESS = "bc1qhs90rgayvff7h50fcmwmlkgk9sdxq58m6pzthd"

# Давсны үнэ (USD)
PRICES_USD = {
    "Давс 1 – $150": 150,
    "Давс 2 – $230": 230,
    "Давс 3 – $350": 350,
}

# ---------------- Туслах товчлуурууд ----------------
def kb_city():
    return ReplyKeyboardMarkup(
        [["Улаанбаатар"], ["🔁 Цэс шинэчлэх"]],
        one_time_keyboard=True, resize_keyboard=True
    )

def kb_products():
    rows = [[k] for k in PRICES_USD.keys()]
    rows.append(["↩ Буцах", "🔁 Цэс шинэчлэх"])
    return ReplyKeyboardMarkup(rows, one_time_keyboard=True, resize_keyboard=True)

def show_main_menu(update: Update, text="Хот сонгоно уу 👇"):
    update.message.reply_text(text, reply_markup=kb_city())

# ---------------- BTC ханш авах ----------------
def get_btc_price_usd() -> float:
    """
    Coindesk API-гаас BTC/USD ханш авах.
    Алдаа гарвал 0 буцаана.
    """
    try:
        r = requests.get("https://api.coindesk.com/v1/bpi/currentprice/USD.json", timeout=10)
        r.raise_for_status()
        data = r.json()
        return float(data["bpi"]["USD"]["rate_float"])
    except Exception:
        return 0.0

# ---------------- Командууд ----------------
def start(update: Update, context: CallbackContext):
    context.user_data.clear()
    show_main_menu(update, "Сайн уу! Гол цэс 👇")

def help_cmd(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🧭 Тусламж:\n"
        "- /menu: Гол цэс рүү буцах\n"
        "- /pay: BTC хаягийг дахин харах\n"
        "- /paid: Төлбөр хийснээ мэдэгдэх\n"
    )

def menu_cmd(update: Update, context: CallbackContext):
    context.user_data.clear()
    show_main_menu(update, "Гол цэсийг дахин ачааллав ✅")

def pay_cmd(update: Update, context: CallbackContext):
    update.message.reply_text(f"💳 BTC: {BTC_ADDRESS}")

def paid_cmd(update: Update, context: CallbackContext):
    update.message.reply_text("Баярлалаа! Төлбөр шалгаж байна. 👌")

# ---------------- Урсгал ----------------
def handle_city(update: Update, context: CallbackContext):
    city = update.message.text
    if city == "🔁 Цэс шинэчлэх":
        return menu_cmd(update, context)

    context.user_data["city"] = city
    update.message.reply_text(
        f"Хот: {city}\nБараагаа сонгоно уу 👇", reply_markup=kb_products()
    )

def handle_back_or_refresh(update: Update, context: CallbackContext):
    txt = update.message.text
    if txt == "↩ Буцах":
        context.user_data.pop("city", None)
        show_main_menu(update, "Хотыг дахин сонгоно уу 👇")
    elif txt == "🔁 Цэс шинэчлэх":
        menu_cmd(update, context)

def show_payment(update: Update, context: CallbackContext):
    choice = update.message.text
    if choice not in PRICES_USD:
        return  # бусад handler барина

    usd_amount = PRICES_USD[choice]
    btc_price = get_btc_price_usd()

    if btc_price <= 0:
        update.message.reply_text(
            "⚠️ BTC ханш авахад алдаа гарлаа. Дахин оролдоно уу /menu",
            reply_markup=kb_products()
        )
        return

    # BTC хэмжээ (6 оронгийн нарийвчлалтай)
    btc_amount = round(usd_amount / btc_price, 6)

    city = context.user_data.get("city", "Улаанбаатар")
    text = (
        f"Захиалга баталгаажлаа ✅\n"
        f"Хот: {city}\n"
        f"Бараа: {choice}\n"
        f"Үнэ: ${usd_amount}\n\n"
        f"💳 Төлбөр (Bitcoin):\n{BTC_ADDRESS}\n"
        f"Илгээх хэмжээ: {btc_amount} BTC\n\n"
        "Төлбөрөө хийсний дараа /paid гэж бичээрэй."
    )
    update.message.reply_text(text)

    # BTC QR зураг
    img = qrcode.make(BTC_ADDRESS)
    bio = BytesIO(); bio.name = "btc.png"
    img.save(bio, "PNG"); bio.seek(0)
    update.message.reply_photo(photo=bio, caption="BTC address QR")

# ---------------- Гол app ----------------
def main():
    up = Updater(TOKEN, use_context=True)
    dp = up.dispatcher

    # Командууд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("menu", menu_cmd))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("pay", pay_cmd))
    dp.add_handler(CommandHandler("paid", paid_cmd))

    # Алхам 1: Хот
    dp.add_handler(MessageHandler(Filters.regex("^Улаанбаатар$"), handle_city))
    dp.add_handler(MessageHandler(Filters.regex("^🔁 Цэс шинэчлэх$"), handle_back_or_refresh))

    # Алхам 2: Бараа
    product_regex = "^(" + "|".join(
        p.replace("(", r"\(").replace(")", r"\)") for p in PRICES_USD.keys()
    ) + ")$"
    dp.add_handler(MessageHandler(Filters.regex(product_regex), show_payment))
    dp.add_handler(MessageHandler(Filters.regex("^(↩ Буцах|🔁 Цэс шинэчлэх)$"), handle_back_or_refresh))

    up.start_polling()
    up.idle()

if __name__ == "__main__":
    main()
