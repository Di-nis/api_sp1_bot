import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_PRAKTIKUM = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
proxy = telegram.utils.request.Request(proxy_url='HTTPS://18.130.89.239:80')
bot = telegram.Bot(token=TELEGRAM_TOKEN, request=proxy)
logger = logging.getLogger('my_logger')


def parse_homework_status(homework):
    homework_status = homework.get('status')
    homework_name = homework.get('homework_name')
    if homework_status is None or homework_name is None:
        logger.error(f'Неверный ответ сервера: {homework}')
        return 'Неверный ответ сервера'
    if homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp=None):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get('{}'.format(API_PRAKTIKUM),
                                         headers=headers,
                                         params=params)
    except Exception as e:
        logger.error(f'Ошибка соедиения с Практикум {e}')
    return homework_statuses.json()


def send_message(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        logger.error(f'Ошибка соедиения с Telegram: {e}')
        return {}
    return bot.send_message(chat_id=CHAT_ID, text=text)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')
            time.sleep(1200)

        except Exception as e:
            logging.exception(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
