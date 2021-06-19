from hashlib import sha256

from src.database import news_db_col


def init_users():
    with open("users.csv", 'r', encoding='utf-8') as users_file:
        lines = users_file.readlines()
        users_passwords = [row.replace('\n', '') for row in lines if row.replace('\n', '') != 'Пароль']
        # for row in lines:
        #     if row.replace('\n', '') != 'Пароль':
        #         users_passwords.append(row.replace('\n', ''))

    for password in users_passwords:
        if not news_db_col.find_one({'password': sha256(password.encode('utf-8')).hexdigest()}):
            news_db_col.insert_one({'password': sha256(password.encode('utf-8')).hexdigest()})
