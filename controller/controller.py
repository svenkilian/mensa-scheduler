import datetime
from math import ceil

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, \
    ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackQueryHandler
from emoji import emojize

import config
from model.model import Mensa, PollData
from utils.utils import is_int


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
        schedule_handler = CommandHandler('schedule', schedule)
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
        self.dispatcher.add_handler(schedule_handler)
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
                 InlineKeyboardButton('Schedule', callback_data='daily_poll')]]

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
    # get_daily_menu(update=None, context=context, chat_id=-1001463530288)
    get_daily_menu(update=None, context=context, chat_id=-1001316049000)


def daily_poll(update, context):
    """
    Send daily_poll
    """

    schedule(update, context)


def schedule(update, context):
    options = ['11:40 Uhr', '12:10 Uhr', '12:40 Uhr', '13:10 Uhr', '13:30 Uhr', '13:50 Uhr']
    context.chat_data['options'] = options

    n_rows = ceil(len(options) / 3)
    keyboard = [[] for _ in range(n_rows)]
    for num, option in enumerate(options):
        row_index = num // 3
        print(row_index)
        keyboard[row_index].append(InlineKeyboardButton(option, callback_data=f'option_{num}'))

    keyboard.append([InlineKeyboardButton('Delete all', callback_data=f'option_delete')])
    keyboard.append([InlineKeyboardButton('Deal me out', callback_data=f'option_declined')])
    options.append('Out')

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.chat_data['current_poll'] = PollData(options)

    context.bot.send_message(chat_id=update.effective_chat.id, text='Please choose:', reply_markup=reply_markup)


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
            id=query,
            title='/schedule',
            input_message_content=InputTextMessageContent(query)
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
        daily_poll(update, context)

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

    elif query.data.startswith('option'):
        # print(query)

        option_list = context.chat_data['options']
        option_chosen = query.data.split('_')[-1]

        # JOB: Register vote
        if is_int(option_chosen):
            option_chosen = int(option_chosen)
            context.chat_data['current_poll'].set_choice(user_first_name=query.from_user.first_name,
                                                         option=option_list[option_chosen])
        else:
            if option_chosen == 'declined':
                context.chat_data['current_poll'].data.loc[
                    query.from_user.first_name, 'Out'] = 1
                context.chat_data['current_poll'].delete_user(query.from_user.first_name, times_only=True)
            elif option_chosen == 'delete':
                context.chat_data['current_poll'].delete_user(query.from_user.first_name)

        # context.bot.send_message(chat_id=update.effective_chat.id, text=f'*{query.from_user.username}: {query.data}*',
        #                          parse_mode=telegram.ParseMode.MARKDOWN)

        try:
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=query.message.message_id,
                                          text=context.chat_data['current_poll'].get_results(),
                                          reply_markup=query.message.reply_markup)
        except telegram.error.BadRequest as bre:
            print('Message did not change.')
        except telegram.error.TimedOut as toe:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f'Timed out. Request sent by {query.from_user.first_name}',
                                     parse_mode=telegram.ParseMode.MARKDOWN)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Sorry, I didn\'t understand that command.')
