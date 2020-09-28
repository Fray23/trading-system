import time
import datetime

from bot.analysis.analysis import analysis
from web.flaskr import db_session as session
from bot.logger import logger, log
from web.flaskr.models import Order, PairSetting, SettingValue
from sqlalchemy import or_, and_

from bot.config import api, get_timeframe, get_klines_limits
from bot.utils import adjust_to_step, calc_buy_avg_rate, get_order_trades

limits = api.exchangeInfo()


class OrderSimple:
    def __init__(self, order):
        self.obj = order
        self.pair = order.pair

        if order.order_type.lower() == 'sell':
            self.order_id = order.sell_order_id
            self.amount = order.sell_amount
            self.price = order.sell_price
            self.finished = order.sell_finished
            self.verified = order.sell_verified
            self.order_type = order.order_type
        else:
            self.order_id = order.buy_order_id
            self.amount = order.buy_amount
            self.price = order.buy_price
            self.finished = order.buy_finished
            self.verified = order.buy_verified
            self.order_type = order.order_type


def get_running_orders():
    opens = session.query(Order).filter(
        Order.buy_cancelled == None, or_(and_(Order.order_type == 'buy', Order.buy_finished == None),
                                         and_(Order.order_type == 'sell', Order.sell_finished == None)))
    res = []
    for order in opens:
        res.append(OrderSimple(order))
    return res


def get_pairs():
    all_pairs = {}
    for pair in PairSetting.query.filter_by(active=True).all():
        all_pairs[pair.quote.upper() + pair.base.upper()] = {
            'base': pair.base,
            'quote': pair.quote,
            'spend_sum': pair.spend_sum,
            'profit_markup': pair.profit_markup,
            'use_stop_loss': pair.use_stop_loss,
            'stop_loss': pair.stop_loss,
            'active': pair.active
        }
    return all_pairs


class OrderProcess:
    def __init__(self, order_id, pair, order_data):
        self.order_id = order_id
        self.pair = pair
        self.order_data = order_data

    def get_limit(self):
        for elem in limits['symbols']:
            if elem['symbol'] == self.pair:
                return elem
        else:
            raise Exception("Не удалось найти настройки выбранной пары " + self.pair)

    def update_rate(self, method):
        order_trades = get_order_trades(
            order_id=self.order_id,
            pair=self.pair,
            api=api
        )

        avg_rate = calc_buy_avg_rate(order_trades, log)
        if avg_rate > 0:
            if method == 'buy':
                data = {
                    'buy_verified': True,
                    'buy_price': avg_rate
                }
                session.query(Order).filter(Order.buy_order_id == self.order_id).update(data)
                session.commit()
            elif method == 'sell':
                data = {
                    'sell_verified': True,
                    'sell_price': avg_rate,
                    'sell_finished': datetime.datetime.utcnow()
                }
                session.query(Order).filter(Order.sell_order_id == self.order_id).update(data)
                session.commit()
            else:
                raise Exception('argument error')
        else:
            raise Exception('Не удается вычислить цену покупки, пропуск')

    def get_qty(self):
        got_qty = float(self.order_data['executedQty'])
        got_qty = got_qty - (got_qty / 100) * 0.1
        got_qty = adjust_to_step(got_qty, self.get_limit()['filters'][2]['stepSize'])
        return got_qty

    def get_bit_price(self):
        prices = api.tickerBookTicker(
            symbol=self.pair
        )
        return float(prices['bidPrice'])

    def get_ask_price(self):
        prices = api.tickerBookTicker(
            symbol=self.pair
        )
        return float(prices['askPrice'])

    def price_change(self, curr_rate, buy_price):
        price_change = (curr_rate/buy_price -1)*100
        return price_change

    def create_order(self, side, recvWindow, quantity, price=0.):
        quantity = float(quantity)
        new_order = api.createOrder(
            symbol=self.pair,
            recvWindow=recvWindow,
            side=side,
            type='MARKET',
            quantity="{quantity:0.{precision}f}".format(
                quantity=quantity, precision=self.get_limit()['baseAssetPrecision']
            ),
            newOrderRespType='FULL'
        )
        if 'orderId' in new_order:
            if side.lower() == 'buy':
                self.order_id = new_order['orderId']
                logger(description=f"Создан ордер на покупку id:{new_order['orderId']} \
                    price: {price},quantity: {quantity}",
                       log_type='info')
                order = Order(
                    order_type='buy',
                    pair=self.pair,
                    buy_order_id=new_order['orderId'],
                    buy_amount=quantity,
                    buy_price=price
                )
                session.add(order)
                session.commit()
                self.update_rate(method='buy')
            elif side.lower() == 'sell':
                logger(description=f"Создан ордер на продажу по рынку {new_order}", log_type='info',)
                session.query(Order).filter_by(
                    buy_order_id=self.order_id
                ).update({
                    'order_type': side.lower(),
                    'sell_finished': datetime.datetime.utcnow(),
                    'sell_created': datetime.datetime.utcnow(),
                    'sell_order_id': new_order['orderId'],
                    'sell_amount': quantity,
                    'sell_price': price
                })
                session.commit()
                self.update_rate(method='sell')
        else:
            raise Exception('error order doesn\'t create')

        return new_order


