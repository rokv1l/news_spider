import os

from telegram.ext import Updater

import config
from init_users import init_users
from bot_modules import common, stats

messaging_list = []


if __name__ == '__main__':
    init_users()

    updater = Updater(token=config.telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(common.authorize_handler)
    dispatcher.add_handler(stats.stats_handler)

    updater.start_polling()
    updater.idle()
