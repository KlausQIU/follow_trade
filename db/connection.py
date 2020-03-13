# !/usr/bin/env python
# coding:utf-8

from setting import *

from influxdb import InfluxDBClient

import functools

import MySQLdb
from MySQLdb.converters import conversions


def influxdbConnection(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kw):
        self.client = InfluxDBClient(HOST, PORT, USER, PASSWORD, DATABASE)
        res = func(self, *args, **kw)
        self.client.close()
        return res
    return wrapper

def influxdbOutConnection(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kw):
        self.client = InfluxDBClient("47.75.13.223", "8086", "rainbow", "rainbow@InfluxDB223", "monitor")
        res = func(self, *args, **kw)
        self.client.close()
        return res
    return wrapper


def mysqldbConnection(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kw):
        try:
            conv=conversions.copy()
            conv[246]=float    # convert decimals to floats
            conv[10]=str 
            self.cx = MySQLdb.connect(host=MYSQLHOST,
                                        user=MYSQLUSER, 
                                        passwd=MYSQLPASSWORD,
                                        db=MYSQLDATABASE, 
                                        port=MYSQLPORT,
                                        charset='utf8',
                                        conv=conv,
                                        connect_timeout=20)
            self.cursor = self.cx.cursor()
            res = func(self,*args,**kw)
            self.cx.commit()
            self.cursor.close()
            self.cx.close()
            return res
        except Exception as e:
            print e
            return None
    return wrapper



