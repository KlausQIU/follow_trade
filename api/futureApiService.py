import sys
sys.path.append("../../arbitrage_marker")

import grpc
import vir_exchange_api_service_pb2_grpc
import vir_exchange_api_service_pb2
from sign_crypto import get_sign_str
import json
from setting import *
import time
import accounts_api_service_pb2_grpc
import accounts_api_service_pb2


class FutureApi:

    def __init__(self, accesskey="", secretkey="", exchange=None, account_code=None):
        self.exchange = exchange
        if len(accesskey) < 100:
            # import pdb; pdb.set_trace()
            self.accesskey = get_sign_str(accesskey)
            self.secretkey = get_sign_str(secretkey)
            # print self.accesskey
            # print self.secretkey
        else:
            self.accesskey = accesskey
            self.secretkey = secretkey
        channel = grpc.insecure_channel("47.52.94.220" + ":" + "50053")
        self.account_code = account_code
        self.stub = vir_exchange_api_service_pb2_grpc.VirExOtcApiStub(channel)

    def tickers(self, symbol, contractType):
        jData = ""
        try:
            response = self.stub.futuresTicker(
                vir_exchange_api_service_pb2.FuturesTicker(symbol=symbol, contractType=contractType, exchange=self.exchange))
            jData = json.loads(response.futuresTicker)
            return {"buyOne":jData["buy"],"sellOne":jData["sell"]}
        except BaseException as e:
            print jData,e
            return

    def accountInfo(self,coin):
        res = {}
        try:
            _ = self.stub.futuresUserInfoFix(vir_exchange_api_service_pb2.FuturesUserInfoFix(asset=coin, exchange=self.exchange,
                                                                                            # accessKey="84a05260-ad7f-474c-b39e-4dd3303bebd5",
                                                                                            #  secretKey="EA8EAF5EFA91DD658B8D8C1E9F13FDB4"))
                                                                                            accountCode=self.account_code))
            
            _ = json.loads(_.futuresUserInfoFix)
            # print _
            res[coin] = {"free": round(float(_["balance"]), 4),"rights":round(float(_["rights"]),4)}
            _res = {}
            for t in _["contracts"]:
                _res[t["contract_type"]] = {
                    "unprofit": t["unprofit"],
                    "profit": t["profit"],
                    "available": t["available"],
                    "balance": t["balance"],
                    "bond": t["bond"],
                    "freeze":t["freeze"]
                }
            res[coin].update(_res)
            return res
        except BaseException as e:
            print e
            return res

    def position(self,symbol,contractType="this_week",Type=0):
        try:
            _ = self.stub.futuresPositionFix(vir_exchange_api_service_pb2.FuturesPositionFix(symbol=symbol,
                                                                                             exchange=self.exchange,
                                                                                             type=Type,
                                                                                             contractType=contractType,
                                                                                            #  accessKey="84a05260-ad7f-474c-b39e-4dd3303bebd5",
                                                                                            #  secretKey="EA8EAF5EFA91DD658B8D8C1E9F13FDB4"))
                                                                                             accountCode=self.account_code))
            _ = json.loads(_.futuresPositionFix)
            # print _
            holding = _.get("holdings",[])
            res = {}
            for c in holding:
                res[c["contract_type"]] = c
            return res
        except BaseException as e:
            print e
            return {}

    def buy(self,symbol,price, amount,contractType="this_week",matchPrice=False):
        try:
            _ = self.stub.futuresTrade(vir_exchange_api_service_pb2.FuturesTrade(symbol=symbol,
                                                                                 exchange=self.exchange,
                                                                                 price=price,
                                                                                 amount=amount,
                                                                                 contractType=contractType,
                                                                                 tradeType=1,
                                                                                 matchPrice=matchPrice,
                                                                                 accountCode=self.account_code))
            _ = json.loads(_.futuresTrade)
            _.update({"price":price,"amount":amount,"contractType":contractType,"symbol":symbol,"side":"buy","createTime":int(time.time()),"orderId":_["order_id"]})
            return _
        except BaseException as e:
            print e
            return {"price":price,"amount":amount,"contractType":contractType,"symbol":symbol,"side":"buy","createTime":int(time.time()),"status":"error"}

    def sell(self, symbol,price,amount,contractType="this_week",matchPrice=False):
        try:
            _ = self.stub.futuresTrade(vir_exchange_api_service_pb2.FuturesTrade(symbol=symbol,
                                                                                 exchange=self.exchange,
                                                                                 price=price,
                                                                                 amount=amount,
                                                                                 contractType=contractType,
                                                                                 tradeType=2,
                                                                                 matchPrice=matchPrice,
                                                                                 accountCode=self.account_code))
            _ = json.loads(_.futuresTrade)
            _.update({"price":price,"amount":amount,"contractType":contractType,"symbol":symbol,"side":"sell","createTime":int(time.time()),"orderId":_["order_id"]})
            return _
        except BaseException as e:
            print e
            return {"price":price,"amount":amount,"contractType":contractType,"symbol":symbol,"side":"sell","createTime":int(time.time()),"status":"error"}

    def liqui_buy(self, symbol,price,amount,contractType="this_week",matchPrice=False):
        try:
            _ = self.stub.futuresTrade(vir_exchange_api_service_pb2.FuturesTrade(symbol=symbol,
                                                                                 exchange=self.exchange,
                                                                                 price=price,
                                                                                 amount=amount,
                                                                                 contractType=contractType,
                                                                                 tradeType=3,
                                                                                 accountCode=self.account_code,
                                                                                 matchPrice=matchPrice))
            _ = json.loads(_.futuresTrade)
            print _
            _.update({"price":price,"amount":amount,"contractType":contractType,"symbol":symbol,"side":"liqui_buy","createTime":int(time.time()),"orderId":_["order_id"]})
            return _
        except BaseException as e:
            print e
            return {"price":price,"amount":amount,"contractType":contractType,"symbol":symbol,"side":"liqui_buy","createTime":int(time.time()),"status":"error"}
    
    def liqui_sell(self, symbol,price,amount,contractType="this_week",matchPrice=False):
        try:
            _ = self.stub.futuresTrade(vir_exchange_api_service_pb2.FuturesTrade(symbol=symbol,
                                                                                 exchange=self.exchange,
                                                                                 price=price,
                                                                                 amount=amount,
                                                                                 contractType=contractType,
                                                                                 tradeType=4,
                                                                                 accountCode=self.account_code,
                                                                                 matchPrice=matchPrice))
            _ = json.loads(_.futuresTrade)
            print _
            _.update({"price":price,"amount":amount,"contractType":contractType,"symbol":symbol,"side":"liqui_sell","createTime":int(time.time()),"orderId":_["order_id"]})
            return _
        except BaseException as e:
            print e
            return {"price":price,"amount":amount,"contractType":contractType,"symbol":symbol,"side":"liqui_sell","createTime":int(time.time()),"status":"error"}

    def orderInfo(self,symbol,orderId,contractType="this_week"):
        try:
            _ = self.stub.futuresCheckOrder(vir_exchange_api_service_pb2.FuturesCheckOrder(symbol=symbol,
                                                                                 exchange=self.exchange,
                                                                                 orderId=orderId,
                                                                                 contractType=contractType,
                                                                                 accountCode=self.account_code))
            _ = json.loads(_.futuresCheckOrder)
            # print _
            _.update({"orderId":_["order_id"]})
            return _
        except BaseException as e:
            print e
            return {"status":"error","message":e}

    def cancelOrder(self,symbol,orderId,contractType="this_week"):
        try:
            _ = self.stub.futuresCancel(vir_exchange_api_service_pb2.FuturesCancel(symbol=symbol,
                                                                                 exchange=self.exchange,
                                                                                 orderId=orderId,
                                                                                 contractType=contractType,
                                                                                 accountCode=self.account_code))
            _ = json.loads(_.futuresCancel)
            print _
            return _
        except BaseException as e:
            print e
            return {"status":"error","message":e}

    def cancelOrders(self,symbol,orderIds,contractType="this_week"):
        try:
            _ = self.stub.futuresBatchCancel(vir_exchange_api_service_pb2.FuturesBatchCancel(symbol=symbol,
                                                                                 exchange=self.exchange,
                                                                                 orderIds=orderIds,
                                                                                 contractType=contractType,
                                                                                 accountCode=self.account_code))
            _ = json.loads(_.futuresBatchCancel)
            print _
            return _
        except BaseException as e:
            print e
            return {"status":"error","message":e}


    def kline(self,symbol,period,contractType="this_week",size=100):
        try:
            _ = self.stub.futuresKLine(vir_exchange_api_service_pb2.FuturesKLine(symbol=symbol,
                                                                                 exchange=self.exchange,
                                                                                 period=period,
                                                                                 contractType=contractType,
                                                                                 size=size))
            _ = json.loads(_.futuresKLine)
            return _["futuresKLine"]
        except BaseException as e:
            print e
            return {"status":"error","message":e}
        
    def rsi(self,symbol,period,timePeriods=None,contractType="this_week",size=100):
        try:
            _ = self.stub.futuresKLineRSI(vir_exchange_api_service_pb2.FuturesKLineRSI(symbol=symbol,
                                                                                    exchange=self.exchange,
                                                                                    period=period,
                                                                                    contractType=contractType,
                                                                                    size=size,
                                                                                    timePeriods=timePeriods
                                                                                    ))
            _ = json.loads(_.futuresKLineRSI)
            return _
        except BaseException as e:
            print e
            return {"status":"error","message":e}

    
    def orders(self,symbol,contractType="this_week"):
        try:
            _ = self.stub.futuresOrders(vir_exchange_api_service_pb2.FuturesOrders(symbol=symbol,
                                                                                    exchange=self.exchange,
                                                                                    contractType=contractType,
                                                                                    accountCode=self.account_code
                                                                                    ))
            _ = json.loads(_.futuresOrders)
            return _
        except BaseException as e:
            print e
            return {"status":"error","message":e}
            