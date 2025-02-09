from pathlib import Path

from cache import KVStorage
from handler import Handler
from telegram import MessageEntity
import os
from dotenv import load_dotenv


import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from cached_message import CachedMessage, Entity
from utils import init_logger, help_message

init_logger()

logger = logging.getLogger(__name__)

path = Path(__file__).parent.parent / ".env"
assert path.is_file()

load_dotenv(path)
telegram_api = os.getenv("TELEGRAM_API")
handler = Handler.from_env()
cache_storage = KVStorage(table_name="cache", file_name="cache_storage.db")


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    message = rf"Hi {user.mention_html()}!"
    message += "\n\n"
    message += help_message()
    await update.message.reply_html(
        message
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(help_message())


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    text_input = update.message.text
    message = await update.message.reply_text(text="Wait a second")

    cache = cache_storage.load(text_input)
    if cache is not None:
        logger.info(f"Cache hit: `{text_input}`")
        try:
            answer = CachedMessage.model_validate_json(cache)
            await context.bot.edit_message_text(
                text=answer.text,
                chat_id=update.message.chat_id,
                message_id=message.message_id,
                entities=answer.tg_entities(),
            )
            return
        except Exception as e:
            logger.error(e)

    text = ""
    entities = []
    logger.info(f"Cache miss: `{text_input}`")
    for chunk in handler.handle(text_input):
        text += chunk.message
        entity = MessageEntity(
            type=chunk.message_type, offset=len(text), length=len(chunk.message)
        )
        if chunk.message_type:
            entities.append(entity)
        if chunk.message.strip() != "":
            await context.bot.edit_message_text(
                text=text,
                chat_id=update.message.chat_id,
                message_id=message.message_id,
                entities=entities,
            )
    answer_to_cache = CachedMessage(
        text=text,
        entities=[Entity.from_tg(_) for _ in entities],
    )
    cache_storage.save(key=text_input, value=answer_to_cache.model_dump_json())


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(telegram_api).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':

    main()
