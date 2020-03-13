#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# encoding: utf-8 # 客户端调用，用于查看API返回结果
import sys 
reload(sys) 
sys.setdefaultencoding("utf-8") 
append_path = '../../follow_trade'
sys.path.append(append_path)

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
from util.general import *
from HttpMD5Util import buildMySign, httpGet, httpPost
import hmac
import base64
import time
import datetime
import hashlib
import consts as c

def gen_sign(message, secretKey):
    # mac = hmac.new(bytes(secretKey).encode("utf-8"), bytes(message).encode("utf-8"), digestmod='sha256')
    mac = hmac.new(secretKey, message, digestmod=hashlib.sha256)
    d = mac.digest()
    return base64.b64encode(d)


def pre_hash(timestamp, method, request_path, body):
    return str(timestamp) + str.upper(method) + request_path + body


def get_header(api_key, sign, timestamp, passphrase):
    header = dict()
    header[c.CONTENT_TYPE] = c.APPLICATION_JSON
    header[c.OK_ACCESS_KEY] = api_key
    header[c.OK_ACCESS_SIGN] = sign
    header[c.OK_ACCESS_TIMESTAMP] = str(timestamp)
    header[c.OK_ACCESS_PASSPHRASE] = passphrase

    return header


def parse_params_to_str(params):
    url = '?'
    for key, value in params.items():
        url = url + str(key) + '=' + str(value) + '&'

    return url[0:-1]


def get_timestamp():
    now = datetime.datetime.now()
    t = now.isoformat("T")
    return t[:-3] + "Z"

# def get_timestamp():
#     url = c.API_URL + c.SERVER_TIMESTAMP_URL
#     response = requests.get(url)
#     if response.status_code == 200:
#         print response.json()
#         import pdb;pdb.set_trace()
#         return response.json()['iso']
#     else:
#         return ""


def signature(timestamp, method, request_path, body, secret_key):
    if str(body) == '{}' or str(body) == 'None':
        body = ''
    message = str(timestamp) + str.upper(method) + request_path + str(body)
    # mac = hmac.new(bytes(secret_key).encode("utf-8"), bytes(message).encode("utf-8"), digestmod='sha256')
    mac = hmac.new(secret_key, message, digestmod=hashlib.sha256)
    d = mac.digest()
    return base64.b64encode(d)

order_status_dict = {-2:"fail",-1:"canceled",0:"submit" ,1:"partial", 2:"done",3:"submit",4:"cancel"}
granularity_dict = {"1min":60,"3min":180,"5min":300, "15min": 900,
 "30min":1800,"1hour":3600,"2hour":7200,"4hour":14400,"6hour":21600,"12hour":43200,"1day":86400,"1week": 604800}
# 1:开多2:开空3:平多4:平空
type_dict = {1:"buy",2:"sell",3:"ping_buy",4:"ping_sell"}

