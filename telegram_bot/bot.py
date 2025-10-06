# telegram-bot/bot.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "7564444541:AAF4H4vv1m7JwE24v5Cqwe9SpQniZvUg8bo"
WEB_APP_URL = "https://alexeiyaganov.github.io/na_sporte/"  # ЗАМЕНИТЕ НА СВОЙ URL


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏃 Поиск мероприятий", callback_data="mode_events")],
        [InlineKeyboardButton("👥 Найти напарника", callback_data="mode_people")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🏃 **SportEvents Map**\n\nВыберите режим работы:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "mode_events":
        keyboard = [[InlineKeyboardButton(
            "🔍 Открыть поиск мероприятий",
            web_app=WebAppInfo(url=f"{WEB_APP_URL}?mode=events")
        )]]
        await query.edit_message_text(
            "🏃 **Режим поиска мероприятий**\n\nНайдите спортивные события рядом с вами!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    elif query.data == "mode_people":
        keyboard = [[InlineKeyboardButton(
            "👥 Открыть поиск напарников",
            web_app=WebAppInfo(url=f"{WEB_APP_URL}?mode=people")
        )]]
        await query.edit_message_text(
            "👥 **Режим поиска напарников**\n\nНайдите единомышленников для тренировок!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )


async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(
        "🔍 Открыть поиск мероприятий",
        web_app=WebAppInfo(url=f"{WEB_APP_URL}?mode=events")
    )]]
    await update.message.reply_text(
        "Открываю поиск мероприятий...",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def people_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(
        "👥 Открыть поиск напарников",
        web_app=WebAppInfo(url=f"{WEB_APP_URL}?mode=people")
    )]]
    await update.message.reply_text(
        "Открываю поиск напарников...",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("events", events_command))
    application.add_handler(CommandHandler("people", people_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()