def run():
    _run = SettingValue.query.filter_by(slug='run').one_or_none()
    if _run is None:
        svalue = SettingValue(slug='run', value='0')
        session.add(svalue)
        session.commit()
    return _run and int(_run.value) == 1


def request_pause():
    _pause = SettingValue.query.filter_by(slug='pause').one_or_none()
    if _pause:
        return int(_pause.value)
    else:
        svalue = SettingValue(slug='pause', value='60')
        session.add(svalue)
        session.commit()
    return 60


def main_flow():
    while True:
        time.sleep(request_pause())
        if not run():
            logger(description='no run', log_type='no')
            continue
        open_orders = get_running_orders()
        all_pairs = get_pairs()

        if open_orders:
            for order in open_orders:

                order_trade_data = api.orderInfo(symbol=order.pair, orderId=order.order_id)

                if 'status' not in order_trade_data:
                    logger(
                        description='\'status\' not in order_trade_data, pair={order.pair}, orderId={order.order_id}',
                        log_type='warning'
                    )
                    continue
                order_status = order_trade_data['status']
                order_type = order.order_type
                pair = order.pair

                profit_markup = all_pairs[order_trade_data['symbol']]['profit_markup']
                sell_verified = order.obj.sell_verified
                use_stop_loss = all_pairs[pair]['use_stop_loss']
                stop_loss = all_pairs[pair]['stop_loss']

                order_process = OrderProcess(
                    order_id=order.order_id,
                    pair=order.pair,
                    order_data=order_trade_data,
                )

                if order.order_type == 'buy':
                    if not order.verified:
                        order_process.update_rate(method='buy')

                    if order_status == 'FILLED':
                        got_qty = order_process.get_qty()
                        bit_price = order_process.get_bit_price()
                        price_change = order_process.price_change(bit_price, order.obj.buy_price)
                        logger(description=f"Цена изменилась на {price_change}%, процент для продажи {all_pairs[pair]['profit_markup']}", log_type='info')

                        if price_change >= profit_markup:
                            order_process.create_order(side='SELL', recvWindow=5000, quantity=got_qty)

                if order_type == 'sell' and not sell_verified:
                    order_process.update_rate(method='sell')

                if use_stop_loss and order_status == 'FILLED' and order_type == 'buy':
                    curr_rate = float(api.tickerPrice(symbol=pair)['price'])
                    buy_price = order.obj.buy_price,

                    if (1 - curr_rate / buy_price[0]) * 100 >= stop_loss:
                        logger(
                            description=f"{pair} Цена упала до стоплосс (покупали по {buy_price}, сейчас {curr_rate}),\
                             пора продавать, процент для продажи {stop_loss}",
                            log_type='info')
                        buy_amount = order_process.get_qty()
                        order_process.create_order(side='SELL', quantity=buy_amount, recvWindow=15000)

        for order in get_running_orders():
            del all_pairs[order.pair]

        if all_pairs:
            logger(
                description=f'Найдены пары, по которым нет неисполненных ордеров: {all_pairs.keys()}',
                log_type='debug')

            for pair, pair_obj in all_pairs.items():
                timeframe = get_timeframe()
                klines_limits = get_klines_limits()
                klines = api.klines(
                    symbol=pair.upper(),
                    interval=timeframe,
                    limit=klines_limits
                )
                order_process = OrderProcess(
                    order_id=None,
                    pair=pair,
                    order_data=None,
                )
                spend_sum = pair_obj['spend_sum']
                base_currency = pair_obj['base']
                top_price = order_process.get_ask_price()

                CURR_LIMITS = order_process.get_limit()
                stepSize = CURR_LIMITS['filters'][2]['stepSize']
                minQty = CURR_LIMITS['filters'][2]['minQty']
                minNotional = CURR_LIMITS['filters'][3]['minNotional']

                if analysis(klines=klines):
                    continue

                balances = {
                    balance['asset']: float(balance['free']) for balance in api.account()['balances']
                    if balance['asset'] in [pair_obj['base'], pair_obj['quote']]
                }
                logger(
                    description=f"Баланс {balances}",
                    log_type='debug')

                if balances[base_currency] >= spend_sum:
                    my_amount = adjust_to_step(spend_sum / top_price, stepSize)

                    if my_amount < float(stepSize) or my_amount < float(minQty):

                        logger(
                            description="Покупка невозможна, выход. Увеличьте размер ставки",
                            log_type='warning')
                        continue

                    trade_am = top_price * my_amount
                    if trade_am < float(minNotional):
                        raise Exception("""меньше допустимого по паре {min_am:0.8f}. минимальная сумма торгов {incr}""".format(
                            trade_am=trade_am,
                            min_am=float(minNotional),
                            incr=minNotional
                        ))
                    order_process.create_order(recvWindow=5000, side='BUY', quantity=my_amount, price=top_price)
