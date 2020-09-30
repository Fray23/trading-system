import statistics as stat
import math
import pandas as pd
import bot.analysis.moving_average as ta
from bot.config import USE_OPEN_CANDLES, get_points_to_enter
from bot.logger import logger


def _analysis(klines):
    klines = klines[:len(klines) - int(not USE_OPEN_CANDLES)]

    closes = [float(x[4]) for x in klines]
    high = [float(x[2]) for x in klines]
    low = [float(x[3]) for x in klines]

    # Скользящая средняя
    sma_5 = ta.SMA(closes, 5)
    sma_100 = ta.SMA(closes, 100)

    ema_5 = ta.EMA(closes, 5)
    ema_100 = ta.EMA(closes, 100)

    enter_points = 0

    if ema_5[-1] > ema_100[-1] and sma_5[-1] > sma_100[-1]:
        # Быстрая EMA выше медленной и быстрая SMA выше медленной, считаем, что можно входить
        enter_points += 1

    macd, macdsignal, macdhist = ta.MACD(closes, 12, 26, 9)
    if macd[-1] > macdsignal[-1] and macdhist[-1] > 0:
        # Линия макд выше сигнальной и на гистограмме они выше нуля
        enter_points += 1.3

    rsi_9 = ta.RSI(closes, 9)
    rsi_14 = ta.RSI(closes, 14)
    rsi_21 = ta.RSI(closes, 21)

    if rsi_9[-1] < 70 and rsi_14[-1] < 70 and rsi_21[-1] < 70:
        # RSI не показывает перекупленности
        enter_points += 2

    fast, slow = ta.STOCH(high, low, closes, 5, 3, 3)
    if fast[-1] > slow[-1]:
        # Быстрая линия стохастика выше медленной, вход
        enter_points += 1.5

    fast, slow = ta.STOCHRSI(closes, 14, 3, 3)
    if fast[-1] > slow[-1]:
        # Быстрая линия STOCHRSI выше медленной, вход
        enter_points += 1.8

    upper, middle, lower = ta.BBANDS(closes, ma_period=21)
    if high[-1] > upper[-1]:
        # Свеча пробила верхнюю полосу Боллинджера
        enter_points += 3
    points_to_enter = get_points_to_enter()

    log_data = {
        'description': f"Свеча набрала {enter_points} баллов, минимум {points_to_enter}",
        'log_type': 'debug',
    }
    logger(**log_data)
    return enter_points < points_to_enter


def analysis(klines,
        sma_p=17,
        NUM_PERIODS_FAST=6,
        NUM_PERIODS_SLOW=24,
        APO_VALUE_FOR_BUY_ENTRY=-5,
        ):
    closes = [float(x[4]) for x in klines]
    timestamp_open_list = [float(x[1]) for x in klines]
    high_list = [float(x[2]) for x in klines]
    low_list = [float(x[3]) for x in klines]
    timestamp_close_list = [float(x[6]) for x in klines]
    data = []

    for op, close, high, low in zip(timestamp_open_list, closes, high_list, low_list):
        data.append({'open': op, 'close': close, 'high': high, 'low': low})
    data = pd.DataFrame(data, index=timestamp_close_list)

    price_history = []

    K_FAST = 2 / (NUM_PERIODS_FAST + 1)
    ema_fast = 0
    ema_fast_values = []

    K_SLOW = 2 / (NUM_PERIODS_SLOW + 1)
    ema_slow = 0
    ema_slow_values = []

    apo_valus = []
    stdev_factors = []
    close = data['close']
    for close_price in close:
        price_history.append(close_price)
        if len(price_history) > sma_p:
            del price_history[0]
        sma = stat.mean(price_history)

        variance = 0
        for hist_price in price_history:
            variance = variance + ((hist_price - sma) ** 2)
        stdev = math.sqrt(variance / len(price_history))
        stdev_factor = stdev / 15
        if stdev_factor == 0:
            stdev_factor = 1
        stdev_factors.append(stdev_factor)

        if ema_fast == 0:
            ema_fast = close_price
            ema_slow = close_price
        else:
            ema_fast = (close_price - ema_fast) * K_FAST * stdev_factor + ema_fast
            ema_slow = (close_price - ema_slow) * K_SLOW * stdev_factor + ema_slow

        ema_fast_values.append(ema_fast)
        ema_slow_values.append(ema_slow)
        apo = ema_fast - ema_slow
        apo_valus.append(apo)

    apo = apo_valus[-1]
    stdev_factor = stdev_factors[-1]

    trand = ema_slow_values[-1] > ema_slow_values[-2] > ema_slow_values[-3]
    buy = apo < APO_VALUE_FOR_BUY_ENTRY * stdev_factor and trand

    log_data = {
        'description': f"trand {trand} and {apo} < {APO_VALUE_FOR_BUY_ENTRY * stdev_factor}, res:{buy}",
        'log_type': 'debug',
    }
    logger(**log_data)
    return buy
