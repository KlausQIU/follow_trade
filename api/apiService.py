# !/usr/bin/env python
# coding:utf-8
import sys
sys.path.append("../../arbitrage_future_spot")

import grpc
import vir_exchange_api_service_pb2_grpc
import vir_exchange_api_service_pb2
from sign_crypto import get_sign_str
import json
from setting import *
import time
import accounts_api_service_pb2_grpc
import accounts_api_service_pb2
import monitor_api_service_pb2_grpc
import monitor_api_service_pb2


class Api():
    def __init__(self, accesskey="", secretkey="", exchange=None, account_code=None):
        self.exchange = exchange
        if len(accesskey) < 100:
            self.accesskey = get_sign_str(accesskey)
            self.secretkey = get_sign_str(secretkey)
        else:
            self.accesskey = accesskey
            self.secretkey = secretkey
        channel = grpc.insecure_channel(GRPC_IP + ":" + GRPC_PORT)
        self.account_code = account_code
        self.stub = vir_exchange_api_service_pb2_grpc.VirExOtcApiStub(channel)
        account_channel = grpc.insecure_channel("accounts-grpc-service.default.svc.cluster.local:50062")
        self.accounts_stub = accounts_api_service_pb2_grpc.AccountsApiStub(account_channel)

    def get_account_code(self,account=""):
        response = self.accounts_stub.GetAccountInfo(accounts_api_service_pb2.AccountReq(accountCode=self.account_code))
        try:
            jData = json.loads(response.accountInfo)
            return jData
        except BaseException as e:
            print e
            return
    

    def tickers(self, symbol, depth=False):
        response = self.stub.getMarketDepth(
            vir_exchange_api_service_pb2.MarketInfo(symbol=symbol, limit=1, exchange=self.exchange))
        jData = json.loads(response.result)
        if depth:
            return jData
        if jData.has_key("bids"):
            return {"buyOne": float(jData["bids"][0][0]), "sellOne": float(jData["asks"][0][0])}
        else:
            return

    def finishOrders(self, symbol,page=1,limit=10):
        try:
            # rpc getFinishedOrders (FinishedOrder) returns (FinishedOrderResult) {}
            response = self.stub.getFinishedOrders(
                vir_exchange_api_service_pb2.FinishedOrder(symbol=symbol,exchange=self.exchange,page=page,limit=limit,
                                                        accountCode=self.account_code
                                                )
            )
            # print response
            jData = json.loads(response.orders)
            return jData
        except BaseException as e:
            print e
            return {}
        

    def buy(self, symbol, price, amount, method=None):
        try:
            if method == "limitMarker":
                response = self.stub.createBuyLimitMakerOrder(
                    vir_exchange_api_service_pb2.OrderInfo(symbol=symbol, quantity=amount, exchange=self.exchange,
                                                    price=price, accountCode=self.account_code))
                jData = json.loads(response.order)
                if jData.get("data"):
                    time.sleep(0.2)
                    res = self.orderInfo(symbol, jData["data"])
                    if res["status"] == "ok":
                        if res["order_status"] in ["canceling","canceled"]:
                            jData["status"] = "error"
            else:
                response = self.stub.createBuyOrder(
                    vir_exchange_api_service_pb2.OrderInfo(symbol=symbol, quantity=amount, exchange=self.exchange,
                                                        price=price,accountCode=self.account_code))

                jData = json.loads(response.order)
            print jData
            jData.update({"orderId": str(jData.get("data", "")),"symbol": symbol, "price": price, "amount": amount, "type": "buy"})
            return jData
        except BaseException as e:
            print e
            return {}

    def sell(self, symbol, price, amount, method=None):
        try:
            if method == "limitMarker":
                response = self.stub.createSellLimitMakerOrder(
                    vir_exchange_api_service_pb2.OrderInfo(symbol=symbol, quantity=amount, exchange=self.exchange,
                                                    price=price, accountCode=self.account_code))
                jData = json.loads(response.order)
                if jData.get("data"):
                    time.sleep(0.2)
                    res = self.orderInfo(symbol, jData["data"])
                    if res["status"] == "ok":
                        if res["order_status"] in ["canceling","canceled"]:
                            jData["status"] = "error"
            else:
                response = self.stub.createSellOrder(
                    vir_exchange_api_service_pb2.OrderInfo(symbol=symbol, quantity=amount, exchange=self.exchange,
                                                        price=price,accountCode=self.account_code))
                jData = json.loads(response.order)
            print jData
            jData.update({"orderId": str(jData.get("data", "")),"symbol": symbol, "price": price, "amount": amount, "type": "sell"})
            return jData
        except BaseException as e:
            print e
            return {}

    def accountInfo(self, symbol):
         # accountCode=self.account_code
        res = {}
        try:
            for c in symbol.split("/"):
                _ = self.stub.getAccountLeft(vir_exchange_api_service_pb2.AssetInfo(asset=c, exchange=self.exchange,
                                                                                    accountCode=self.account_code))
                _ = json.loads(_.left)
                res[c] = {"free": round(float(_["free"]), 4), "locked": round(float(_["locked"]), 4)}
            return res
        except BaseException as e:
            print e
            return res

    def cancelOrder(self, symbol, order_id):
        try:
            _ = self.stub.cannelOrder(vir_exchange_api_service_pb2.OrderDetail(symbol=symbol, order_id=order_id, exchange=self.exchange,
                                                                            accountCode=self.account_code))
            jData = json.loads(_.order_detail)
            return jData
        except BaseException as e:
            print e
            return

    def orders(self, symbol):
        try:
            _ = self.stub.getCurrentOrders(vir_exchange_api_service_pb2.CurrentOrder(symbol=symbol, exchange=self.exchange,
                                                                            accountCode=self.account_code))
            jData = json.loads(_.orders)
            return jData["orders"]
        except BaseException as e:
            print e
            return

    def orderInfo(self, symbol, orderId):
        # pre-submitted	准备提交
        # submitted	已提交，未执行
        # partial-filled	部分已成交
        # canceling	撤销中
        # partial-canceled	部分成交已撤销
        # canceled	已撤销
        # done	完成
        # rejected	拒绝
        # expired	过期
        # print symbol,orderId,self.exchange
        # print self.accesskey,self.secretkey
        _ = self.stub.checkOrder(vir_exchange_api_service_pb2.OrderDetail(symbol=symbol, order_id=orderId,
                                                                           exchange=self.exchange,
                                                                           accountCode=self.account_code))
        jData = json.loads(_.order_detail)
        try:
            float_map = ["price", "amount", "deal_amount","avg_price"]
            for f in float_map:
                if f not in jData.keys():
                    continue
                jData[f] = float(jData[f])
            # jData.update({"orderId": str(jData["orderId"])})
            return jData
        except BaseException as e:
            print e, jData

    def kline(self,symbol,period,size=100):
        try:
            _ = self.stub.kline(vir_exchange_api_service_pb2.KLine(symbol=symbol,
                                                                    exchange=self.exchange,
                                                                    period=period,
                                                                    size=size))
            _ = json.loads(_.kline)

            return _["kline"]
        except BaseException as e:
            print e
            return {"status":"error","message":e}


if __name__ == '__main__':
    a = Api()
    a.kline("btc/usdt","15min")
