import time
import datetime
from trade.bot.trades import BaseTrade
from trade.bot.logger import logger

def adjust_to_step(value, step, increase=False):
   return ((int(value * 100000000) - int(value * 100000000) % int(
        float(step) * 100000000)) / 100000000)+(float(step) if increase else 0)


def calc_buy_avg_rate(order_trades, log):
    bought = 0
    spent = 0
    fee = 0
    avg_rate = 0
    for trade in order_trades:
        bought += trade.trade_amount
        spent += trade.trade_amount * trade.trade_rate
        fee += trade.trade_fee

        try:
            logger(description='По ордеру была сделка {id} на покупку {am:0.8f} по курсу {r:0.8f}, комиссия {fee:0.8f} {f_a}'.format(
                    id=trade.trade_id,
                    am=trade.trade_amount,
                    r=trade.trade_rate,
                    fee=trade.trade_fee,
                    f_a=trade.fee_type
                ),
                log_type='debug',)
            avg_rate = spent / bought
        except ZeroDivisionError:
            logger(description='Не удалось посчитать средневзвешенную цену, деление на 0',
                log_type='debug',)
            avg_rate = 0
    logger(
        description='Средневзвешенная цена {ar:0.8f}'.format(ar=avg_rate),
        log_type='debug',
    )
    return avg_rate


def calc_sell_avg_rate(order_trades, log):
    sold = 0
    got = 0
    fee = 0

    for trade in order_trades:

        sold += trade.trade_amount
        got += trade.trade_amount * trade.trade_rate
        fee += trade.trade_fee

        logger(description='По ордеру была сделка {id} на продажу {am:0.8f} по курсу {r:0.8f}, комиссия {fee:0.8f} {f_a}'.format(
                id=trade.trade_id,
                am=trade.trade_amount,
                r=trade.trade_rate,
                fee=trade.trade_fee,
                f_a=trade.fee_type
            ),
            log_type='debug',)
    try:
        avg_rate = got / sold
    except ZeroDivisionError:
        logger(description='Не удалось посчитать средневзвешенную цену, деление на 0',
            log_type='debug',)
        avg_rate = 0

    logger(description='Средневзвешенная цена {ar:0.8f}'.format(ar=avg_rate),
        log_type='debug',)
    return avg_rate


def get_order_trades(order_id, pair, api):
    trades = api.myTrades(symbol=pair)
    trades.reverse()

    ret_trades = []
    for trade in trades:
        if str(trade['orderId']) == str(order_id):
            ret_trades.append(
                BaseTrade(
                    trade_id=trade['id'],
                    trade_rate=float(trade['price']),
                    trade_amount=float(trade['qty']),
                    trade_type='buy' if trade['isBuyer'] else 'sell',
                    trade_fee=float(trade['commission']),
                    fee_type=trade['commissionAsset']
                )
            )
    return ret_trades


def sync_time(bot, log, pause):
    while True:
        try:
            # Получаем ограничения торгов по всем парам с биржи
            limits = bot.exchangeInfo()

            local_time = int(time.time())
            server_time = int(limits['serverTime']) // 1000

            # Бесконечный цикл программы
            shift_seconds = server_time - local_time

            if local_time + shift_seconds != server_time:
                bot.set_shift_seconds(shift_seconds)
                logger(
                    description="""
                    Текущее время: {local_time_d} {local_time_u}
                    Время сервера: {server_time_d} {server_time_u}
                    Разница: {diff:0.8f} {warn}
                    Бот будет работать, как будто сейчас: {fake_time_d} {fake_time_u}
                    """.format(
                        local_time_d=datetime.fromtimestamp(local_time), local_time_u=local_time,
                        server_time_d=datetime.fromtimestamp(server_time), server_time_u=server_time,
                        diff=abs(local_time - server_time),
                        warn="ТЕКУЩЕЕ ВРЕМЯ ВЫШЕ" if local_time > server_time else '',
                        fake_time_d=datetime.fromtimestamp(local_time + shift_seconds),
                        fake_time_u=local_time + shift_seconds
                    ),
                    log_type='debug',
                    )

        except:
            log.exception('sync_time error')

        if pause:
            time.sleep(10000)
        else:
            break
