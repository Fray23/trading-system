from bot.api import Binance
from web.flaskr.models import SettingValue
from bot.logger import logger

api = Binance(
)

limits = api.exchangeInfo()

USE_OPEN_CANDLES = True


def get_klines_limits():
    klines_limits = SettingValue.query.filter_by(slug='klines_limits').one_or_none()
    if klines_limits:
        klines_limits = int(klines_limits.value)
    else:
        klines_limits = 200
        logger(description="klines_limits не найден, установленно значание 200")
        SettingValue.create('klines_limits', '200')
    return klines_limits


def get_points_to_enter():
    points_to_enter = SettingValue.query.filter_by(slug='points_to_enter').one_or_none()
    if points_to_enter:
        points_to_enter = float(points_to_enter.value)
    else:
        points_to_enter = 7
        logger(description="points_to_enter не найден, установленно значание 7")
        SettingValue.create('points_to_enter', '7')
    return points_to_enter


def get_timeframe():
    timeframe = SettingValue.query.filter_by(slug='timeframe').one_or_none()
    if not timeframe:
        timeframe = '1d'
        logger(description="timeframe не найден, установленно значание 1d")
        SettingValue.create('timeframe', '1d')
    else:
        timeframe = timeframe.value
    return timeframe
