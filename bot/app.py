import os
from threading import Thread

from telegram.ext import Updater

import config
from init_users import init_users
from bot_modules import common, stats, errors

updater = Updater(token=config.telegram_token, use_context=True)
dispatcher = updater.dispatcher


if __name__ == '__main__':
    init_users()

    dispatcher.add_handler(common.authorize_handler)
    dispatcher.add_handler(stats.stats_handler)

    Thread(target=errors.errors_mailing).start()

    updater.start_polling()
    updater.idle()
