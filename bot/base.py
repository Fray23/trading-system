from sqlalchemy import and_
from bot.bot import OrderProcess
from bot.config import api
from web.flaskr import db_session as session
from web.flaskr.models import Order


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
    opens_sell = session.query(Order).filter(and_(Order.order_type == 'sell', Order.sell_finished == None))
    res = []
    for order in opens_sell:
        res.append(OrderSimple(order))
    return res


def sell_last_trade(order_id, pair):
    for order in get_running_orders():
        order_trade_data = api.orderInfo(symbol=order.pair, orderId=order.order_id)
        order_process = OrderProcess(
            order_id=order_id,
            pair=pair,
            order_data=order_trade_data
        )
        got_qty = order_process.get_qty()
        order_process.create_order(side='SELL', recvWindow=5000, quantity=got_qty)
