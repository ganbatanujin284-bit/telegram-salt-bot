import os
from io import BytesIO
import qrcode, requests
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("8449746552:AAGDJBlNazAHg_UcMWeGMfw99v6rNYX7ukg")
BTC_ADDRESS = os.getenv("BTC_ADDRESS") or "bc1qhs90rgayvff7h50fcmwmlkgk9sdxq58m6pzthd"  # ← өөрийн хаягаа оруул

# Дисплей дээр MNT, бодит BTC-д зориулж USD дүн хадгална
ITEMS = {
    "Давс 1 – 600,000₮": {"usd": 150, "mnt": 600_000},
    "Давс 2 – 900,000₮": {"usd": 230, "mnt": 900_000},
    "Давс 3 – 1,200,000₮": {"usd": 330, "mnt": 1_200_000},
}

def kb_products():
    rows = [[name] for name in ITEMS.keys()]
    rows.append(["🔁 Цэс шинэчлэх"])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def fetch_btc_usd_rate():
    """
    CoinGecko-оос BTC/USD ханш татна. Амжилтгүй бол None буцаана.
    """
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": "bitcoin", "vs_currencies": "usd"},
            timeout=6,
        )
        r.raise_for_status()
        data = r.json()
        return float(data["bitcoin"]["usd"])
    except Exception:
        return None

def make_bip21_qr(btc_address: str, amount_btc: float, label: str = "Payment"):
    """
    BIP21 URI үүсгээд QR болгоно: bitcoin:<addr>?amount=<btc>&label=<label>
    """
    uri = f"bitcoin:{btc_address}?amount={amount_btc:.8f}&label={label}"
    img = qrcode.make(uri)
    bio = BytesIO()
    bio.name = "btc_payment_qr.png"
    img.save(bio, "PNG")
    bio.seek(0)
    return bio, uri

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Сайн уу! Доорх цэсээс бүтээгдэхүүнээ сонгоно уу 👇",
        reply_markup=kb_products()
    )

def on_text(update: Update, context: CallbackContext):
    text = (update.message.text or "").strip()

    if text in ITEMS:
        usd = ITEMS[text]["usd"]
        mnt = ITEMS[text]["mnt"]

        # Ханш авч BTC тооцоолох
        rate = fetch_btc_usd_rate()  # 1 BTC = ? USD
        if rate:
            btc_amount = round(usd / rate, 8)  # дүнг BTC-рүү
            qr, uri = make_bip21_qr(BTC_ADDRESS, btc_amount, label=text.replace(" ", "_"))
            caption = (
                f"Та {text} сонголоо.\n\n"
                f"Төлбөр: {mnt:,}₮ (жишээ дэлгэц), бодит BTC: ~${usd}\n"
                f"Одоогийн ханшаар: {btc_amount} BTC  (1 BTC ≈ ${rate:,.2f})\n\n"
                f"BTC Address:\n{BTC_ADDRESS}\n\n"
                f"BIP21 URI:\n{uri}"
            )
            update.message.reply_photo(photo=qr, caption=caption)
        else:
            # Ханш авч чадсангүй – хаяг л үзүүлнэ
            update.message.reply_text(
                f"Та {text} сонголоо.\n\n"
                f"Төлбөр: {mnt:,}₮ (жишээ дэлгэц), бодит BTC нь ~${usd} дүнтэй тэнцүү.\n"
                f"Одоогоор ханш татаж чадсангүй. BTC хаяг:\n{BTC_ADDRESS}"
            )

    elif text == "🔁 Цэс шинэчлэх":
        update.message.reply_text("Цэс шинэчлэгдлээ.", reply_markup=kb_products())
    else:
        update.message.reply_text("Цэснээс сонгоно уу.", reply_markup=kb_products())

def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN тохируулна уу (.env → BOT_TOKEN=...)")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, on_text))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    
