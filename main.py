"""
KIT Mensa Bot
"""
import datetime
import logging
import os

import pytz
from colorama import Fore, Style
from telegram.ext import Updater

import config
from controller.controller import callback_daily_update, Controller
from model.model import Mensa


def main():
    """
    Main method for running bot server.
    """
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    # JOB: Create mensa object
    mensa = Mensa()
    print(f'\nServing menu for {Style.BRIGHT}{mensa.get_info().get("name")}{Style.RESET_ALL}')

    # JOB: Create Updater and Controller instance
    print('\nCreating Updater ...')

    # Read token string from text file
    with open(os.path.join(config.ROOT_DIR, 'data/connection_token.txt'), 'r') as f:
        token = f.read()

    updater = Updater(token=token, use_context=True)
    print(
        f'Successfully created Updater with username {Style.BRIGHT}{updater.bot.username}{Style.RESET_ALL} '
        f'and display name {Style.BRIGHT}{updater.bot.first_name}{Style.RESET_ALL}.')
    dispatcher = updater.dispatcher
    controller = Controller(dispatcher)
    controller.register_handlers()
    queue = updater.job_queue

    # JOB: Schedule daily menu update message
    job_daily_update = queue.run_daily(time=datetime.time(hour=17, minute=56, second=0, tzinfo=pytz.timezone('CET')),
                                       callback=callback_daily_update)

    # JOB: Start bot
    updater.start_polling()
    if updater.running:
        print('Bot started.')
    updater.idle()


if __name__ == '__main__':
    main()
