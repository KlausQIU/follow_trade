#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
# 客户端调用，用于查看API返回结果

# 现货
from OkcoinSpotAPI import OKCoinSpot
import requests
import httplib
import urlparse
import json
from collections import defaultdict
import time
# 期货的
# from OkcoinFutureAPI import OKCoinFuture
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

append_path = '../../follow_trade'
sys.path.append(append_path)

from util.general import *


# 初始化apikey，secretkey,url
# apikey = '7033039d-0a60-4c6a-9758-7d18eb724d36'
# secretkey = '3A82A8B5D1988704DC2BB7885483A568'
okcoinRESTURL = 'https://www.okex.com'

# status: -1: 已撤销  0: 未成交  1: 部分成交  2: 完全成交 3: 撤单处理中
STATUS_TYPE = {2:"done",-1:"canceled",1:"other"}

class OKEXService(object):

    def __init__(self, account=None):
        self.account = account

    def chooseType(self, coinType):
        return coinType

    def chooseType_num(self, coinType):
        return coinType

    def get_trade_params(self, coinType, price, amount):
        params = {}
        params["amount"] = amount
        params["symbol"] = coinType
        params["price"] = price
        return params

    '''
    获取账号详情
    '''

    def getAccountInfo(self, method="get_account_info"):
        result = self.api_get(method="userinfo")
        if result and result["result"] == True:
            result = result["info"]["funds"]
            _result = defaultdict(dict)
            for status in result:
                for coin in result[status]:
                    if status == "freezed":
                        _result[coin]["frozen"] = float(result[status][coin])
                    if status == "free":
                        _result[coin]["available"] = float(result[status][coin])
            return _result
        return {"result": "fail", "msg": result}

    def buy(self, coinType, price, amount, method="buy"):
        # symbol: btc_cny: 比特币 ltc_cny: 莱特币 eth_cny :以太坊
        # type:限价单（buy/sell） 市价单（buy_market/sell_market）
        # symbol,tradeType,price='',amount=''
        # okcoinSpot.trade('ltc_usd','buy','0.1','0.2')
        coinType = self.chooseType(coinType)
        params = self.get_trade_params(coinType, price, amount)
        result = self.api_get(method, params)
        if result and result.has_key('result') and result["result"] == True:
            return {"result": "success", "id": result["order_id"], "price":price,
                    "amount":amount}
        return {"result": "fail", "msg": result}

    def sell(self, coinType, price, amount, method="sell"):
        coinType = self.chooseType(coinType)
        params = self.get_trade_params(coinType, price, amount)
        result = self.api_get(method, params)
        if result and result.has_key('result') and result["result"] == True:
            return {"result": "success", "id": result["order_id"], "price": price,
                    "amount": amount}
        return {"result": "fail", "msg": result}

    def cancelOrder(self, coinType, id, method="cancelOrder"):
        coinType = self.chooseType(coinType)
        params = {"symbol": coinType, "id": id}
        result = self.api_get(method, params)
        if result and result["result"] == True:
            return {"result": "success", "id": result["order_id"]}
        return {"result": "fail"}

    def getOrderInfo(self, coinType, id, method="order_info"):
        coinType = self.chooseType(coinType)
        params = {"symbol": coinType, "id": id}
        result = self.api_get(method, params)
        if result and result["result"] == True:
            orderInfo = result["orders"][0]
            _result = {"result": "success"}
            _result["id"] = orderInfo["order_id"]
            _result["price"] = orderInfo["price"]
            _result["amount"] = orderInfo["amount"]
            # status:-1:已撤销  0:未成交  1:部分成交  2:完全成交 3:撤单处理中
            
            _result["status"] = STATUS_TYPE.get(orderInfo["status"],"other")
            return _result
        return {"result": "fail"}

    def getOrders(self, coinType, method="orders_info"):
        coinType = self.chooseType(coinType)
        params = {"symbol": coinType, "id": -1}
        result = self.api_get(method, params)
        if result and result["result"] == True:
            _result = []
            for order in result["orders"]:
                _order = {}
                _order["id"] = order["order_id"]
                _order["price"] = float(order["price"])
                _order["amount"] = float(order["amount"])
                _order["type"] = 0 if order["type"] == "buy" else 1
                _result.append(_order)
            return _result
        return []

    def get_tickers(self, coinType, method="ticker"):
        coinType = self.chooseType(coinType)
        okcoinRESTURL = 'https://www.okex.com'
        okcoinRESTURL = urlparse.urlparse(okcoinRESTURL).hostname
        try:
            conn = httplib.HTTPSConnection(okcoinRESTURL, timeout=2)
            conn.request('GET', '/api/v1/ticker.do?symbol=%s' % coinType)
            ticker = json.loads(conn.getresponse().read())
            if ticker.has_key("ticker") and ticker["ticker"]:
                okcoin_ticker = {}
                okcoin_ticker["buyOne"] = float(ticker["ticker"]["buy"])
                okcoin_ticker["sellOne"] = float(ticker["ticker"]["sell"])
                return okcoin_ticker
            return {"result": "fail", "msg": ticker}
        except BaseException as e:
            return {"result": "fail", "msg": "%s" % e}

    def get_kline(self, coinType, Type="5min",method="kline"):
        coinType = self.chooseType(coinType)
        okcoinRESTURL = 'https://www.okex.com'
        okcoinRESTURL = urlparse.urlparse(okcoinRESTURL).hostname
        try:
            conn = httplib.HTTPSConnection(okcoinRESTURL, timeout=2)
            conn.request(
                'GET', '/api/v1/kline.do?symbol=%s&type=%s' % (coinType,Type))
            data = json.loads(conn.getresponse().read())
            if data:
                return data
            return {"result": "fail", "msg": ticker}
        except BaseException as e:
            return {"result": "fail", "msg": "%s" % e}
        
    def funds_transfer(self, coinType, amount, From, To, method="funds_transfer"):
        # 转出账户(1：币币账户 3：合约账户 6：我的钱包)
        coinType = self.chooseType(coinType)
        params = {"symbol": coinType,
                  "amount": amount,
                  "from": From,
                  "to": To}
        result = self.api_get(method, params)
        if result and result.has_key('result') and result["result"] == True:
            return {"result": "success", "msg": result}
        return {"result": "fail", "msg": result}

    def api_get(self, method, params={}):
        # 现货API
        if self.account:
            apikey, secretkey = get_account_key("okex", self.account)
        okcoinSpot = OKCoinSpot(okcoinRESTURL, apikey, secretkey)
        if method == "userinfo":
            api_do = "okcoinSpot.%s()" % (method)
            return eval(api_do)

        elif method in ["buy", "sell"]:
            return okcoinSpot.trade(params["symbol"],
                                    method,
                                    params["price"],
                                    params["amount"])
        elif method == "cancelOrder":
            return okcoinSpot.cancelOrder(params["symbol"],
                                          params["id"])

        elif method in ["order_info", "orders_info"]:
            return okcoinSpot.orderinfo(params["symbol"],
                                        params["id"])

        elif method == "ticker":
            return okcoinSpot.ticker(symbol=params["symbol"])
        elif method == "funds_transfer":
            return okcoinSpot.funds_transfer(params["amount"], params["from"],
            params["to"],symbol=params["symbol"])


def many_buy(coinType, price, price_distance, count, amount):
    n = 0
    while n <= count:
        print buy(coinType, price, amount, None, None)
        price -= price_distance
        n += 1
        time.sleep(1)


def many_sell(coinType, price, price_distance, count, amount):
    n = 0
    while n <= count:
        print sell(coinType, price, amount, None, None)
        price += price_distance
        n += 1
        time.sleep(1)


if __name__ == '__main__':
    print getAccountInfo()
