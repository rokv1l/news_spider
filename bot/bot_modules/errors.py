import time

from app import dispatcher
from config import messaging_list, mailing_sleep
from src.database import errors_db_col


def errors_mailing():
    while True:
        time.sleep(mailing_sleep)
        if not messaging_list:
            continue
        cursor = errors_db_col.find({'checked': False})
        errors = set()
        for i in cursor:
            errors_db_col.update_one(i, {'$set': {'checked': True}})
            errors.add(i['error'])
        if not errors:
            continue
        text = '\n-------------------------------\n'.join(errors)
        for _id in messaging_list:
            dispatcher.bot.send_message(
                chat_id=_id,
                text=text
            )
