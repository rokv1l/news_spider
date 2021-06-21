
from hashlib import sha256

from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, Filters

from config import messaging_list
from src.database import news_db_col
"""
Последнее сообщение которое требует удаления клавиатуры сохраняется в 
context.user_data['message_for_delete_keyboard']
"""
# просто константы для навигации по логике сценария
AUTHORIZE = 0


def start(update, context):
    if context.user_data.get('access'):
        update.effective_chat.send_message('Вы уже можете пользоваться возможностями бота')
        return ConversationHandler.END
    else:
        update.effective_chat.send_message('Введите пароль')
        return AUTHORIZE


def authorize(update, context):
    password = update.message.text
    user = news_db_col.find_one({'password': sha256(password.encode('utf-8')).hexdigest()})
    if user:
        context.user_data['access'] = 1
        messaging_list.append(update.effective_chat.id)
        update.effective_chat.send_message(
            'Авторизация прошла успешно.\n'
            'Вы будете получать сообщения об ошибках в этом чате и можете воспользоваться коммандой '
            '/stats что-бы узнать сколько новостей в базе данных на данный момент'
        )
        return ConversationHandler.END
    else:
        context.user_data['access'] = 0
        update.effective_chat.send_message('Такого пароля не существует, попробуйте еще раз')
        return AUTHORIZE


authorize_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        AUTHORIZE: [MessageHandler(Filters.text, authorize)],
    },
    fallbacks=[]
)
