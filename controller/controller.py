import datetime

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, \
    ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler
from emoji import emojize

import config
from model.model import Mensa


class Controller:
    def __init__(self, dispatcher):
        """

        :param dispatcher:
        """
        self.dispatcher = dispatcher

    def register_handlers(self):
        # JOB: Create function handlers
        start_handler = CommandHandler('start', start)
        inline_handler = InlineQueryHandler(inline)
        help_handler = CommandHandler('help', help)
        today_handler = CommandHandler('today', today)
        tomorrow_handler = CommandHandler('tomorrow', tomorrow)
        l6_today_handler = CommandHandler('l6_today', l6_today)
        l6_tomorrow_handler = CommandHandler('l6_tomorrow', l6_today)
        poll_handler = CommandHandler('daily_poll', daily_poll)
        unknown_handler = MessageHandler(Filters.command, unknown)

        # JOB: Add handlers to dispatcher
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(help_handler)
        self.dispatcher.add_handler(inline_handler)
        self.dispatcher.add_handler(CallbackQueryHandler(button))
        self.dispatcher.add_handler(today_handler)
        self.dispatcher.add_handler(tomorrow_handler)
        self.dispatcher.add_handler(l6_today_handler)
        self.dispatcher.add_handler(l6_tomorrow_handler)
        self.dispatcher.add_handler(poll_handler)
        self.dispatcher.add_handler(unknown_handler)


def start(update, context):
    """
    Start bot

    :param update:
    :param context:
    :return: None
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome to MensaBot!')

    keyboard = [[InlineKeyboardButton('Today\'s Menu', callback_data='daily'),
                 InlineKeyboardButton('Poll', callback_data='daily_poll')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def get_daily_menu(update, context, chat_id, l6=False):
    text = ''

    if context.user_data is not None:
        offset = context.user_data['offset']
    else:
        offset = 0

    date = (datetime.date.today() + datetime.timedelta(days=offset))

    if not l6:
        text = f'*{Mensa().get_info().get("name")}* {emojize(":fork_and_knife:", use_aliases=True)}\n' \
               f'*Menu for {date.strftime("%A, %B %d, %Y")}*\n'
        whitelist = ['Linie']

    else:
        print('L6')
        whitelist = ['L6 Update']

    line_data = [(line, contents) for line, contents in
                 Mensa().meal_data_lines(offset=offset)]

    for line, contents in line_data:
        contents = contents.loc[line].reset_index().apply(
            lambda
                x: f'▫ {x["name"]} {x["symbol"]}',
            axis=1).tolist()  # TODO: Add number emojis to lines

        if any(e in line for e in whitelist):
            text += f'\n\n*{line}*:\n' + '\n'.join(contents)

    context.bot.send_message(chat_id=chat_id,
                             text=text,
                             parse_mode=telegram.ParseMode.MARKDOWN)
    context.bot.send_message(chat_id=chat_id,
                             text=f'<a href="https://openmensa.org/c/31/{date}">Full menu</a>',
                             parse_mode=telegram.ParseMode.HTML)

    if offset == 0:
        keyboard = [[InlineKeyboardButton('Tomorrow\'s Menu', callback_data='tomorrow')]]
        keyboard[0].append(InlineKeyboardButton('L6 Menu', callback_data='l6_today'))
        keyboard[0].append(InlineKeyboardButton('Schedule', callback_data='daily_poll'))
    else:
        keyboard = [[InlineKeyboardButton('Today\'s Menu', callback_data='today')]]
        keyboard[0].append(InlineKeyboardButton('L6 Menu', callback_data='l6_tomorrow'))
        keyboard[0].append(InlineKeyboardButton('Schedule', callback_data='daily_poll'))

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text='Further info:', reply_markup=reply_markup)


def today(update, context):
    """
    Show daily menu
    """
    context.user_data['offset'] = 0
    get_daily_menu(update, context, chat_id=update.effective_chat.id)


def l6_today(update, context):
    """
    """
    context.user_data['offset'] = 0
    get_daily_menu(update, context, chat_id=update.effective_chat.id, l6=True)


def l6_tomorrow(update, context):
    """
    """
    context.user_data['offset'] = 1
    get_daily_menu(update, context, chat_id=update.effective_chat.id, l6=True)


def tomorrow(update, context):
    """
    Show daily menu
    """
    context.user_data['offset'] = 1
    get_daily_menu(update, context, update.effective_chat.id)


def callback_daily_update(context: telegram.ext.CallbackContext):
    get_daily_menu(update=None, context=context, chat_id=-1001463530288)


def daily_poll(update, context, chat_id=None):
    """
    Send daily_poll
    """

    if chat_id is None:
        chat_id = update.effective_chat.id

    options = ['11:40 Uhr', '12:10 Uhr', '12:40 Uhr', '13:10 Uhr', '13:30 Uhr', '13:50 Uhr',
               'Other']

    config.CURRENT_POLL = send_poll(context=context, chat_id=chat_id,
                                    question='What time do you want to have lunch today?',
                                    options=options,
                                    disable_notification=True, is_anonymous=True, allows_multiple_answers=True)

    keyboard = [[InlineKeyboardButton('Close Poll', callback_data='close_poll')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text='Click below to close poll:', reply_markup=reply_markup)


def send_poll(context,
              chat_id,
              question,
              options,
              disable_notification=None,
              reply_to_message_id=None,
              reply_markup=None,
              timeout=None,
              **kwargs):
    """
    Use this method to send a native daily_poll. A native daily_poll can't be sent to a private chat.
    """
    url = '{0}/sendPoll'.format(context.bot.base_url)

    data = {
        'chat_id': chat_id,
        'question': question,
        'options': options
    }

    data.update(kwargs)

    return context.bot._message(url, data, timeout=timeout, disable_notification=disable_notification,
                                reply_to_message_id=reply_to_message_id, reply_markup=reply_markup)


def close_poll(update, context):
    return context.bot.stop_poll(chat_id=update.effective_chat.id, message_id=config.CURRENT_POLL.message_id)


def inline(update, context):
    """
    Example for inline capabilities
    """
    query = update.inline_query.query
    if not query:
        return

    print(query)
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Action',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)


def help(update, context):
    update.message.reply_text('Help!')
    # context.bot.send_message(chat_id=update.effective_chat.id, text='Test')


def button(update, context) -> None:
    """
    Handle button press
    """
    query = update.callback_query
    # query.edit_message_text(text=f'Selected option: {query.data.capitalize()}')
    if query.data == 'daily':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Showing today\'s menu.')
        today(update, context)

    elif query.data == 'daily_poll':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Poll')
        daily_poll(update, context, chat_id=update.effective_chat.id)

    elif query.data == 'tomorrow':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Showing tomorrow\'s menu.')
        tomorrow(update, context)

    elif query.data == 'l6_today':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Showing today\'s L6 menu.')
        l6_today(update, context)

    elif query.data == 'l6_tomorrow':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Showing tomorrow\'s L6 menu.')
        l6_tomorrow(update, context)

    elif query.data == 'close_poll':
        config.POLL_RESULTS = close_poll(update, context).to_dict()
        context.bot.send_message(chat_id=update.effective_chat.id, text='Results:')

        option_votes = [f'{option["text"]}: {option["voter_count"]}' for option in config.POLL_RESULTS['options']]
        message = f'*{config.POLL_RESULTS["question"]}*\n\n' + '\n'.join(option_votes)
        context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Sorry, I didn\'t understand that command.')
