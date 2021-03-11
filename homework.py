import os
import time

import logging
import requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='main.log',
    filemode='w'
)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] != 'approved':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
        )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    token = PRAKTIKUM_TOKEN
    # Делаем запрос к API Яндекс.
    homework_statuses = requests.get(
        'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
        headers={'Authorization': f'OAuth {token}'},
        params={'from_date': current_timestamp}
    )
    return homework_statuses.json()


def send_message(message, bot_client):
    text = message
    chat_id = CHAT_ID
    logging.info('Сообщение отправлено.')
    return bot_client.send_message(chat_id, text)


def main():
    # Проинициализировать бота здесь.
    bot_client = Bot(token=TELEGRAM_TOKEN)
    logging.debug('Бот запущен.')
    current_timestamp = int(time.time())  # Начальное значение timestamp.

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot_client
                )
            # Обновить timestamp.
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp
            )
            time.sleep(600)  # Опрашивать раз в десять минут.

        except Exception as e:
            text = f'Бот столкнулся с ошибкой: {e}'
            logging.error(text)
            send_message(text, bot_client)
            time.sleep(5)


if __name__ == '__main__':
    main()
