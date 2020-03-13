# !/usr/bin/env python
# coding:utf-8


import sys
append_path = '../../strategy'
sys.path.append(append_path)

from ConfigParser import ConfigParser
import functools
import threading
import time
from datetime import datetime
from util.db import Mysqldb
from influxdb import InfluxDBClient

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

def mysqlConnection(func):
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        mysqldb = Mysqldb()
        tableName,insert_data = func(*args, **kwargs)
        print tableName, insert_data
        mysqldb.insert(tableName, insert_data)
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


@async
def insert_qixian_trade(coinType, account, spot_exchange=None, future_exchange=None,params=None):
    if not params or not account:
        return
    if params["spot"]["before_price"] > params["future"]["before_price"]:
        # 现货卖
        buy_exchange,sell_exchange = future_exchange,spot_exchange
        Type = "sell"
    else:
        # 现货买
        buy_exchange, sell_exchange = spot_exchange, future_exchange
        Type = "buy"

    # 收益计算为直接计算现货 因为现货的币数会平掉期货的币数
    # 例如 期货  10  现货 11 卖出 10/10 得 11， 平仓时，价格都是 10 期货无损，现货 买入 10 数量 10/10 得利润= 1 * 手续费
    spot = params["spot"]
    profit = abs((spot["before_price"] * spot["before_amount"]) - \
        (spot["now_price"] * spot["now_amount"])) - (40*0.001)

    insert_data = {
        "account":account,
        "log_time":datetime.now(),
        "symbol":coinType,
        "buy_exchange":buy_exchange,
        "sell_exchange":sell_exchange,
        "buy_price": str(params["spot"]["before_price"] if Type == "buy" else params["future"]["before_price"]),
        "sell_price": str(params["future"]["before_price"] if Type == "buy" else params["spot"]["before_price"]),
        "buy_ping_price": str(params["spot"]["now_price"] if Type == "buy" else params["future"]["now_price"]),
        "sell_ping_price": str(params["future"]["now_price"] if Type == "buy" else params["spot"]["now_price"]),
        "before_amount": str(params["spot"]["before_amount"]),
        "now_amount": str(params["spot"]["now_amount"]),
        "profit": str(profit),
        "comment":""
    }
    print insert_data

    mysqldb = Mysqldb()
    mysqldb.insert("log_qixian_trade", insert_data)

@async
def insert_grid_trade(coinType, account, exchange=None,params=None):
    if not account or not params:
        return
    insert_data = { 
        "account": account,
        "log_time":datetime.now(),
        "symbol":coinType,
        "exchange":exchange,
        "side":params.get("side"),
        "price":params.get("price",0.0),
        "amount":params.get("amount",0.0),
        "strategy":params.get("strategy","grid"),
        "order_id": params.get("order_id"),
        "status": "fail"
    }
    mysqldb = Mysqldb()
    mysqldb.insert("log_grid_trade", insert_data)

@async
def update_grid_trade(coinType,account,order_id=None,exchange=None,params=None):
    try:
        sql = '''UPDATE log_grid_trade SET '''
        for k, v in params.iteritems():
                if type(v) in [int, float]:
                    sql += "%s=%s , " % (k, v)
                else:
                    sql += "%s='%s' , " % (k, str(v))
        sql = sql[:-2]
        sql += "where order_id='%s';" % (order_id)
        print ">>>>>>  update data sql  <<<<<<"
        print sql
        print ">>>>>> update data sql  <<<<<<"
        mysqldb = Mysqldb()
        mysqldb.do_sql(sql)
    except BaseException as e:
        print e
        return
    
