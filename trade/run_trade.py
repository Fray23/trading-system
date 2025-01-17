import threading

from trade.bot.trade import main_flow
from trade.bot.config import api
from trade.bot.utils import sync_time
from trade.bot.logger import log


if __name__ == '__main__':
    sync_time(api, log, False, )

    t1 = threading.Thread(target=main_flow)
    t2 = threading.Thread(target=sync_time, args=(api, log, True,))

    threads = [t1, t2]

    for t in threads:
        t.start()
