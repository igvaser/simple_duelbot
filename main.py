from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import random

# === ТВОЙ ТОКЕН и WebApp URL ===
import os
TOKEN = os.getenv("BOT_TOKEN")

WEBAPP_URL = "https://telegram-fireduel.vercel.app"

CHOICES = ["Камень 🪨", "Ножницы ✂️", "Бумага 📄"]

# === Команда /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎮 Играть в WebApp", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("🤖 Играть в Telegram", callback_data="tg_play")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Выбери, как ты хочешь играть:",
        reply_markup=reply_markup
    )

# === Команда /play (для Telegram) ===
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_choice_buttons(update.effective_chat.id, context)

# === Выбор Telegram-варианта игры через кнопку ===
async def handle_tg_play_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await send_choice_buttons(query.message.chat_id, context)

# === Отправка кнопок Камень/Ножницы/Бумага ===
async def send_choice_buttons(chat_id, context):
    keyboard = [
        [InlineKeyboardButton("Камень 🪨", callback_data="Камень 🪨")],
        [InlineKeyboardButton("Ножницы ✂️", callback_data="Ножницы ✂️")],
        [InlineKeyboardButton("Бумага 📄", callback_data="Бумага 📄")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Выбери свой ход:",
        reply_markup=reply_markup
    )

# === Определение результата игры ===
def get_result(user, bot):
    if user == bot:
        return "🤝 Ничья!"
    elif (user.startswith("Камень") and bot.startswith("Ножницы")) or \
         (user.startswith("Ножницы") and bot.startswith("Бумага")) or \
         (user.startswith("Бумага") and bot.startswith("Камень")):
        return "🎉 Ты победил!"
    else:
        return "🤖 Бот победил!"

# === Обработка выбора хода ===
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_choice = query.data
    bot_choice = random.choice(CHOICES)
    result = get_result(user_choice, bot_choice)

    keyboard = [
        [InlineKeyboardButton("🔁 Ещё раунд", callback_data="tg_play")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    response = (
        f"<b>Ты выбрал:</b> {user_choice}\n"
        f"<b>Бот выбрал:</b> {bot_choice}\n\n"
        f"<b>{result}</b>"
    )

    await query.edit_message_text(text=response, reply_markup=reply_markup, parse_mode="HTML")

# === Запуск приложения ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))

    app.add_handler(CallbackQueryHandler(handle_choice, pattern="^(Камень|Ножницы|Бумага).*"))
    app.add_handler(CallbackQueryHandler(handle_tg_play_button, pattern="^tg_play$"))

    app.run_polling()

if __name__ == "__main__":
    main()