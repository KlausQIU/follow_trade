# !/usr/bin/env python
# coding:utf-8
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
import monitor_api_service_pb2_grpc
import monitor_api_service_pb2



class Sms:

    def __init__(self):
        sms_channel = grpc.insecure_channel("monitor-grpc-sms-server.monitor.svc.cluster.local:50061")
        self.sms_stub = monitor_api_service_pb2_grpc.MonitorApiStub(sms_channel)

    def common_sms(self,phones,content):
        _ = self.sms_stub.SendSms127152114(monitor_api_service_pb2.Sms127152114(phones=phones,content=content))
        print _