class OKEXFutureService():

    def __init__(self, account=None):
        self.account = account
        self.API_KEY, self.API_SECRET_KEY,self.PASSPHRASE = get_account_key("okex", self.account)

    def gen_header(self,method,params,request_path):
        timestamp = get_timestamp()
        body = json.dumps(params) if method == c.POST else ""
        if method == c.GET and params:
            request_path += parse_params_to_str(params)
        sign = gen_sign(pre_hash(timestamp, method, request_path, str(body)), self.API_SECRET_KEY)
        header = get_header(self.API_KEY, sign, timestamp, self.PASSPHRASE)
        return header

    def update_instrument_id(self):
        url = c.API_URL + c.FUTURE_PRODUCTS_INFO
        header = self.gen_header(c.GET,{},c.FUTURE_PRODUCTS_INFO)
        try:
            res = requests.get(url,headers=header)
            if res.status_code == 200:
                result = {}
                for info in res.json():
                    if result.keys().__len__() == 3:
                        result["swap"] = "SWAP"
                        with open("../exchange/okex/instrument.json","wb") as f:
                            f.write(json.dumps(result))
                        return {"result":"success"}
                    if info["alias"] in result.keys():
                        continue
                    result[info["alias"]] = info["instrument_id"].split("-")[-1]
        except BaseException as e:
            print e
            return

    def get_instrument_id(self,contractType):
        with open("../exchange/okex/instrument.json","rb") as f:
            info_dict = json.loads(f.read())
        return info_dict.get(contractType)


    def get_ticker(self,symbol,contractType):
        instrument_id = self.get_instrument_id(contractType)
        symbol = symbol.replace("_","-").upper() + "-" + instrument_id
        request_url = c.FUTURE_SPECIFIC_TICKER + symbol + "/ticker"
        url = c.API_URL + request_url
        # /api/futures/v3/instruments/<instrument_id>/ticker
        header = self.gen_header(c.GET,{},request_url)
        try:
            res = requests.get(url,headers=header)
            if res.status_code == 200:
                data = res.json()
                return {"buyOne":float(data["best_bid"]),"sellOne":float(data["best_ask"])}
            else:
                print res.text
                return {}
        except BaseException as e:
            print e
            return {}
    
    def get_kline(self,symbol,contractType, timeType, size=30):
        instrument_id = self.get_instrument_id(contractType)
        symbol = symbol.replace("_","-").upper() + "-" + instrument_id
        post_data = {"granularity": granularity_dict.get(timeType)}
        request_url = c.FUTURE_KLINE + symbol + "/candles"
        url = c.API_URL + request_url
        # /api/futures/v3/instruments/<instrument_id>/ticker
        header = self.gen_header(c.GET,{},request_url)
        try:
            res = requests.get(url,params=post_data, headers=header)
            if res.status_code == 200:
                res = res.json()[:30]
                res.reverse()
                return res
            else:
                print res.text
                return []
        except BaseException as e:
            print e
            return []

    def buy(self,symbol,price,amount,contractType):
        url = c.API_URL + c.FUTURE_ORDER
        instrument_id = self.get_instrument_id(contractType)
        symbol = symbol.replace("_","-").upper() + "-" + instrument_id
        # 1:开多2:开空3:平多4:平空
        params = {"type": 1,"price":price,"size":amount,"instrument_id":symbol,"leverage":20}
        header = self.gen_header(c.POST,params,c.FUTURE_ORDER)
        try:
            res = requests.post(url, data=json.dumps(params), headers=header)
            if res.status_code == 200:
                data = res.json()
                data["result"] = "success"
                data["price"] = price
                data["amount"] = amount
                data["contractType"] = contractType
                return data
            else:
                print res.text
                return {}
        except BaseException as e:
            print e
            return {"result":"fail"}
    
    def sell(self,symbol,price,amount,contractType):
        url = c.API_URL + c.FUTURE_ORDER
        instrument_id = self.get_instrument_id(contractType)
        symbol = symbol.replace("_","-").upper() + "-" + instrument_id
        # 1:开多2:开空3:平多4:平空
        params = {"type": 2,"price":price,"size":amount,"instrument_id":symbol,"leverage":20}
        header = self.gen_header(c.POST,params,c.FUTURE_ORDER)
        try:
            res = requests.post(url, data=json.dumps(params), headers=header)
            if res.status_code == 200:
                data = res.json()
                data["result"] = "success"
                data["price"] = price
                data["amount"] = amount
                data["contractType"] = contractType
                return data
            else:
                print res.text
                return {}
        except BaseException as e:
            print e
            return {"result":"fail"}

    def ping_buy(self,symbol,price,amount,contractType):
        url = c.API_URL + c.FUTURE_ORDER
        instrument_id = self.get_instrument_id(contractType)
        symbol = symbol.replace("_","-").upper() + "-" + instrument_id
        # 1:开多2:开空3:平多4:平空
        params = {"type": 3,"price":price,"size":amount,"instrument_id":symbol,"leverage":20}
        header = self.gen_header(c.POST,params,c.FUTURE_ORDER)
        try:
            res = requests.post(url, data=json.dumps(params), headers=header)
            if res.status_code == 200:
                data = res.json()
                data["result"] = "success"
                data["price"] = price
                data["amount"] = amount
                data["contractType"] = contractType
                return data
            else:
                print res.text
                return {}
        except BaseException as e:
            print e
            return {"result":"fail"}

    def ping_sell(self,symbol,price,amount,contractType):
        url = c.API_URL + c.FUTURE_ORDER
        instrument_id = self.get_instrument_id(contractType)
        symbol = symbol.replace("_","-").upper() + "-" + instrument_id
        # 1:开多2:开空3:平多4:平空
        params = {"type": 4,"price":price,"size":amount,"instrument_id":symbol,"leverage":20}
        header = self.gen_header(c.POST,params,c.FUTURE_ORDER)
        try:
            res = requests.post(url, data=json.dumps(params), headers=header)
            if res.status_code == 200:
                data = res.json()
                data["result"] = "success"
                data["price"] = price
                data["amount"] = amount
                data["contractType"] = contractType
                return data
            else:
                print res.text
                return {}
        except BaseException as e:
            print e
            return {"result":"fail"}

    def getPosition(self,symbol,contractType):
        instrument_id = self.get_instrument_id(contractType)
        instrument_id = symbol.replace("_","-").upper() + "-" + instrument_id
        request_url = c.FUTURE_SPECIFIC_POSITION + instrument_id + "/position"
        url = c.API_URL + request_url
        header = self.gen_header(c.GET,{},request_url)
        try:
            res = requests.get(url, headers=header)
            if res.status_code == 200:
                if not res.json()["holding"]:
                    return {contractType:{symbol:{}}}
                data = res.json()["holding"][0]
                result = {}
                result[contractType] = {symbol: {"long":{
                    "amount": float(data["long_qty"]),
                    "available": float(data["long_avail_qty"]),
                    "boom": float(data["long_liqui_price"]),
                    "ratio": float(data["long_pnl_ratio"]) * 100,
                    "avg_price": float(data["long_avg_cost"])
                },"short": {
                    "amount": float(data["short_qty"]),
                    "available": float(data["short_avail_qty"]),
                    "boom": float(data["short_liqui_price"]),
                    "ratio": float(data["short_pnl_ratio"]) * 100,
                    "avg_price": float(data["short_avg_cost"])}
                }}
                return result
            else:
                print res.text
                return {}
        except BaseException as e:
            print e
            return {"result":"fail"}

    def getAccountInfo(self, symbol,contractType):
        instrument_id = self.get_instrument_id(contractType)
        instrument_id = symbol.replace("_","-").upper() + "-" + instrument_id
        symbol = symbol.replace("_usd", "")
        request_url = c.FUTURE_COIN_ACCOUNT + symbol
        url = c.API_URL + request_url
        header = self.gen_header(c.GET,{},request_url)
        try:
            res = requests.get(url, headers=header)
            if res.status_code == 200:
                data = res.json()
                result = {}
                result["symbol"] = symbol
                result["right"] = float(data["equity"])
                result["auto_margin"] =  int(data["auto_margin"])
                if data["contracts"]:
                    d = data["contracts"][0]
                    result["profit"] = float(d["realized_pnl"])
                    result["unprofit"] = float(d["unrealized_pnl"])
                return result
            return {}
        except BaseException as e:
            print e
            return {"result":"fail"}

    def getOrder(self, symbol, contractType, orderId):
        instrument_id = self.get_instrument_id(contractType)
        instrument_id = symbol.replace("_","-").upper() + "-" + instrument_id
        request_url =  c.FUTURE_ORDER_INFO + instrument_id + "/" + "%s"%orderId
        url = c.API_URL + request_url
        header = self.gen_header(c.GET,{},request_url)
        try:
            res = requests.get(url, headers = header)
            if res.status_code == 200:
                data = res.json()
                data["status"] = order_status_dict.get(int(data["state"]))
                data["result"] = "success"
                data["amount"] = float(data.get("filled_qty")) if data.get("filled_qty") else 0.0
                data["type"] = type_dict.get(int(data["type"])) # 1:开多2:开空3:平多4:平空
                return data
            return {}
        except BaseException as e:
            print e
            return {"result":"fail"}

    def cancelOrder(self,symbol, contractType,orderId):
        instrument_id = self.get_instrument_id(contractType)
        instrument_id = symbol.replace("_","-").upper() + "-" + instrument_id
        request_url =  c.FUTURE_REVOKE_ORDER + instrument_id + "/" + "%s"%orderId
        url = c.API_URL + request_url
        header = self.gen_header(c.POST,{},request_url)
        try:
            res = requests.post(url, data='{}',headers=header)
            if res.status_code == 200:
                data = res.json()
                data["result"] = "success"
                return data
            else:
                print res.text
                return {}
        except BaseException as e:
            print e
            return {"result":"fail"}

    # def orders(self,symbol, contractType):
        





