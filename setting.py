# !/usr/bin/env python
# coding:utf-8

import os

# 1.套利账号:
# 647141f1-91364def-207b5271-fc475
# b8ccaf45-f93f19eb-1fc60033-89346

EX1 = os.environ.get("EX1", "huobi")
# 测试账号
ACCESSKEY_EX1 = os.environ.get("ACCESS_KEY_EX1", "654a22cb-a2cecd1b-60bd6562-f15a5")
ACCESSSEC_EX1 = os.environ.get("ACCESS_SEC_EX1", "13bbf9bd-511b3fd8-07545720-835f0")

# 正式账号
# ACCESSKEY_EX1 = os.environ.get("ACCESS_KEY_EX1", "SoBGjujJBxbFW1WgA15sOSN1tHSzNICt1B0+pL4sohilLGD2aYyX+FS/l01Md4pTSCxHTl28vWIYLuDf1tp3zERmi5CAMgRHitITCrHfqf9S8N53gxIUej1Qvfvm2oz6t4PG+5ppTGOeDBC9CHLewJa2hjWAWbWV2i9O9bdDkukx8st/b1O7svfoeAZsi8htNJECwfWA07NxKJ8lpeOYQXpL1wqGbY9bOscb5rOUqdJNMrsDswsKs3d0OD6y0waJqAXbQgvpsQjAnx96aPXeW402lAkQVQepGXXjuONAmvWZqc4jGg2l4dT3k/E9fTXq6nL7zMdNDo6rGS6gt4OVOA==")
# ACCESSSEC_EX1 = os.environ.get("ACCESS_SEC_EX1", "dvws304VUpxzfRzAGEB+KjnxUhtg/oTze9xuPvFf0xAW2Dc0uYmA9dSdEifpH0s4a+gcrGUhnzHBqAX+RAVE8MB96PLoKlq1tFaCKQu8iNUYTzaJLfXSRwrXabrZ9rXkTbSLENcmLyf8qiqHGON0g3+f5ErUT1t3FA6FIJK/jKUS0cgXi4oOeymUBeEEyJaPd4Tj9AB1Qf1R8RBiscF/3HoJJFymexvXphUDNf1cQs8aoKpp0qXg+TjeqKIMMXkZKkmVtLdE2Ksq0Abq1L72+hSKhxpF9fPv/MB61rfb8UcdK5rJ67DnFRiX941v2FmuG8y7vLB2KBAbnZ6c1vOx6g==")
EX1_FEE = os.environ.get("EX1_FEE", 0.00035)

EX2 = os.environ.get("EX2", "coinex")
# 测试账号
ACCESSKEY_EX2 = os.environ.get("ACCESS_KEY_EX2", "D6DAD784CEF548F78D3913F5E9BB8574")
ACCESSSEC_EX2 = os.environ.get("ACCESS_SEC_EX2", "02A4286124F24906B5B7BEEEC41ED20B1B25E1AB596A9493")
# 正式账号
# ACCESSKEY_EX2 = os.environ.get("ACCESS_KEY_EX2", "LsHr8g1fOWHYqrS7e01lyYkO6EN+zXLRiI9Qy/Xaz7eDoVjC/fpyfLZ9LR65TpLp8ytrOUftWra5Y6Vu8TIrde4p9PiSJo4N8Eao2G0igd+mZDhDOnsP2d+XOLg+WL/aqbkDrxpn0MWTNEnP+QlUu75schMNUy1AipjV9aNk96Su9j47Z2QJXWb9XhZkUvl10uekEc476SQ3MZ/nasxEnFkQv+5p3GNRdOAR56SsJk94Fs1AC7wuiQ8ElaoW9nOKxJa2zUlLjxNO4HImLzA8dBhIcScbsTBve33P0kBwLq+d7Hcq/7DBwXN5zEIgGYzTyhZPimzIuolbcE/BCZuXYw==")
# ACCESSSEC_EX2 = os.environ.get("ACCESS_SEC_EX2", "PstHD9Gdk6DqGM73AWBDuV18veFXiqyo+C2rZMrjTWH/Xdp+m4Y0x8I5XYjppMeNX21wB0HPdmgHtShkU/LbMiwWc44q9OzwsFLKqSjrgCSSoYycjVn3Z/J0le6g/rRnkIqD56lrgYf6BBn3gcQ9JdZa14w4sJuCFKtCbf3EHwGUbo2Jw4cDzR8+QzrcD465NrvqX9tguPOUiI7buyRUF58INTDONUh6TEKVja36RjtPBVkI+8Y7+eTv+ZHWE85uWojOVibQSWgDFdt1sz3QhKE7Vy0HiyJEAPWNRdKOLrTC/qskDWwnEkxFoj1eLKZuodBi0U09m2nMZYmxK9Mmnw==")
EX2_FEE = os.environ.get("EX2_FEE", 0.00025)

