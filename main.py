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
import instaloader
import download_ig as ig_get_links
import urllib

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InputMediaDocument, InlineKeyboardMarkup, \
    InlineKeyboardButton, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)

updater = Updater(token="1663996570:AAEWn7SRSkVPqftZHX8fC994t_-6b95CnFY",
                  use_context=True)

logger = logging.getLogger(__name__)
tg_logger = logging.getLogger('telegram')
tg_logger.setLevel(logging.INFO)
ig_logger = logging.getLogger('download_ig')
ig_logger.setLevel(logging.DEBUG)
urllib_logger = logging.getLogger('urllib3')
urllib_logger.setLevel(logging.INFO)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

MENU, ACTION, DOWNLOAD_PHOTO_REQUEST, DOWNLOAD_STORIES_REQUEST, GET_ACCOUNT_INFORMATION = range(5)
reply_keyboard = [['Скачать фото', 'Посмотреть stories', 'Информация о профиле']]
actions = ["/cancel", "/start", "/dp", "/ds", "/pi"]

reply_error_keyboard = [['Главное меню', 'Завершить']]

keyboard = [[InlineKeyboardButton("Главное меню", callback_data='Главное меню'),
             InlineKeyboardButton("Завершить", callback_data='Завершить')]]

ERROR_REPLY_MARKUP = ReplyKeyboardRemove()  # InlineKeyboardMarkup(keyboard)


def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.debug("%s %s starts the bot. Info: id - %s, username - %s, lg_code - %s",
                 user.first_name, user.last_name, user.id, user.username, user.language_code)
    reply_markup = ReplyKeyboardMarkup(
        keyboard=reply_keyboard,
        resize_keyboard=True
    )

    update.message.reply_text(
        'IG Downloader - бот для полностью анонимного просмотра записей и stories в Instagram.'
        '\n\n'
        'Используйте следующие команды для взаимодействия с ботом:\n'
        '/start - Запустить бота\n'
        '/cancel - Завершить диалог\n'
        '/support - Поддержка и разработка бота\n')

    update.message.reply_text('Что вы хотите сделать?',
                              reply_markup=reply_markup)

    return ACTION


