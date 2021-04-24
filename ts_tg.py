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
import urllib

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


def start(update: Update, context: CallbackContext) -> int:
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


def choose_action(update: Update, context: CallbackContext) -> int:
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

    elif update.message.text == "/cancel":
        return cancel(update=update, context=context)


def download_and_send_photo(update: Update, context: CallbackContext) -> int:
    text = update.message.text

    if text == "/cancel":
        return cancel(update=update, context=context)
    elif not check_link_possibility(text):
        print("d")
        update.message.reply_photo("https://ibb.co/sqhpzM2",
                                   caption=('Неверный формат.\n Убедидетесь в правильности вводимой ссылки,'
                                            ' она должна соответствовать одному из предложенных образцов:\n'
                                            '\n'
                                            '1. https://www.instagram.com/p/CMnW2SBMKiu/\n'
                                            '2. www.instagram.com/p/CMnW2SBMKiu/\n'
                                            '3. instagram.com/p/CMnW2SBMKiu/\n'),
                                   reply_markup=ReplyKeyboardRemove())
    else:
        logger.info("Photo link is %s", update.message.text)

        update.message.reply_text(
            '*Ожидайте*',
            reply_markup=ReplyKeyboardRemove()
        )

        context.bot.send_chat_action(update.effective_chat.id, "upload_document")

        links_request = get_links_from_post(text)

        if links_request is None:
            links_request = get_links_from_post(text)
            logger.info("Link is broken:")
            update.message.reply_photo("https://ibb.co/8mPwsP6",
                                       caption=('Ошибка получения информации от instagram.'
                                                '\nДля начала, убедидетесь в правильности вводимой ссылки,'
                                                ' она должна соответствовать одному из предложенных образцов:\n'
                                                '\n'
                                                '1. https://www.instagram.com/p/CMnW2SBMKiu/\n'
                                                '2. www.instagram.com/p/CMnW2SBMKiu/\n'
                                                '3. instagram.com/p/CMnW2SBMKiu/\n'),
                                                reply_markup=ReplyKeyboardRemove())
            update.message.reply_text('Если ошибка продолжает появляться, то обязательно сообщите о ней в'
                                                ' telegram @volinvd')

            return menu(update=update, context=context)


        if links_request[0] == "GraphImage":
            try:
                context.bot.send_document(
                    update.effective_chat.id,
                    document=links_request[1])
            except:
                logger.info("Can't send photo:", links_request[1])
                update.message.reply_photo("https://ibb.co/8mPwsP6",
                                           caption=('Ошибка отправки сообщения.'
                                                    '\nДля начала, убедидетесь в правильности вводимой ссылки,'
                                                    ' она должна соответствовать одному из предложенных образцов:\n'
                                                    '\n'
                                                    '1. https://www.instagram.com/p/CMnW2SBMKiu/\n'
                                                    '2. www.instagram.com/p/CMnW2SBMKiu/\n'
                                                    '3. instagram.com/p/CMnW2SBMKiu/\n',

                                                    'Если ошибка продолжает появляться, то обязательно сообщите о ней в'
                                                    ' telegram @volinvd'),
                                           reply_markup=ReplyKeyboardRemove())

        elif links_request[0] == "GraphSidecar":

            for url in (links_request[1]):
                try:
                    context.bot.send_document(
                        update.effective_chat.id,
                        document=url)
                except:
                    logger.info("Can't send photo:", url)

    return menu(update=update, context=context)


def check_link_possibility(link):
    if "instagram.com" not in link:
        return False

    return True


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
    context.bot.send_chat_action(update.effective_chat.id, "upload_document")
    links_request = get_links_from_story(username)

    for elem in links_request[1]:
        try:
            context.bot.send_chat_action(update.effective_chat.id, "upload_document")
            context.bot.send_document(
                update.effective_chat.id,
                document=elem)
        except:
            logger.info("Can't send photo:", links_request[1])

    return menu(update=update, context=context)


def menu(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Скачать фото', 'Посмотреть stories', 'pass']]

    update.message.reply_text(
        'Вы хотите сделать что-нибудь еще?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True),
    )

    return ACTION


def cancel(update: Update, context: CallbackContext) -> int:
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

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
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