# 初始仓位
BASE_EX1_COIN = os.environ.get("BASE_EX1_COIN",1.15006 )
BASE_EX1_PAY = os.environ.get("BASE_EX1_PAY", 18785.4613741)
BASE_EX2_COIN = os.environ.get("BASE_EX2_COIN", 2.400)
BASE_EX2_PAY = os.environ.get("BASE_EX2_PAY", 9867.4077247)

# "tov5pYkFDz2JtvPBPZglDKRPlh2Dt50TybH8RrBh69r9yIndyugUhzBsjOEt0hU7"
# "imMG1FLrcDTJmWfm5Akp9lC7Jk1YpvdV8O7dtisLOnCqsrDtCkv80E6KnhgaoSSN"

# 单次交易的数量
AMOUNT = os.environ.get("AMOUNT", 0.1)

# 当前交易对的精度
PRICE_PRECISION = os.environ.get("PRICE_PRECISION", 2)
AMOUNT_PRECISION = os.environ.get("AMOUNT_PRECISION", 4)


# 限制最大未成交委托单数
LIMIT_UNFINISH = os.environ.get("LIMIT_UNFINISH", 20)

# coinex 您的API:诺德
# Access ID:D6DAD784CEF548F78D3913F5E9BB8574
# Secret Key:02A4286124F24906B5B7BEEEC41ED20B1B25E1AB596A9493

# 2.扫描频率： 单位：秒
INTERVAL = os.environ.get("INTERVAL", 2)

# 3.Influxdb 相关信息：
# monitor display
# monitor-influxdb-influxdb.monitor.svc.cluster.local
TABLE = os.environ.get("TABLE", "arbitrage_settle_account")
HOST = os.environ.get("HOST", "monitor-influxdb-influxdb.monitor.svc.cluster.local")
PORT = os.environ.get("PORT", 8086)
USER = os.environ.get("USER", "rainbow")
PASSWORD = os.environ.get("PASSWORD", "rainbow")
DATABASE = os.environ.get("DATABASE", "monitor")

ORDERTABLE = os.environ.get("ORDERTABLE", "markerArbitrage_order_result")

# mysqlDB 相关信息
MYSQLHOST = os.environ.get("MYSQLHOST","47.52.98.113")
MYSQLPORT= os.environ.get("MYSQLPORT",31000)
MYSQLUSER = os.environ.get("MYSQLUSER", "root")
MYSQLPASSWORD= os.environ.get("MYSQLPASSWORD", "ztWZyubY4Ebfh7Ww")
MYSQLDATABASE= os.environ.get("MYSQLDATABASE", "arbitrage")
MYSQLTABLE = os.environ.get("MYSQLTABLE", "arbitrage_profit")

# 4.交易所及交易对相关信息：

ASSET1 = os.environ.get("ASSET1", "btc")
ASSET2 = os.environ.get("ASSET2", "usdt")

# 5.套利服务名称：
PROJECT = os.environ.get("PROJECT")

# GRPC
GRPC_IP = os.environ.get("GRPC_IP", "47.52.94.220")
GRPC_PORT = os.environ.get("GRPC_PORT", "50052")


URL = "http://localhost:8765/status/?format=prettyjson"
