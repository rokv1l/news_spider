
from telegram.ext import CommandHandler

from src.database import news_db_col


def access_control(func):
    def inner(update, context):
        if context.user_data.get('access'):
            func(update, context)
    return inner


@access_control
def stats(update, context):
    text = f'Отчёт о колличестве новостей\n' \
           f'Всего новостей - {news_db_col.count()}\n'
    update.effective_chat.send_message(text)


stats_handler = CommandHandler('stats', stats)
