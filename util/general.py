# !/usr/bin/env python
# coding:utf-8


import sys
append_path = '../../follow_trade'
sys.path.append(append_path)

from ConfigParser import ConfigParser
import functools
import threading
import time
from datetime import datetime

def get_account_key(exchange, account=None):
    cf = ConfigParser()
    cf.read('../config/%s.ini' % account)
    apikey = cf.get('%s' % exchange, 'api_key')
    secretkey = cf.get('%s' % exchange, 'secret_key')
    if exchange == "okex":
        passphrase = cf.get('%s'%exchange, 'passphrase')
        return apikey, secretkey,passphrase
    return apikey, secretkey


def get_account_params(strategy, account=None):
    cf = ConfigParser()
    cf.read('../config/%s.ini' % account)
    params = dict(cf.items("%s"%strategy))
    return params

def get_huobi_acctid(account=None):
    cf = ConfigParser()
    cf.read('../config/%s.ini' % account)
    acct_id = int(cf.get('huobi','acct_id') or 0)
    return acct_id


def get_percision(exchange, coinType):
    try:
        cf = ConfigParser()
        cf.read('../config/%s.ini' % exchange)
        price_percision = int(cf.get("%s" % coinType, "price_percision"))
        amount_percision = int(cf.get("%s" % coinType, "amount_percision"))
        return price_percision,amount_percision
    except BaseException as e:
        print e
        return 4,4

def async(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        my_thread.setDaemon(True)
        my_thread.start()
    return wrapper


def chooseCoinStr(coinType):
    return coinType


@async
def Log(coinType, msg):
    now_md = time.strftime("%Y%m%d")
    fileName = chooseCoinStr(coinType)
    with open('log/%s_%s.log' % (fileName, now_md), 'a') as t:
        now = datetime.now()
        str_time = now.strftime('%Y-%m-%d %H:%M:%S')
        msg = "[" + str_time + "]" + ' ' + msg + "\n"
        t.write(msg)