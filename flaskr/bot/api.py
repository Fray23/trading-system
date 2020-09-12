from Crypto.Hash import SHA512
import time
import urllib
import hmac, hashlib
import requests
from urllib.parse import urlparse


class BitrixApi:
    def __init__(self, api_key, api_secret, api_version):
        self.API_URL = 'https://api.bittrex.com'
        self.API_VERSION = api_version
        self.API_KEY = api_key
        self.API_SECRET = bytes(api_secret, encoding='utf-8')

    def sha512(self, data):
        h = hmac.new(key=self.API_SECRET, digestmod=hashlib.sha512)
        h.update(data.encode('utf-8'))
        return h.hexdigest()

    @staticmethod
    def simple_sha512(data):
        h = SHA512.new(data)
        return h.hexdigest()

    def api_query(self, api_method, method, data={}):
        uri = self.API_URL + '/' + self.API_VERSION + api_method
        params = {
            'Api-Key': self.API_KEY,
            'Api-Timestamp': str(int((time.time())*1000)),
            'Api-Content-Hash': self.simple_sha512(urllib.parse.urlencode(data))
            }
        pre_sign = ''.join([
                    str(params['Api-Timestamp']),
                    str(uri),
                    str(method).upper(),
                    str(params['Api-Content-Hash']),
                    ''
                ])
        params['Api-Signature'] = self.sha512(pre_sign)
        if method.upper() == 'POST':
            response = requests.post(uri, headers=params, data=data)
        elif method.upper() == 'GET':
            response = requests.get(uri, headers=params)
        else:
            return
        return response


# publick
# secure


class Binance():
    methods = {
        # public methods
        'ping': {'url': 'api/v1/ping', 'method': 'GET', 'private': False},
        'time': {'url': 'api/v1/time', 'method': 'GET', 'private': False},
        'exchangeInfo': {'url': 'api/v1/exchangeInfo', 'method': 'GET', 'private': False},
        'depth': {'url': 'api/v1/depth', 'method': 'GET', 'private': False},
        'trades': {'url': 'api/v1/trades', 'method': 'GET', 'private': False},
        'historicalTrades': {'url': 'api/v1/historicalTrades', 'method': 'GET', 'private': False},
        'aggTrades': {'url': 'api/v1/aggTrades', 'method': 'GET', 'private': False},
        'klines': {'url': 'api/v3/klines', 'method': 'GET', 'private': False},                        # +

        'ticker24hr': {'url': 'api/v1/ticker/24hr', 'method': 'GET', 'private': False},
        'tickerPrice': {'url': 'api/v3/ticker/price', 'method': 'GET', 'private': False},

        'tickerBookTicker': {'url': 'api/v3/ticker/bookTicker', 'method': 'GET', 'private': False},
        # private methods
        'createOrder': {'url': 'api/v3/order', 'method': 'POST', 'private': True},
        'testOrder': {'url': 'api/v3/order/test', 'method': 'POST', 'private': True},
        'orderInfo': {'url': 'api/v3/order', 'method': 'GET', 'private': True},
        'cancelOrder': {'url': 'api/v3/order', 'method': 'DELETE', 'private': True},
        'openOrders': {'url': 'api/v3/openOrders', 'method': 'GET', 'private': True},
        'allOrders': {'url': 'api/v3/allOrders', 'method': 'GET', 'private': True},
        'account': {'url': 'api/v3/account', 'method': 'GET', 'private': True},
        'myTrades': {'url': 'api/v3/myTrades', 'method': 'GET', 'private': True},
        # wapi
        'depositAddress': {'url': '/wapi/v3/depositAddress.html', 'method': 'GET', 'private': True},
        'withdraw': {'url': '/wapi/v3/withdraw.html', 'method': 'POST', 'private': True},
        'depositHistory': {'url': '/wapi/v3/depositHistory.html', 'method': 'GET', 'private': True},
        'withdrawHistory': {'url': '/wapi/v3/withdrawHistory.html', 'method': 'GET', 'private': True},
        'withdrawFee': {'url': '/wapi/v3/withdrawFee.html', 'method': 'GET', 'private': True},
        'accountStatus': {'url': '/wapi/v3/accountStatus.html', 'method': 'GET', 'private': True},
        'systemStatus': {'url': '/wapi/v3/systemStatus.html', 'method': 'GET', 'private': True},
    }

    def __init__(self, API_KEY, API_SECRET):
        self.API_KEY = API_KEY
        self.API_SECRET = bytearray(API_SECRET, encoding='utf-8')
        self.shift_seconds = 0

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            kwargs.update(command=name)
            return self.call_api(**kwargs)

        return wrapper

    def set_shift_seconds(self, seconds):
        self.shift_seconds = seconds

    def call_api(self, **kwargs):

        command = kwargs.pop('command')
        api_url = 'https://api.binance.com/' + self.methods[command]['url']

        payload = kwargs
        headers = {}

        payload_str = urllib.parse.urlencode(payload)
        if self.methods[command]['private']:
            payload.update({'timestamp': int(time.time() + self.shift_seconds - 1) * 1000})
            payload_str = urllib.parse.urlencode(payload).encode('utf-8')
            sign = hmac.new(
                key=self.API_SECRET,
                msg=payload_str,
                digestmod=hashlib.sha256
            ).hexdigest()

            payload_str = payload_str.decode("utf-8") + "&signature=" + str(sign)
            headers = {"X-MBX-APIKEY": self.API_KEY}

        if self.methods[command]['method'] == 'GET':
            api_url += '?' + payload_str

        response = requests.request(method=self.methods[command]['method'], url=api_url,
                                    data="" if self.methods[command]['method'] == 'GET' else payload_str,
                                    headers=headers)
        if 'code' in response.text:
            print(response.text)
        return response.json()

