# !/usr/bin/env python
# coding:utf-8

import os
import sys
sys.path.append("../follow_trade")

from api.okex.okexFutureApiV3 import OKEXFutureService as okf
from util.general import Log

from pydash import collections
import pandas as pd
import numpy as np
import time
import datetime
import json
from ConfigParser import ConfigParser

from copy import deepcopy
import requests


class Follow:
    '''
    初始化：
        一个跟随账号---跟随下单
        一个交易账号---正主
        交易所名称---
    '''
    def __init__(self,trade_account="",exchange="okex"):
        self.trade_account = trade_account
        self.exchange = exchange
        self.strategy = "follow"
        self.default_data = {u'sell_available': 0.0, u'buy_bond': 0.0, u'contract_id': 0, u'buy_price_avg': 0.0, 
                                u'buy_amount': 0.0, u'buy_flatprice': 0.0, 
                                u'symbol': u'eos/usdt', u'buy_profit_real': 0.0,
                                 u'sell_amount':0.0, u'sell_profit_real': 0.0, 
                                 u'sell_bond': 0.0, u'sell_flatprice': 0.0, u'buy_price_cost': 0.0, u'sell_profit_lossratio': 0.0, 
                                 u'contract_type': u'quarter', u'create_date': 0, u'buy_profit_lossratio': 0.0, 
                                u'lever_rate': 20, u'sell_price_avg': 0.0, u'buy_available': 0.0, u'sell_price_cost': 0.0}
        self.last_buy_trade_amount = 0
        self.last_sell_trade_amount = 0
    
    def gen_params(self):
        cf = ConfigParser()
        cf.read("config/%s.ini"%self.trade_account)
        self.coin = cf.get(self.strategy,"coin")
        self.symbol = cf.get(self.strategy,"symbol")
        self.trade_account_code = cf.get(self.strategy,"trade_account_code")
        #import pdb; pdb.set_trace()
        self.follow_account_codes = json.loads(cf.get(self.strategy,"follow_account_codes"))

        self.contract_type = cf.get(self.strategy,"contractType")
        self.trade_amount = cf.get(self.strategy,"trade_amount")
        self.rates = json.loads(cf.get(self.strategy,"rates"))
        self.contractMultiple = int(cf.get(self.strategy,"contractMultiple"))
        self.default_data["symbol"] = self.symbol
        self.default_data["contract_type"] = self.contract_type
        self.default_data["lever_rate"] = 20 if self.contractMultiple == 1 else 10

        self.trade_api = okf(account=self.trade_account_code)
        for code in self.follow_account_codes:
            self.__dict__["follow_api_%s"%(self.follow_account_codes.index(code) + 1)] = okf(account=code)
        for r in self.rates:
            self.__dict__["rate_%s"%(self.rates.index(r) + 1)] = float(r)


    def judge_account(self):
        import pdb;pdb.set_trace()
        trade_account = self.trade_api.getAccountInfo(self.symbol,self.contract_type)
        follow_account = self.follow_api_1.getAccountInfo(self.symbol,self.contract_type) # 第一个能获取到就行，其他不管
        # 判断是否有币
        #if not trade_account.has_key("right") or not follow_account.has_key("right"):
        #    return

        self.handler_account(trade_account,self.trade_account_code)
        self.handler_account(follow_account,self.follow_account_codes[0])

    def show_info(self, data, Type=None, account=None):
        if not Type:
            now = datetime.datetime.now()
            print "启动时间: %s 当前时间: %s  已启动: %s "%(self.startTime,now,now-self.startTime)
            return
        if Type == "account":
            msg = u"账户: %s,剩余币数: %s, 已实现收益: %s"%(account,data["rights"],data["profit"])
            
        if Type == "position":
            msg = u"账户: %s \n"%account
            duo = data["long"]
            kong = data["kong"]
            msg += u"多仓 -- 均价: %s  数量: %s   爆仓价: %s   收益率: %s \n"%(duo["avg_price"],
                                                                        duo["amount"],
                                                                        duo["boom"],
                                                                        duo["ratio"])
            msg += u"空仓 -- 均价: %s  数量: %s   爆仓价: %s   收益率: %s \n"%(kong["avg_price"],
                                                                        kong["amount"],
                                                                        kong["boom"],
                                                                        kong["ratio"])
        print msg

    def handler_account(self,accountInfo,account_code):
        data= {}
        data["rights"] = float(accountInfo["rights"])
        c_info = accountInfo.get(self.contract_type,{})
        data["profit"] = float(c_info.get("profit",0))
        data["unprofit"] = float(c_info.get("unprofit",0))
        self.show_info(data,Type="account",account=account_code)

    def judge_position(self):
        trade_position = self.trade_api.getPosition(self.symbol,contractType=self.contract_type)
        follow_position = self.follow_api_1.getPosition(self.symbol,contractType=self.contract_type)
        
        self.trade_position = trade_position.get(self.contract_type,{})
        if self.trade_position:
            self.show_info(self.trade_position,Type="position",account=self.trade_account_code)
        else:
            # 空仓，填默认值
            self.show_info(self.default_data,Type="position",account=self.trade_account_code)
        
        self.follow_position_1 = follow_position.get(self.contract_type,{})
        if self.follow_position_1:
            self.show_info(self.follow_position_1,Type="position",account=self.follow_account_codes[0])
        else:
            self.show_info(self.default_data,Type="position",account=self.follow_account_codes[0])
        
        for c in range(2,self.follow_account_codes.__len__() + 1):
            follow_position = eval("self.follow_api_%s.getPosition(self.symbol,contractType=self.contract_type,Type=self.contractMultiple)"%c)
            self.__dict__["follow_position_%s"%c] = follow_position.get(self.contract_type,{})
            return True
        return True


    def start(self):
        self.startTime = datetime.datetime.now()
        while True:
            self.show_info("")
            self.gen_params()
            self.judge_account()
            can_go = self.judge_position()
            if not can_go:
                time.sleep(5)
                continue
            
            self.do_trade()
            time.sleep(5)

    def do_trade(self):
        for c in range(1,self.follow_account_codes.__len__() + 1):
            self._do_trade(self.__dict__["follow_position_%s"%c],self.__dict__["follow_api_%s"%c],self.__dict__["rate_%s"%c],Type="buy")
            self._do_trade(self.__dict__["follow_position_%s"%c],self.__dict__["follow_api_%s"%c],self.__dict__["rate_%s"%c],Type="sell")


    def _do_trade(self,follow_position,follow_api,rate,Type=None):
        ticker = follow_api.get_ticker(self.symbol,contractType=self.contract_type)
        if not ticker or not ticker.has_key("buyOne"):
            return
        if Type == "buy":
            compare_price = ticker["sellOne"]
        else:
            compare_price = ticker["buyOne"]

        self.update_trade_amount(compare_price,self.trade_position.get("%s_amount"%Type,0.0),\
            self.trade_position.get("%s_profit_lossratio"%Type),Type=Type)

        diff_amount = int(self.trade_position.get("%s_amount"%Type,0.0) * rate - follow_position.get("%s_amount"%Type,0.0))

        if self.trade_position.get("%s_amount"%Type,0.0) < 1/rate:
            diff_amount = int(follow_position.get("%s_amount"%Type,0.0) * -1)

        if not diff_amount:
            return
        data = {}
        if diff_amount > 0:
            #import pdb;pdb.set_trace()
            insert = False
            if compare_price * 0.99 < self.trade_position.get("%s_price_avg"%Type,0.0) and Type == "buy":
                res = follow_api.buy(self.symbol,compare_price,diff_amount,contractType=self.contract_type,matchPrice=True)
                print "%s加仓: %s"%(Type,res)
                insert = True
            if compare_price * 1.01 > self.trade_position.get("%s_price_avg"%Type,0.0) and Type == "sell":
                res = follow_api.sell(self.symbol,compare_price,diff_amount,contractType=self.contract_type,matchPrice=True)
                print "%s加仓: %s"%(Type,res)
                insert = True
            if insert:
                data["msg"] = "加 %s仓: 价格： %s  数量： %s"%("多" if Type == "buy" else "空",compare_price,abs(diff_amount)/rate)
                data["result"] = 0
                # 插入log#
                Log(self.coin,data["msg"])
        elif diff_amount < 0:
            # 需要减仓 直接市价减
            diff_amount = abs(diff_amount)
            res = eval("follow_api.liqui_%s(self.symbol,compare_price,diff_amount,contractType=self.contract_type,matchPrice=True)"%(Type))
            print "减仓: 数量: %s  结果: %s"%(diff_amount,res)
            data["msg"] = "减 %s仓: 价格： %s  数量： %s"%("多" if Type == "buy" else "空",compare_price,diff_amount/rate)
            coin_count = round(diff_amount/compare_price/20,4)
            data["result"] = 1*coin_count if self.trade_position.get("%s_profit_lossratio"%Type) > 0 else -1 *coin_count
            Log(self.coin,data["msg"])


    def update_trade_amount(self, price, amount, profit_rate, Type=None):
        temp_last_amount = self.__dict__["last_%s_trade_amount"%Type]
        data = {}
        if temp_last_amount > amount:
            # 减仓了，记录
            diff_amount = temp_last_amount - amount
            data["msg"] = "减 %s仓: 价格: %s  数量： %s"%("多" if Type == "buy" else "空",price,diff_amount)
            coin_diff = round(diff_amount*10/price/20,4)
            data["result"] = int(1 * coin_diff) if profit_rate >0 else int(-1 * coin_diff)
            self.__dict__["last_%s_trade_amount"%Type] = amount
            Log(self.coin,data["msg"])
            return
        if temp_last_amount < amount:
            diff_amount = amount - temp_last_amount
            data["msg"] = "加 %s仓: 价格: %s  数量： %s"%("多" if Type == "buy" else "空",price,diff_amount)
            data["result"] = 0
            self.__dict__["last_%s_trade_amount"%Type] = amount
            Log(self.coin,data["msg"])
            return
