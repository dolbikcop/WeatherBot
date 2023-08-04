import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, \
    ConversationHandler, MessageHandler, filters, CallbackContext

from cities import available_cities, get_info_about_city, get_weather_journal
from text_message import GREETINGS

load_dotenv()
token = os.getenv("TOKEN")


async def helper(update: Update, _):
    await update.message.reply_text(GREETINGS)


async def cities(update: Update, _) -> None:
    keyboard = [
        [
            InlineKeyboardButton(city.title(), callback_data=city)
            for city in available_cities[i:i + 3]
        ] for i in range(0, len(available_cities), 3)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Доступные города: ', reply_markup=reply_markup)


async def choose_city_inline_buttons(update: Update, _):
    query = update.callback_query
    city_name = query.data

    city_info = get_info_about_city(city_name)

    await query.answer()
    await query.message.reply_text(city_info)
    return 0


async def choose_city_input(update: Update, _):
    city_name = update.message.text
    city_info = get_info_about_city(city_name)

    await update.message.reply_text(city_info)
    return 0


async def city_is_unknown(update: Update, _):
    await update.message.reply_text('Введите другой город.')
    return 0


async def start(update: Update, _):
    await update.message.reply_text('Введите нужный вам город')
    return 0


async def journal(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        await update.message.reply_text('Метода использования: \n'
                                        '/journal <название города>')
    else:
        city_name = context.args[0]
        city_journal = get_weather_journal(city_name)

        if len(city_journal) == 0:
            await update.message.reply_text(f'Записей по городу {city_name} не существует.')
            return

        await update.message.reply_text(f'Выбранный город: {city_name} \n\n'
                                        + '\n'.join(city_journal))


def main() -> None:
    pattern = '^' + '|'.join(available_cities) + "$"
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            0: [
                MessageHandler(filters.Regex(pattern), choose_city_input),
                MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex(pattern)), city_is_unknown)
            ]
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("cities", cities),
            CommandHandler("help", helper),
            CommandHandler('journal', journal),
            CommandHandler("cancel", helper)
                   ],
    )

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("cities", cities))
    app.add_handler(CallbackQueryHandler(choose_city_inline_buttons, pattern=pattern))
    app.add_handler(CommandHandler("help", helper))
    app.add_handler(CommandHandler('cancel', helper))
    app.add_handler(CommandHandler('journal', journal))
    app.add_handler(conv_handler)

    app.run_polling()


if __name__ == '__main__':
    main()
