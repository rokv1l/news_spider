import time

from app import messaging_list, dispatcher
from src.database import errors_db_col


def errors_mailing():
    while True:
        cursor = errors_db_col.find_all({'checked': False})
        errors = set()
        for i in cursor:
            errors_db_col.update_one(i, {'$set': {'checked': True}})
            errors.add(i['error'])
        text = '\n-------------------------------\n'.join(errors)
        for _id in messaging_list:
            dispatcher.bot.send_message(
                chat_id=_id,
                text=text
            )
        time.sleep(60*60)
