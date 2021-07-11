
from telegram.ext import CommandHandler

from src.database import news_db_col


def access_control(func):
    def inner(update, context):
        if context.user_data.get('access'):
            func(update, context)
    return inner


@access_control
def stats(update, context):
    sources_list = [
        'aif', 'bfm', 'echo', 'icmos', 'interfax', 'kommersant', 'kp', 'lenta', 'm24', 'mbk', 'mk', 'mockva',
        'moslenta', 'mskagency', 'novayagazeta', 'pravda', 'rbc', 'regnum', 'rg', 'ria', 'riamo', 'rt', 'tass',
        'tvrain', 'vm', 'mn', 'bezformata_msk', 'bezformata_podmoskovye', 'inregiontoday', 'molnet', 'moscow_ru_today',
        'mosday', 'moskva_tyt', 'mosreg', 'mperspektiva', 'msk_news', 'msknovosti',
    ]
    text = f'Отчёт о колличестве новостей\n' \
           f'Всего новостей - {news_db_col.count()}\n'
    for source in sources_list:
        text += f"{source} - {news_db_col.find({'source': source}).count()}\n"
    update.effective_chat.send_message(text)


stats_handler = CommandHandler('stats', stats)
