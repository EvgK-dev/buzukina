import logging
import re
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import httpx
from decouple import config

# Настройка логирования с ротацией
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.handlers.RotatingFileHandler("bot.log", maxBytes=10485760, backupCount=5),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_BOT_TOKEN = config("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_CHAT_ID = config("TELEGRAM_GROUP_CHAT_ID", cast=int)
API_BASE_URL = config("API_BASE_URL", default="http://127.0.0.1:8000/api/")


# бронирование

async def process_booking(update: Update, context: ContextTypes.DEFAULT_TYPE, endpoint: str, action: str) -> None:
    query = update.callback_query
    await query.answer()

    message_text = query.message.text
    reply_markup = query.message.reply_markup
    booking_data = extract_booking_data(message_text)

    if booking_data is None:
        await query.edit_message_text("⚠️ Ошибка при извлечении данных.")
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE_URL}{endpoint}/", json=booking_data)
        response_data = response.json()
        result_message = response_data.get("message", f"⚠️ Ошибка при {action} бронирования.")
    except Exception as e:
        result_message = f"⚠️ Ошибка при {action} бронирования: {e}"

    updated_message = f"{message_text}\n\n{result_message}"
    await query.edit_message_text(
        text=updated_message,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await process_booking(update, context, "confirm", "подтверждении")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await process_booking(update, context, "cancel", "отмене")

def extract_booking_data(message_text):
    booking_data = {}
    lines = message_text.strip().split("\n")
    for line in lines:
        if line.startswith("ДОМ:"):
            booking_data["house"] = line.split("ДОМ: ")[1].strip()
        elif line.startswith(" ЗАЕЗД:"):
            booking_data["startdate"] = line.split("ЗАЕЗД:")[1].strip()
        elif line.startswith(" СУТОК:"):
            booking_data["day"] = line.split("СУТОК: ")[1].strip()
        elif line.startswith(" ИМЯ:"):
            booking_data["person"] = line.split("ИМЯ: ")[1].strip()
        elif line.startswith(" НОМЕР:"):
            booking_data["contact"] = line.split("НОМЕР: ")[1].strip()
        elif line.startswith("  КОММЕНТАРИЙ:"):
            booking_data["additional_services"] = line.split("КОММЕНТАРИЙ: ")[1].strip()
        elif line.startswith("АДМИН:"):
            booking_data["admin_text"] = line.split("АДМИН: ")[1].strip()
    return booking_data if booking_data else None

async def change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    notification = await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(
            "Вам надо прокомментировать (ответить на) сообщение, чтобы внести в него изменения.\n\n"
            "Затем '✅ Подтвердить', чтобы изменения пошли в базу данных.\n"
            "Вы должны увидеть сообщение '✅ Бронирование подтверждено!'\n\n"
            "Иначе нажмите '❌ Отменить' и '✅ Подтвердить'\n\n"
            "⚠️ Обратите внимание: текст внутри поля АДМИН перезаписывается и будет содержать только последний комментарий"
        ),
    )
    await asyncio.sleep(8)
    await notification.delete()


# проверка забронированных дат

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text
    if not message_text:
        return

    message_text = message_text.lower()
    if message_text == "меню":
        keyboard = [[InlineKeyboardButton("📅 Забронированные даты", callback_data="booked_dates")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите опцию:",
            reply_markup=reply_markup,
        )
    elif update.message.reply_to_message and update.message.reply_to_message.from_user.is_bot:
        replied_message = update.message.reply_to_message
        comment_text = update.message.text
        original_text = replied_message.text
        if "АДМИН:" in original_text:
            lines = original_text.split("\n")
            updated_lines = [f"АДМИН: {comment_text}" if line.startswith("АДМИН:") else line for line in lines]
            new_text = "\n".join(updated_lines)
        else:
            new_text = original_text + f"\n\nАДМИН: {comment_text}"
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=replied_message.message_id,
            text=new_text,
            reply_markup=replied_message.reply_markup,
        )

async def booked_dates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_BASE_URL}check_houses/")
        if response.status_code == 200:
            response_data = response.json()
            buttons = [[InlineKeyboardButton(f"🏠 {house['name']}", callback_data=f"house_{house['id']}")] for house in response_data]
            result_message = "Выберите дом:"
        else:
            result_message = "⚠️ Ошибка при получении данных о домах."
            buttons = []
    except Exception as e:
        result_message = f"⚠️ Ошибка при подключении к серверу: {e}"
        buttons = []
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        text=result_message,
        reply_markup=reply_markup,
        parse_mode="HTML",
    )

async def handle_house_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    house_id = query.data.split("_")[1]
    await query.answer()
    period_buttons = [
        [InlineKeyboardButton("📅 Неделя", callback_data=f"week_{house_id}")],
        [InlineKeyboardButton("📅 Месяц", callback_data=f"month_{house_id}")],
    ]
    reply_markup = InlineKeyboardMarkup(period_buttons)
    await query.edit_message_text(
        text="Выберите период для просмотра забронированных дат:",
        reply_markup=reply_markup,
    )

async def handle_period_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    try:
        period, house_id = query.data.split("_")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}get_reserved_dates/",
                json={"house_id": house_id, "period": period},
            )
        if response.status_code == 200:
            response_data = response.json()
            reserved_dates = response_data.get("reserved_dates", [])
            house_name = response_data.get("house_name", "Неизвестный дом")
            reserved_message = "\n".join(
                [
                    f"<b>{date['date']}</b> - <b>{date['person']}</b> <code>{date['contact']}</code> // чел.: {date['num_people']} // доп.: {date['additional_services']},"
                    for date in reserved_dates
                ]
            )
            result_message = (
                f"Забронированные даты для <b>{house_name}</b>:\n\n{reserved_message}"
                if reserved_message
                else f"Нет забронированных дат для <b>{house_name}</b>"
            )
        else:
            result_message = "⚠️ Ошибка при получении данных о забронированных датах."
    except Exception as e:
        result_message = f"⚠️ Ошибка при подключении к серверу: {e}"
    await query.edit_message_text(text=result_message, parse_mode="HTML")



def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(booked_dates, pattern="^booked_dates$"))
    application.add_handler(CallbackQueryHandler(handle_house_selection, pattern=r"^house_\d+$"))
    application.add_handler(CallbackQueryHandler(handle_period_selection, pattern=r"^(week|two_weeks|month)_\d+$"))
    application.add_handler(CallbackQueryHandler(confirm, pattern="confirm:*"))
    application.add_handler(CallbackQueryHandler(cancel, pattern="cancel:*"))
    application.add_handler(CallbackQueryHandler(change, pattern="^change$"))
    application.run_polling()

if __name__ == "__main__":
    main()