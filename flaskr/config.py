import os
import logging
from flaskr.bot.api import Binance

api = Binance(
)

pairs = [
#   {
#        'base': 'USDT',
#        'quote': 'BTC',
#        'spend_sum': 11,  # Сколько тратить base каждый раз при покупке quote
#        'profit_markup': 0.15, # Какой навар нужен с каждой сделки? (1=1%)
#        'use_stop_loss': False, # Нужно ли продавать с убытком при падении цены
#        'stop_loss': 1, # 1% - На сколько должна упасть цена, что бы продавать с убытком
#        'active': True,
#    },
    {
        'base': 'USDT',
        'quote': 'ETH',
        'spend_sum': 11,  # Сколько тратить base каждый раз при покупке quote
        'profit_markup': 3, # Какой навар нужен с каждой сделки? (0.001 = 0.1%)
        'use_stop_loss': False, # Нужно ли продавать с убытком при падении цены
        'stop_loss': 1, # 2%  - На сколько должна упасть цена, что бы продавать с убытком
        'active': True,
    },
    # {
    #     'base': 'USDT',
    #     'quote': 'LTC',
    #     'spend_sum': 11,  # Сколько тратить base каждый раз при покупке quote
    #     'profit_markup': 0.15, # Какой навар нужен с каждой сделки? (0.001 = 0.1%)
    #     'use_stop_loss': False, # Нужно ли продавать с убытком при падении цены
    #     'stop_loss': 1, # 2%  - На сколько должна упасть цена, что бы продавать с убытком
    #     'active': True,
    # },
    # {
    #     'base': 'USDT',
    #     'quote': 'OMG',
    #     'spend_sum': 11,  # Сколько тратить base каждый раз при покупке quote
    #     'profit_markup': 0.15, # Какой навар нужен с каждой сделки? (0.001 = 0.1%)
    #     'use_stop_loss': False, # Нужно ли продавать с убытком при падении цены
    #     'stop_loss': 1, # 2%  - На сколько должна упасть цена, что бы продавать с убытком
    #     'active': True,
    # }
]
# MARKETS = [
#     'USDT-BTC', 'USDT-BCH', 'USDT-ETC','USDT-OMG',
#     'USDT-XRP', 'USDT-LTC', 'USDT-ZEC', 'USDT-XMR', 'ex-DASH'
# ]

KLINES_LIMITS = 200
POINTS_TO_ENTER = 7

limits = api.exchangeInfo()

USE_OPEN_CANDLES = True

TIMEFRAME = "1w"
'''
    Допустимые интервалы:
    •    1m     // 1 минута
    •    3m     // 3 минуты
    •    5m    // 5 минут
    •    15m  // 15 минут
    •    30m    // 30 минут
    •    1h    // 1 час
    •    2h    // 2 часа
    •    4h    // 4 часа
    •    6h    // 6 часов
    •    8h    // 8 часов
    •    12h    // 12 часов
    •    1d    // 1 день
    •    3d    // 3 дня
    •    1w    // 1 неделя
    •    1M    // 1 месяц
'''

# Подключаем логирование
logging.basicConfig(
    format="%(asctime)s [%(levelname)-5.5s] %(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("{path}/logs/{fname}.log".format(path=os.path.dirname(os.path.abspath(__file__)), fname="binance")),
        logging.StreamHandler()
    ])
log = logging.getLogger('')
