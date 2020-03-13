#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
# 客户端调用，用于查看API返回结果

# 现货
# from OkcoinFutureAPI import OKCoinFuture
import requests
import httplib
import urlparse
import json
from collections import defaultdict
import time
import datetime
# 期货的
from OkcoinFutureAPI import OKCoinFuture
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

append_path = '../../strategy'
sys.path.append(append_path)

from util.general import *
from HttpMD5Util import buildMySign, httpGet, httpPost

# 初始化apikey，secretkey,url
# apikey = '7033039d-0a60-4c6a-9758-7d18eb724d36'
# secretkey = '3A82A8B5D1988704DC2BB7885483A568'
okcoinRESTURL = 'https://www.okex.com'

# status: -1: 已撤销  0: 未成交  1: 部分成交  2: 完全成交 3: 撤单处理中
STATUS_TYPE = {2: "done", -1: "canceled", 1: "partial-filled", 0:"submitted"}

TRADE_TYPE = {1:"buy",2:"sell",3:"ping_buy",4:"ping_sell"}

class OKEXFutureService(object):

    def __init__(self, account=None):
        self.account = account

    def chooseType(self, coinType):
        return coinType

    def chooseType_num(self, coinType):
        if isinstance(coinType, str):
            try:
                _invert = {}
                for i in range(12):
                    _invert[self.chooseType(i)] = i
                return _invert[coinType]
            except:
                return coinType
        return coinType

    def get_position_params(self, contractType, coinType, type1):
        params = {}
        params["contractType"] = contractType
        params["symbol"] = coinType
        params["type"] = type1
        return params

    def get_trade_params(self, coinType, price, amount, tradeType):
        params = {}
        # 先使用固定参数
        params["lever_rate"] = 10

        # 执行参数
        params["symbol"] = coinType
        params["type"] = tradeType
        params["amount"] = amount
        params["price"] = price

        return params

    '''
    获取账号详情
    '''
    def getAccountInfo(self, method="future_userinfo_4fix"):
        result = self.api_get(method="future_userinfo_4fix")
        if result and result["result"] == True:
            result = result["info"]
            _result = {}
            for coin in result:
                _result[coin] = {
                    "available": float(result[coin]["rights"])
                }
                if result[coin]["contracts"]:
                    res = {}
                    for t in result[coin]["contracts"]:
                        res[t["contract_type"]] = {
                            "unprofit": t["unprofit"],
                            "profit": t["profit"],
                            "available": t["available"],
                            "balance": t["balance"]
                        }
                    _result[coin].update(res)
            return _result
        return {"result": "fail"}

    def estimated_price(self, coinType, method="future_estimated_price"):
        '''预交割价格'''
        coinType = self.chooseType(coinType)
        params = {"symbol":coinType}
        result = self.api_get(method, params)
        if result and result.get("forecast_price"):
            return result["forecast_price"]
        return

    def getPosition(self, coinType, contractType="this_week", method="future_position_4fix"):
        # buy_amount: 多仓数量
        # buy_available: 多仓可平仓数量
        # buy_bond: 多仓保证金
        # buy_flatprice: 多仓强平价格
        # buy_profit_lossratio: 多仓盈亏比
        # buy_price_avg: 开仓平均价
        # buy_price_cost: 结算基准价
        # buy_profit_real: 多仓已实现盈余
        # contract_id: 合约id
        # contract_type: 合约类型
        # create_date: 创建日期
        # sell_amount: 空仓数量
        # sell_available: 空仓可平仓数量
        # sell_bond: 空仓保证金
        # sell_flatprice: 空仓强平价格
        # sell_profit_lossratio: 空仓盈亏比
        # sell_price_avg: 开仓平均价
        # sell_price_cost: 结算基准价
        # sell_profit_real: 空仓已实现盈余
        # symbol: btc_usd   ltc_usd    eth_usd    etc_usd    bch_usd
        # lever_rate: 杠杆倍数
        coinType = self.chooseType(coinType)
        type1 = 1
        params = self.get_position_params(contractType, coinType, type1)
        result = self.api_get(method, params)
        # return result
        try:
            if result and result["result"] == True:
                result = result["holding"]
                _result = {}
                # print result
                for i in result:
                    _result[i["symbol"]] = {
                        "sell": {
                            "ratio": float(i['sell_profit_lossratio']),
                            "avg_price": i['sell_price_avg'],
                            "amount": i["sell_amount"],
                            "available": i["sell_available"],
                            "boom": float(i["sell_flatprice"]),
                            # "real_profit": float(i["sell_profit_real"]),
                            "bond": float(i["sell_bond"])
                        },
                        "buy": {
                            "ratio": float(i['buy_profit_lossratio']),
                            "avg_price": i['buy_price_avg'],
                            "amount": i["buy_amount"],
                            "available": i["buy_available"],
                            "boom": float(i["buy_flatprice"]),
                            # "real_profit": float(i["buy_profit_real"]),
                            "bond": float(i["buy_bond"]),
                        }
                    }
                return _result
        except BaseException as e:
            print e
        return None

    def get_tickers(self, coinType, contractType="this_week", method="ticker"):
        coinType = self.chooseType(coinType)
        market_url = urlparse.urlparse(okcoinRESTURL).hostname
        try:
            conn = httplib.HTTPSConnection(market_url, timeout=2)
            conn.request('GET', '/api/v1/future_ticker.do?symbol=%s&contract_type=%s' % (coinType, contractType))
            result = json.loads(conn.getresponse().read())
            if result and result.has_key("ticker"):
                _result = {}
                _result["buyOne"] = result["ticker"]["buy"]
                _result["sellOne"] = result["ticker"]["sell"]
                _result["high"] = result["ticker"]["high"]
                _result["low"] = result["ticker"]["low"]
            return _result
        except Exception as e:
            print e
            return {"result": "fail", "msg": "%s" % e}

    def get_kline(self, symbol, contract_type, timeType="1min",size="10"):
        FUTURE_TICKER_RESOURCE = "/api/v1/future_kline.do"
        params = ''
        if symbol:
            params += '&symbol=' + symbol if params else 'symbol=' + symbol
        if contract_type:
            params += '&contract_type=' + contract_type if params else 'contract_type=' + contract_type
        if timeType:
            params += '&type=' + timeType if params else 'timeType=' + timeType
        if size:
            params += '&size=' + size
        try:
            res = httpGet(okcoinRESTURL, FUTURE_TICKER_RESOURCE, params)
            return res
        except BaseException as e:
            print e
            return

    
    def buy(self, coinType, price, amount, match_price=None, contractType="this_week", method="trade"):
        # tradeType 1:开多   2:开空   3:平多   4:平空
        # this_week:当周   next_week:下周   quarter:季度
        coinType = self.chooseType(coinType)
        params = self.get_trade_params(coinType, price, amount, 1)
        if match_price:
            params["match_price"] = 1
        else:
            params['match_price'] = 0
        params["contractType"] = contractType
        result = self.api_get(method, params)
        if result and result["result"] == True:
            res = {"result": "success",
                   "id": result["order_id"], "status": "fail"}
            res["createTime"] = int(time.time())
            res["createTimeStr"] = str(datetime.now())
            res["tradeType"] = 1
            res["price"] = price
            res["amount"] = amount
            res["contractType"] = contractType
            res["type"] = TRADE_TYPE.get(1)
            return res
        return {"result": "fail", "msg": result}
    
    def sell(self, coinType, price, amount, match_price=None, contractType="this_week", method="trade"):
        # tradeType 1:开多   2:开空   3:平多   4:平空
        # this_week:当周   next_week:下周   quarter:季度
        coinType = self.chooseType(coinType)
        params = self.get_trade_params(coinType, price, amount, 2)
        if match_price:
            params["match_price"] = 1
        else:
            params['match_price'] = 0
        params["contractType"] = contractType
        result = self.api_get(method, params)
        if result and result["result"] == True:
            res = {"result": "success",
                   "id": result["order_id"], "status": "fail"}
            res["createTime"] = int(time.time())
            res["createTimeStr"] = str(datetime.now())
            res["tradeType"] = 2
            res["price"] = price
            res["amount"] = amount
            res["contractType"] = contractType
            res["type"] = TRADE_TYPE.get(2)
            return res
        return {"result": "fail", "msg": result}
    
    def ping_buy(self, coinType, price, amount, match_price=None, contractType="this_week", method="trade"):
        # tradeType 1:开多   2:开空   3:平多   4:平空
        # this_week:当周   next_week:下周   quarter:季度
        coinType = self.chooseType(coinType)
        params = self.get_trade_params(coinType, price, amount, 3)
        if match_price:
            params["match_price"] = 1
        else:
            params['match_price'] = 0
        params["contractType"] = contractType
        result = self.api_get(method, params)
        if result and result["result"] == True:
            res = {"result": "success",
                   "id": result["order_id"], "status": "fail"}
            res["createTime"] = int(time.time())
            res["createTimeStr"] = str(datetime.now())
            res["tradeType"] = 3
            res["price"] = price
            res["amount"] = amount
            res["contractType"] = contractType
            res["type"] = TRADE_TYPE.get(3)
            return res
        return {"result": "fail", "msg": result}
    
    def ping_sell(self, coinType, price, amount, match_price=None, contractType="this_week", method="trade"):
        # tradeType 1:开多   2:开空   3:平多   4:平空
        # this_week:当周   next_week:下周   quarter:季度
        coinType = self.chooseType(coinType)
        params = self.get_trade_params(coinType, price, amount, 4)
        if match_price:
            params["match_price"] = 1
        else:
            params['match_price'] = 0
        params["contractType"] = contractType
        result = self.api_get(method, params)
        if result and result["result"] == True:
            res = {"result": "success",
                   "id": result["order_id"], "status": "fail"}
            res["createTime"] = int(time.time())
            res["createTimeStr"] = str(datetime.now())
            res["tradeType"] = 4
            res["price"] = price
            res["amount"] = amount
            res["contractType"] = contractType
            res["type"] = TRADE_TYPE.get(4)
            return res
        return {"result": "fail", "msg": result}

    def trade(self, coinType, price, amount, tradeType, match_price=None, contractType="this_week", method="trade"):
        # tradeType 1:开多   2:开空   3:平多   4:平空
        # this_week:当周   next_week:下周   quarter:季度
        coinType = self.chooseType(coinType)
        params = self.get_trade_params(coinType, price, amount, tradeType)
        if match_price:
            params["match_price"] = 1
        else:
            params['match_price'] = 0
        params["contractType"] = contractType
        result = self.api_get(method, params)
        if result and result["result"] == True:
            res = {"result": "success", "id": result["order_id"],"status":"fail"}
            res["createTime"] = int(time.time())
            res["createTimeStr"] = str(datetime.now())
            res["tradeType"] = tradeType
            res["price"] = price
            res["amount"] = amount
            res["contractType"] = contractType
            res["type"] = TRADE_TYPE.get(tradeType)
            return res
        return {"result": "fail", "msg": result}

    def cancelOrder(self, coinType, id, contractType="next_week", method="cancelOrder"):
        coinType = self.chooseType(coinType)
        params = {"symbol": coinType, "id": id, "contractType": contractType}
        result = self.api_get(method, params)
        print result
        if result and result["result"] == True:
            return {"result": "success", "id": result["order_id"]}
        return {"result": "fail","msg":"%s"%(json.dumps(result))}

    def cancelOrders(self, coinType, ids,contractType="this_week",method="cancelOrders"):
        coinType = self.chooseType(coinType)
        params = {"symbol": coinType, "id": ids, "contractType": contractType}
        result = self.api_get(method, params)
        print result
        if result and result["result"] == True:
            return {"result": "success", "id": result["order_id"]}
        return {"result": "fail", "msg": "%s" % (json.dumps(result))}

    def getOrderInfo(self, coinType, id, contractType='next_week', method="order_info"):
        '''
        status: 订单状态(0等待成交 1部分成交 2全部成交 -1撤单 4撤单处理中 5撤单中)
        type 1:开多   2:开空   3:平多   4:平空
        '''
        coinType = self.chooseType(coinType)
        params = {"symbol": coinType, "id": id, "contractType": contractType}
        result = self.api_get(method, params)
        if result and result["result"] == True:
            if not result["orders"]:
                return {"result": "fail", "msg": "empty message"}
            orderInfo = result["orders"][0]
            _result = {"result": "success"}
            _result["id"] = orderInfo["order_id"]
            _result["price"] = orderInfo["price"]
            _result["amount"] = orderInfo["amount"]
            # _result["status"] = orderInfo["status"]
            _result["status"] = STATUS_TYPE.get(orderInfo["status"], "other")
            _result["type"] = orderInfo["type"]
            return _result
        return {"result": "fail", "msg": result}

    def getOrders(self,coinType,contractType="next_week",method="orders_info"):
        coinType = self.chooseType(coinType)
        params = {"symbol": coinType, "contractType": contractType}
        result = self.api_get(method, params)
        if result and result["result"] == True:
            if not result["orders"]:
                return {"result": "fail", "msg": "empty message"}
            _result = {"result": "success","orders":[]}
            for order in result["orders"]:
                _res = {}
                _res["id"] = order["order_id"]
                _res["price"] = order["price"]
                _res["amount"] = order["amount"]
                # _res["status"] = order["status"]
                _res["status"] = STATUS_TYPE.get(order["status"], "other")
                _res["type"] = order["type"]
                _result["orders"].append(_res)
            return _result
        return {"result": "fail", "msg": result}

    def depth(self, symbol, contractType, size=10,method="future_depth"):
        params = {"symbol":symbol,"contractType":contractType,"size":size}
        res =self.api_get(method, params)
        try:
            if res and res.has_key("bids"):
                return res
        except BaseException as e:
            print e
            return
        
    
    def api_get(self, method, params={}):
        # 现货API
        if self.account:
            apikey, secretkey = get_account_key("okex", self.account)
        okcoinSpot = OKCoinFuture(okcoinRESTURL, apikey, secretkey)
        if method == "future_userinfo_4fix":
            api_do = "okcoinSpot.%s()" % (method)
            return eval(api_do)

        elif method == "future_position_4fix":
            return okcoinSpot.future_position_4fix(params["symbol"], params["contractType"], params["type"])

        elif method == "trade":
            return okcoinSpot.future_trade(params["symbol"],
                                           params["contractType"],
                                           params["price"],
                                           params["amount"],
                                           params["type"],
                                           params["match_price"],
                                           params["lever_rate"])

        elif method == "ticker":
            return okcoinSpot.future_ticker(params["symbol"], params["contractType"])

        elif method == "order_info":
            return okcoinSpot.future_orderinfo(params["symbol"], params["contractType"], params["id"])
        
        elif method == "orders_info":
            return okcoinSpot.future_orderinfo(params["symbol"], params["contractType"],-1, status=1)

        elif method == "cancelOrder":
            return okcoinSpot.future_cancel(params["symbol"], params["contractType"], params["id"])
        elif method == "future_estimated_price":
            return okcoinSpot.future_estimated_price(params["symbol"])

        elif method == "future_depth":
            return okcoinSpot.future_depth(params.get("symbol"), params.get("contractType"),params.get("size"))
        elif method == "cancelOrders":
            return okcoinSpot.future_cancelorders(params["symbol"], params["contractType"], params["id"])

if __name__ == '__main__':
    # trade(9,8.24,1,1)
    ok = OKEXFutureService("wanghuageng")
    # print ok.get_tickers(9)
    # print ok.getAccountInfo()
    print ok.get_kline("eos_usdt","this_week")
    # print getPosition(9)
    # print getOrderInfo(9,1040492596114432, contractType="this_week")
    # print trade(9, 7,1,1)
    # print cancelOrder(9, 1035794044242944, contractType="this_week")
