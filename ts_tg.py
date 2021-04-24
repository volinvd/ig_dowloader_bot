# !/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import instaloader_test as ig_get_links

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InputMediaDocument
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

MENU, ACTION, DOWNLOAD_PHOTO_REQUEST, DOWNLOAD_STORIES_REQUEST = range(4)
reply_keyboard = [['Скачать фото', 'Посмотреть stories', 'pass']]

def start(update: Update, _: CallbackContext) -> int:
    reply_markup = ReplyKeyboardMarkup(
        keyboard=reply_keyboard,
        resize_keyboard=True
    )

    update.message.reply_text(
        'Описание бота*'
        'Send /cancel to stop talking to me.\n\n'
        'Что вы хотите сделать?',
        reply_markup=reply_markup)

    return ACTION


def choose_action(update: Update, _: CallbackContext) -> int:
    print("e")
    user = update.message.from_user
    user_answr = update.message.text
    logger.info("Action of %s: %s", user.first_name, user_answr)
    update.message.reply_text(
        "Хорошо",
        reply_markup=ReplyKeyboardRemove(),
    )

    if update.message.text == "Скачать фото":
        update.message.reply_text(
            "Пришлите мне ссылку на фото",
            reply_markup=ReplyKeyboardRemove(),
        )
        return DOWNLOAD_PHOTO_REQUEST

    elif update.message.text == "Посмотреть stories":
        update.message.reply_text(
            "Пришлите мне ссылку на профиль пользователя",
            reply_markup=ReplyKeyboardRemove(),
        )
        return DOWNLOAD_STORIES_REQUEST


def download_and_send_photo(update: Update, context: CallbackContext) -> int:
    logger.info("Photo link is %s", update.message.text)
    photo_link = update.message.text
    update.message.reply_text(
        '*Ожидайте*',
    )

    links_request = get_links_from_post(photo_link)
    print(links_request)

    if links_request[0] == "GraphImage":
        try:
            context.bot.send_document(
                update.effective_chat.id,
                document=links_request[1])
        except:
            logger.info("Can't send photo:", links_request[1])

    elif links_request[0] == "GraphSidecar":

        for url in (links_request[1]):
            try:
                context.bot.send_document(
                    update.effective_chat.id,
                    document=url)
            except: logger.info("Can't send photo:", url)

    return ACTION



def get_links_from_post(link):
    ig = ig_get_links.GetLinksIG()
    info = ig.get_photo_urls(link)

    logger.info("get_links: urls is %s", info)

    return info

def get_links_from_story(username):
    ig = ig_get_links.GetLinksIG()
    info = ig.get_story_urls(username)

    logger.info("get_links: urls is %s", info)

    return info


def download_and_send_stories(update: Update, context: CallbackContext) -> int:
    logger.info("User link is %s", update.message.text)
    username = update.message.text
    update.message.reply_text(
        '*Ожидайте*',
        reply_markup=ReplyKeyboardRemove(),
    )

    links_request = get_links_from_story(username)
    print(links_request)

    for elem in links_request[1]:
        try:
            context.bot.send_document(
                update.effective_chat.id,
                document=elem)
        except:
            logger.info("Can't send photo:", links_request[1])

    return MENU


def menu(update: Update, _: CallbackContext) -> int:
    print('DDDDDDDDDDD')
    reply_keyboard = [['Скачать фото', 'Посмотреть stories', 'pass']]

    update.message.reply_text(
        'Что вы хотите сделать?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False),
    )

    return ACTION



def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    # Create the Updater and pass it your bot's token.
    updater = Updater(token="1663996570:AAEWn7SRSkVPqftZHX8fC994t_-6b95CnFY",
                      use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [MessageHandler(Filters.regex('^(Скачать фото|Посмотреть stories|pass)$'), menu)],
            ACTION: [MessageHandler(Filters.text, choose_action)],
            DOWNLOAD_PHOTO_REQUEST: [MessageHandler(Filters.text, download_and_send_photo)],
            DOWNLOAD_STORIES_REQUEST: [MessageHandler(Filters.text, download_and_send_stories)],

        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
