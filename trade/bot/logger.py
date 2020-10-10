import os
import logging

from database.models import Log
from web.flaskr.utils import log_types

logging.basicConfig(
    format="%(asctime)s [%(levelname)-5.5s] %(message)s",
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("{path}/logs/{fname}.log".format(path=os.path.dirname(os.path.abspath(__file__)), fname="binance")),
        logging.StreamHandler()
    ])
log = logging.getLogger('')


def logger(**kwargs):
    kwargs['log'] = log
    if 'log_type' not in kwargs:
        kwargs['log_type'] = log_types['debug']
    Log.create(**kwargs)
