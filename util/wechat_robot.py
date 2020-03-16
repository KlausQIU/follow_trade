# !/usr/bin/env python
# coding:utf-8
import sys
sys.path.append("../strategy")

import requests
from ConfigParser import ConfigParser
import json

robot_base_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="

def robot_msg(msg, robot_name="suanfa", mentioned_list=None):
    cf = ConfigParser()
    cf.read("config/wechat_robot.ini")
    robot_key = cf.get(robot_name,"key")
    robot_url = robot_base_url + robot_key
    res = requests.post(robot_url, data=json.dumps({
        "msgtype": "text",
        "text": {
        "content": msg,
        "mentioned_list": mentioned_list,
        }}),headers={'Content-Type': 'application/json' })
    print res
    print res.text
        
