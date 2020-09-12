import flaskr.bot.analysis.moving_average as ta
from flaskr.config import USE_OPEN_CANDLES, POINTS_TO_ENTER, log


def analysis(klines):
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

    log.debug("Свеча набрала {b} баллов, минимум {p}".format(b=enter_points, p=POINTS_TO_ENTER))
    return enter_points < POINTS_TO_ENTER
