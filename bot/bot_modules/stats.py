from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters

from src.database import news_db_col


def stats(update: Update, context):

    sources_list = [
        'aif', 'bfm', 'echo', 'icmos', 'interfax', 'kommersant', 'kp', 'lenta', 'm24', 'mbk', 'mk', 'mockva',
        'moslenta', 'mskagency', 'novayagazeta', 'pravda', 'rbc', 'regnum', 'rg', 'ria', 'riamo', 'rt', 'tass',
        'tvrain', 'vm'
    ]
    text = f'Отчёт о колличестве новостей\n' \
           f'Всего новостей - {news_db_col.count()}\n'
    for source in sources_list:
        text += f"{source} - {news_db_col.find({'source': source}).count()}\n"
    update.effective_chat.send_message(text)


stats_handler = CommandHandler('stats', stats)
