# !/usr/bin/env python
# coding:utf-8

import sys
from main import Follow

fileName = sys.argv[0].split("/")[-1][:-3]

def start():
    try:
        follow = Follow(trade_account=fileName,exchange="okex")
        follow.start()
    except KeyboardInterrupt:
        follow.write_record()

if __name__ == '__main__':
    start()