from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import qrcode
from io import BytesIO

TOKEN = "8449746552:AAGEgAhr7fJE-Scqijs4tovIpqo-vQtRGzQ"          # ← BotFather токеноо тавина
BTC_ADDRESS = "bc1qhs90rgayvff7h50fcmwmlkgk9sdxq58m6pzthd" # ← BTC хаягаа тавина

PRICES = {
    "Давс 1 – 600,000₮": 600000,
    "Давс 2 – 900,000₮": 900000,
    "Давс 3 – 1,200,000₮": 1200000,
}

def start(update: Update, context: CallbackContext):
    kb = [["Улаанбаатар"]]
    update.message.reply_text("Хот сонгоно уу 👇",
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True))

def handle_city(update: Update, context: CallbackContext):
    context.user_data["city"] = update.message.text
    kb = [[k] for k in PRICES.keys()]
    update.message.reply_text("Бараагаа сонгоно уу 👇",
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True))

def show_payment(update: Update, context: CallbackContext):
    choice = update.message.text
    if choice not in PRICES:
        update.message.reply_text("Буруу сонголт. /start гэж эхлүүлнэ үү.")
        return
    amt = PRICES[choice]
    city = context.user_data.get("city", "Улаанбаатар")
    msg = (f"Захиалга баталгаажлаа ✅\nХот: {city}\nБараа: {choice}\n"
           f"Нийт үнэ: {amt:,}₮\n\n💳 BTC хаяг:\n{BTC_ADDRESS}\n\n"
           "Төлбөр хийсний дараа /paid гэж бичээрэй.")
    update.message.reply_text(msg)
    # QR
    img = qrcode.make(BTC_ADDRESS)
    bio = BytesIO(); bio.name = "btc.png"; img.save(bio, "PNG"); bio.seek(0)
    update.message.reply_photo(photo=bio, caption="BTC address QR")

def repeat_pay(update: Update, context: CallbackContext):
    update.message.reply_text(f"BTC: {BTC_ADDRESS}")

def paid(update: Update, context: CallbackContext):
    update.message.reply_text("Баярлалаа! Төлбөр шалгаж байна. 👌")

def main():
    up = Updater(TOKEN, use_context=True)
    dp = up.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("pay", repeat_pay))
    dp.add_handler(CommandHandler("paid", paid))
    dp.add_handler(MessageHandler(Filters.regex("^Улаанбаатар$"), handle_city))
    product_regex = "^(" + "|".join(map(lambda s: s.replace("(", r"\(").replace(")", r"\)"), PRICES.keys())) + ")$"
    dp.add_handler(MessageHandler(Filters.regex(product_regex), show_payment))
    up.start_polling()
    up.idle()

if __name__ == "__main__":
    main()