def choose_action(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_answr = update.message.text

    if update.message.text in reply_keyboard[0] or update.message.text in actions:
        logger.info("Action of %s %s: %s", user.first_name, user.last_name, user_answr)
        update.message.reply_text(
            "Хорошо",
            reply_markup=ReplyKeyboardRemove(),
        )

        if update.message.text == "Скачать фото" or update.message.text == "/dp":
            update.message.reply_text(
                "Пришлите мне ссылку на фото",
                reply_markup=ReplyKeyboardRemove(),
            )
            return DOWNLOAD_PHOTO_REQUEST

        elif update.message.text == "Посмотреть stories" or update.message.text == "/ds":
            update.message.reply_text(
                "Пришлите мне ссылку на профиль пользователя",
                reply_markup=ReplyKeyboardRemove(),
            )
            return DOWNLOAD_STORIES_REQUEST

        elif update.message.text == "Информация о профиле" or update.message.text == "/pi":
            update.message.reply_text(
                "Пришлите мне ссылку на профиль пользователя",
                reply_markup=ReplyKeyboardRemove(),
            )
            return GET_ACCOUNT_INFORMATION

        elif update.message.text == "/cancel":
            return cancel(update=update, context=context)

        elif update.message.text == "/start":
            return start(update=update, context=context)

        else:
            update.message.reply_text(
                "Выберите одно из действий, указанных на кнопках ниже",
                reply_markup=ReplyKeyboardRemove(),
            )
            return menu(update=update, context=context)
    else:
        update.message.reply_text(
            "Выберите одно из действий, указанных на кнопках ниже",
            reply_markup=ReplyKeyboardRemove(),
        )

        return menu(update=update, context=context)


def download_and_send_photo(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    logger.info("Got text: %s", text)
    reply_error_markup = ReplyKeyboardMarkup(
        keyboard=reply_error_keyboard,
        resize_keyboard=True
    )

    if text == "/cancel" or text == "Завершить":
        return cancel(update=update, context=context)
    elif text == "/start":
        return start(update=update, context=context)
    elif text == "Главное меню":
        return menu(update=update, context=context)
    elif text == "Скачать фото":
        update.message.reply_text(
            "Пришлите мне ссылку на фото",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif not check_link_possibility(text):
        logger.info("Got text: %s", text)
        update.message.reply_photo("https://ibb.co/sqhpzM2",
                                   caption=('Неверный формат ссылки фотографии.'
                                            '\nУбедидетесь в правильности вводимой ссылки,'
                                            ' она должна соответствовать одному из предложенных образцов:\n'
                                            '\n'
                                            '1. https://www.instagram.com/p/CMnW2SBMKiu/\n'
                                            '2. www.instagram.com/p/CMnW2SBMKiu/\n'
                                            '3. instagram.com/p/CMnW2SBMKiu/\n'),
                                   reply_markup=reply_error_markup)
        logger.info("Link unsupported: %s", text)
        return
    else:
        update.message.reply_text(
            'Пожалуйста, подождите',
            reply_markup=ReplyKeyboardRemove()
        )

        context.bot.send_chat_action(update.effective_chat.id, "upload_document")

        links_request = get_links_from_post(text)
        logger.info("Link request: %s", links_request)

        if links_request is None:
            links_request = get_links_from_post(text)
            logger.warning("Link is broken: %s", links_request)
            context.bot.send_photo(update.message.chat.id, "https://ibb.co/8mPwsP6",
                                   caption=('Ошибка получения информации от Instagram.'
                                            '\nДля начала, убедидетесь в правильности вводимой ссылки,'
                                            ' она должна соответствовать одному из предложенных образцов:\n'
                                            '\n'
                                            '1. https://www.instagram.com/p/CMnW2SBMKiu/\n'
                                            '2. www.instagram.com/p/CMnW2SBMKiu/\n'
                                            '3. instagram.com/p/CMnW2SBMKiu/\n'
                                            '\nТакже, ошибка может возникнуть, если вы указали ссылку на '
                                            'фотографию, принадлежащую закрытому аккаунту'),
                                   reply_markup=reply_error_markup)

            update.message.reply_text('Если ошибка продолжает появляться, то обязательно сообщите о ней в'
                                      ' telegram @volinvd')

        if links_request[0] == "GraphImage":
            try:
                context.bot.send_document(
                    update.effective_chat.id,
                    document=links_request[1])
            except:
                logger.warning("Can't send photo:", links_request[1])
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
                                           reply_markup=reply_error_keyboard)

        elif links_request[0] == "GraphSidecar":
            for url in (links_request[1]):
                try:
                    context.bot.send_document(
                        update.effective_chat.id,
                        document=url)
                except:
                    logger.warning("Can't send photo: %s", url)

        return menu(update=update, context=context)


def inline_error_button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query

    if query.data == "Главное меню":
        menu(update=update, context=context)
    elif query.data == "Завершить":
        cancel(update=update, context=context)

    context.bot.answer_callback_query(query["id"])


def check_link_possibility(link):
    logger.debug("Link is %s", link)
    if "instagram.com" not in link:
        return False

    return True


def get_links_from_post(link):
    logger.debug("Link is %s", link)
    ig = ig_get_links.GetLinksIG()
    info = ig.get_photo_urls(link)

    logger.debug("Urls is %s", info)

    return info


def download_and_send_stories(update: Update, context: CallbackContext) -> int:
    logger.info("User account link is %s", update.message.text)
    profile_link = update.message.text

    reply_error_markup = ReplyKeyboardMarkup(
        keyboard=reply_error_keyboard,
        resize_keyboard=True
    )
    if profile_link == "/cancel" or profile_link == "Завершить":
        return cancel(update=update, context=context)
    elif profile_link == "/start":
        return start(update=update, context=context)
    elif profile_link == "Главное меню":
        return menu(update=update, context=context)
    elif profile_link == "Посмотреть stories":
        update.message.reply_text(
            "Пришлите мне ссылку на профиль в одном из предложенных форматов:"
            '\n'
            '1. https://www.instagram.com/volinvd/?hl=ru\n'
            '2. www.instagram.com/volinvd/?hl=ru\n'
            '3. www.instagram.com/volinvd/\n',
            reply_markup=ReplyKeyboardRemove(),
        )
    elif not check_link_possibility(profile_link):
        update.message.reply_photo("https://ibb.co/sqhpzM2",
                                   caption=('Неверный формат ссылки профиля.'
                                            '\nУбедидетесь в правильности вводимой ссылки,'
                                            ' она должна соответствовать одному из предложенных образцов:\n'
                                            '\n'
                                            '1. https://www.instagram.com/volinvd/?hl=ru\n'
                                            '2. www.instagram.com/volinvd/?hl=ru\n'
                                            '3. www.instagram.com/volinvd/\n'),
                                   reply_markup=reply_error_markup)
        logger.info("Invalid link format %s", profile_link)
    else:
        ig = ig_get_links.GetLinksIG()
        username = ig.username_from_link(profile_link)

        logger.debug("Username from link is %s", username)

        if ig.is_private_account(username):
            update.message.reply_photo("https://ibb.co/5xcD6Xt",
                                       caption=('Указана ссылка на закрытый профиль.'
                                                '\nК сожалению, получить доступ к закрытому аккаунту невозможно.'
                                                ),
                                       reply_markup=reply_error_markup)
            logger.debug("Account is private %s", info)
        else:
            update.message.reply_text(
                'Пожалуйста, подождите',
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
                    logger.warning("Can't send photo:", links_request[1])

        return menu(update=update, context=context)


def get_links_from_story(username):
    logger.debug("Username is %s", username)
    ig = ig_get_links.GetLinksIG()
    info = ig.get_story_urls(username)

    logger.info("Urls is %s", info)

    return info


def get_profile_info(username):
    logger.debug("get_links: urls is %s", username)
    ig = ig_get_links.GetLinksIG()
    info = ig.get_profile_info(username)

    logger.info("Info is %s", info)

    return info


def send_about_profile(update: Update, context: CallbackContext) -> int:
    logger.info("User link is %s", update.message.text)
    profile_link = update.message.text

    reply_error_markup = ReplyKeyboardMarkup(
        keyboard=reply_error_keyboard,
        resize_keyboard=True
    )

    if profile_link == "/cancel" or profile_link == "Завершить":
        return cancel(update=update, context=context)
    elif profile_link == "/start":
        return start(update=update, context=context)
    elif profile_link == "Главное меню":
        return menu(update=update, context=context)
    elif profile_link == "Информация о профиле":
        update.message.reply_text(
            "Пришлите мне ссылку на профиль в одном из предложенных форматов:"
            '\n'
            '1. https://www.instagram.com/volinvd/?hl=ru\n'
            '2. www.instagram.com/volinvd/?hl=ru\n'
            '3. www.instagram.com/volinvd/\n',
            reply_markup=ReplyKeyboardRemove(),
        )
    elif not check_link_possibility(profile_link):
        update.message.reply_photo("https://ibb.co/sqhpzM2",
                                   caption=('Неверный формат ссылки профиля.'
                                            '\nУбедидетесь в правильности вводимой ссылки,'
                                            ' она должна соответствовать одному из предложенных образцов:\n'
                                            '\n'
                                            '1. https://www.instagram.com/volinvd/?hl=ru\n'
                                            '2. www.instagram.com/volinvd/?hl=ru\n'
                                            '3. www.instagram.com/volinvd/\n'
                                            '4. instagram.com/volinvd/\n'),
                                   reply_markup=reply_error_markup)
        logger.info("Invalid link format %s", profile_link)
    else:
        update.message.reply_text(
            'Пожалуйста, подождите',
            reply_markup=ReplyKeyboardRemove(),
        )
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        ig = ig_get_links.GetLinksIG()
        try:
            username = ig.username_from_link(profile_link)

            profile_picture_url = get_profile_picture_link(username)
            info = get_profile_info(username)
            context.bot.send_chat_action(update.effective_chat.id, "typing")

            fullname, profile_type, count_of_followers, count_of_folowees, count_of_posts, count_of_igtv, type = \
                info["username"], info["profile_type"], info["count_of_followers"], \
                info["count_of_followees"], info["count_of_posts"], info["count_of_igtv"], info["type"]

            update.message.reply_photo(profile_picture_url,
                                       caption=(f"""
Информация по аккаунту {username}:

Имя пользователя: {fullname}
Тип профиля: {profile_type}

Количество подписчиков: {count_of_followers}
Количество подписок: {count_of_folowees}
Количество записей: {count_of_posts}
Количество видео Instagram TV: {count_of_igtv}
Тип аккаунта: {type}"""),
                                       reply_markup=ReplyKeyboardRemove())
        except instaloader.exceptions.ProfileNotExistsException:
            update.message.reply_photo("https://ibb.co/pwQnzMx",
                                       caption=('Указана сылка на несуществующий профиль.'
                                                '\nУбедидетесь в правильности вводимой ссылки,'
                                                ' она должна соответствовать одному из предложенных образцов:\n'
                                                '\n'
                                                '1. https://www.instagram.com/volinvd/?hl=ru\n'
                                                '2. www.instagram.com/volinvd/?hl=ru\n'
                                                '3. www.instagram.com/volinvd/\n'
                                                '4. instagram.com/volinvd/\n'),
                                       reply_markup=reply_error_markup)
            logger.info("Profile not exists %s", profile_link)

        return menu(update=update, context=context)


def get_profile_picture_link(username):
    ig = ig_get_links.GetLinksIG()
    info = ig.get_profile_photo_link(username)

    logger.info("Profile picture link is %s", info)

    return info


def menu(update: Update, context: CallbackContext) -> int:
    logger.debug("Menu")
    reply_keyboard = [['Скачать фото', 'Посмотреть stories', 'Информация о профиле']]

    context.bot.send_message(update.effective_chat.id,
                             'Вы хотите сделать что-нибудь еще?',
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False,
                                                              resize_keyboard=True),
                             )

    return ACTION


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Conversation for %s %s (%s) ended", user.first_name, user.last_name, user.username)
    update.message.reply_text('Диалог завершен. Вы можете заново обратиться ко мне используя команду /start.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main() -> None:
    # Create the Updater and pass it your bot's token.

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ACTION: [MessageHandler(Filters.text, choose_action)],
            DOWNLOAD_PHOTO_REQUEST: [MessageHandler(Filters.text, download_and_send_photo)],
            DOWNLOAD_STORIES_REQUEST: [MessageHandler(Filters.text, download_and_send_stories)],
            GET_ACCOUNT_INFORMATION: [MessageHandler(Filters.text, send_about_profile)],
            MENU: [MessageHandler(Filters.text, menu)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("cancel", cancel))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
