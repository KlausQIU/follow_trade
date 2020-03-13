# !/usr/bin/env python
# coding:utf-8

import logging
import time
from logging import handlers
import os
from async import async
from db.connection import mysqldbConnection
from datetime import datetime


def log(fileName):
    now_md = time.strftime("%Y_%m_%d")
    fileName = fileName + "_%s" % now_md
    if not os.path.isdir("log"):
        os.mkdir("log")
    logger = logging.getLogger('log/%s.log' % fileName)
    format_str = logging.Formatter('%(asctime)s %(filename)s : %(levelname)s: %(message)s')
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setFormatter(format_str)
    th = handlers.TimedRotatingFileHandler(
        filename='log/%s.log' % fileName, when='D', backupCount=3, encoding='utf-8')
    th.setFormatter(format_str)
    logger.addHandler(sh)
    logger.addHandler(th)
    return logger

#@async
def Log(project, msg):
    now_md = time.strftime("%Y%m%d")
    with open('log/%s_%s.log' % (project.replace("/",""),now_md), 'a') as t:
        now = datetime.now()
        str_time = now.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(msg, unicode):
            msg = msg.encode("utf-8")
        msg = "[" + str_time + "]" + ' ' + msg + "\n"
        t.write(msg)

# @async
# @mysqldbConnection
def dbLog(cursor, data, tableName=None):
    if not tableName:
        return
    insert_sql = "INSERT INTO %s"%tableName
    insert_sql += '('
    insert_sql += ",".join(map(lambda x:"`%s`"%x ,data.keys()))
    insert_sql += ')'
    insert_sql += "VALUES ("
    insert_sql += ",".join(map(lambda x:"'%s'"%x ,data.values()))
    insert_sql += ');'
    print '-'*10+'insert data'+'-'*10
    print insert_sql
    print '-'*10+'insert data'+'-'*10
    try:
        cursor.execute(insert_sql)
    except BaseException as e:
        print e
    
def update_db_order(cursor, order, params=None,tableName=None,project=""):
    if not params.has_key("update_time"):
        params["update_time"] = int(time.time())
    if not params.has_key("update_time_str"):
        params["update_time_str"] = datetime.now()
    sql = "update %s set "%tableName
    for k,v in params.iteritems():
        if type(v) in [int,float]:
            sql += "%s=%s , "%(k,v)
        else:
            sql += "%s='%s' , "%(k,str(v))
    sql = sql[:-2]
    sql += "where buy_order_id='%s';"%(order["buy"]["orderId"])
    print ">>>>>>  update data sql  <<<<<<"
    print sql
    print ">>>>>> update data sql  <<<<<<"
    try:
        res = cursor.execute(sql)
        msg = "数据插入更新成功: %s"%res
        print msg
        Log(project,msg)
        return msg
    except BaseException as e:
        msg = "数据插入更新失败: %s"%e
        print msg
        Log(project,msg)
        return msg


def update_db_future_order(cursor, params=None, whereParams=None, tableName=None, project=""):
    if not params.has_key("update_time"):
        params["update_time"] = int(time.time())
    if not params.has_key("update_time_str"):
        params["update_time_str"] = datetime.now()
    sql = "update %s set "%tableName
    for k,v in params.iteritems():
        if type(v) in [int,float]:
            sql += "%s=%s , "%(k,v)
        else:
            sql += "%s='%s' , "%(k,str(v))
    sql = sql[:-2]
    sql += "where "
    for k,v in whereParams.iteritems():
        if type(v) in [int,float]:
            sql += "%s=%s , "%(k,v)
        else:
            sql += "%s='%s' , "%(k,str(v))
    sql = sql[:-2]     
    print ">>>>>>  update data sql  <<<<<<"
    print sql
    print ">>>>>> update data sql  <<<<<<"
    try:
        res = cursor.execute(sql)
        msg = "数据插入更新成功: %s"%res
        print msg
        Log(project,msg)
        return msg
    except BaseException as e:
        msg = "数据插入更新失败: %s"%e
        print msg
        Log(project,msg)
        return msg