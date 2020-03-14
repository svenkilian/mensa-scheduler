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
from controller.controller import callback_daily_update, Controller, callback_daily_results
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

    updater = Updater(token=token, use_context=True, request_kwargs={'read_timeout': 20, 'connect_timeout': 20})
    print(
        f'Successfully created Updater with username {Style.BRIGHT}{updater.bot.username}{Style.RESET_ALL} '
        f'and display name {Style.BRIGHT}{updater.bot.first_name}{Style.RESET_ALL}.')
    dispatcher = updater.dispatcher
    controller = Controller(dispatcher)
    controller.register_handlers()
    queue = updater.job_queue

    # JOB: Schedule daily menu update message
    job_daily_update = queue.run_daily(time=datetime.time(hour=9, minute=30, second=30, tzinfo=pytz.timezone('CET')),
                                       callback=callback_daily_update)

    job_daily_results = queue.run_daily(time=datetime.time(hour=11, minute=0, second=10, tzinfo=pytz.timezone('CET')),
                                        callback=callback_daily_results)

    # JOB: Start bot
    updater.start_polling()
    if updater.running:
        print('Bot started.')
    updater.idle()


if __name__ == '__main__':
    main()
