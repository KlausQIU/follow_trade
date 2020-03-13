# !/usr/bin/env python
# coding:utf-8

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64


def get_sign_str(message):
    with open('api/pubkey.pem', "r") as f:
        key = f.read()
        rsakey = RSA.importKey(key)  # 导入读取到的公钥
        cipher = Cipher_pkcs1_v1_5.new(rsakey)  # 生成对象
        cipher_text = base64.b64encode(cipher.encrypt(message.encode(encoding="utf-8")))
        return cipher_text
