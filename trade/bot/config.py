from settings import API_SECRET, API_KEY
from trade.bot.api import Binance
from database.models import SettingValue
from trade.bot.logger import logger

api = Binance(
    API_KEY=API_KEY,
    API_SECRET=API_SECRET
)

limits = api.exchangeInfo()

USE_OPEN_CANDLES = True

slugs = {
    'apo_sma_p': 'apo_sma_p',
    'APO_NUM_PERIODS_FAST': 'APO_NUM_PERIODS_FAST',
    'APO_NUM_PERIODS_SLOW': 'APO_NUM_PERIODS_SLOW',
    'APO_VALUE_FOR_BUY_ENTRY': 'APO_VALUE_FOR_BUY_ENTRY',

    'klines_limits': 'klines_limits',
    'points_to_enter': 'points_to_enter',
    'timeframe': 'timeframe'
}
APO_SMA_P = 'apo_sma_p'
APO_NUM_PERIODS_FAST = 'APO_NUM_PERIODS_FAST'
APO_NUM_PERIODS_SLOW = 'APO_NUM_PERIODS_SLOW'
APO_VALUE_FOR_BUY_ENTRY = 'APO_VALUE_FOR_BUY_ENTRY'
KLINES_LIMITS = 'klines_limits'
POINTS_TO_ENTER = 'points_to_enter'
TIMEFRAME = 'timeframe'


def get_klines_limits():
    klines_limits = SettingValue.query.filter_by(slug=slugs['klines_limits']).one_or_none()
    if klines_limits:
        klines_limits = int(klines_limits.value)
    else:
        klines_limits = 200
        logger(description="klines_limits не найден, установленно значание 200")
        SettingValue.create('klines_limits', '200')
    return klines_limits


def get_points_to_enter():
    points_to_enter = SettingValue.query.filter_by(slug=slugs['points_to_enter']).one_or_none()
    if points_to_enter:
        points_to_enter = float(points_to_enter.value)
    else:
        points_to_enter = 7
        logger(description="points_to_enter не найден, установленно значание 7")
        SettingValue.create('points_to_enter', '7')
    return points_to_enter


def get_timeframe():
    timeframe = SettingValue.query.filter_by(slug=slugs['timeframe']).one_or_none()
    if not timeframe:
        timeframe = '1d'
        logger(description="timeframe не найден, установленно значание 1d")
        SettingValue.create('timeframe', '1d')
    else:
        timeframe = timeframe.value
    return timeframe


def get_setting_value(slug, default, value_type):
    value = SettingValue.query.filter_by(slug=slug).one_or_none()
    if not value:
        value = value_type(default)
        logger(description=f"{slug} не найден, установленно значание {default}")
        SettingValue.create(f"{slug}", f"{default}")
        return value
    else:
        value = value_type(value.value)
    return value
