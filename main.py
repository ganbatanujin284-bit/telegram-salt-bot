import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")

# Бүтээгдэхүүнүүд (нэр → MNT)
PRICES_MNT = {
    "Давс 1 – 600000₮": 600000,
    "Давс 2 – 900000₮": 900000,
    "Давс 3 – 1200000₮": 1200000,
}

def kb_city():
    return ReplyKeyboardMarkup(
        [["Улаанбаатар"], ["🔁 Цэс шинэчлэх"]],
        one_time_keyboard=True, resize_keyboard=True
    )

def kb_products():
    rows = [[k] for k in PRICES_MNT.keys()]
    rows.append(["Буцах"])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Сайн уу! Хот сонгоно уу 👇", reply_markup=kb_city())

def on_text(update: Update, context: CallbackContext):
    text = (update.message.text or "").strip()

    if text == "Улаанбаатар":
        update.message.reply_text("Бүтээгдэхүүнүүд:", reply_markup=kb_products())
    elif text in PRICES_MNT:
        price = PRICES_MNT[text]
        update.message.reply_text(f"Та {text} сонголоо. Үнэ: {price}₮")
    elif text in ("🔁 Цэс шинэчлэх", "Буцах"):
        update.message.reply_text("Цэс шинэчлэгдлээ.", reply_markup=kb_city())
    else:
        update.message.reply_text("Товчилсон цэснээс сонгоно уу.")

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN тохируулна уу (.env-д BOT_TOKEN=...)")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, on_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
  
