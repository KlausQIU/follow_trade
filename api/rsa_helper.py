# coding=utf-8
import base64

import rsa


class RSA:
    def __init__(self):
        pass

    @staticmethod
    def generator(path, save_pkcs1):
        """
        生成公私钥对
        :param path:
        :param data:
        :return:
        """
        with open(path, 'wb') as f:
            f.write(save_pkcs1)

    @staticmethod
    def make_key(path):
        """
        生成公钥和私钥
        :param path:
        :return:
        """
        try:
            # 生成随机数
            pubkey, privkey = rsa.newkeys(1024)
            # 保存公钥
            with open(path + '/hack_public.pem', 'w+') as f:
                f.write(pubkey.save_pkcs1().decode())
            # 保存私钥
            with open(path + '/hack_private.pem', 'w+') as f:
                f.write(privkey.save_pkcs1().decode())
        except Exception, e:
            print e

    @staticmethod
    def read_pub_key(pub_key_path):
        """
        读取公钥
        :param pub_key_path: 公钥路径
        :return: pubkey 公钥
        """
        try:
            # 导入公钥
            with open(pub_key_path, 'r') as f:
                pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())
            return pubkey
        except Exception, e:
            print e

    @staticmethod
    def read_priv_key(priv_key_path):
        """
        读取私钥
        :param priv_key_path: 私钥路径
        :return: privkey 私钥
        """
        try:
            # 导入私钥
            with open(priv_key_path, 'r') as f:
                privkey = rsa.PrivateKey.load_pkcs1(f.read().encode())
            return privkey
        except Exception, e:
            print e

    @staticmethod
    def encrypt(msg, pubkey):
        """
        加密消息
        :param msg: 明文
        :param pubkey:  公钥
        :return:
        """
        try:
            return base64.b64encode(rsa.encrypt(msg.encode(), pubkey))
        except Exception, e:
            print e

    @staticmethod
    def decrypt(crypto_msg, privkey):
        """
        解密消息
        :param crypto_msg:
        :param privkey:
        :return:
        """
        try:
            return rsa.decrypt(base64.b64decode(crypto_msg), privkey).decode()
        except Exception, e:
            print e


if __name__ == '__main__':
    # (pubkey, privkey) = rsa.newkeys(2048)
    # data = pubkey.save_pkcs1()
    # RSA.generator('rsa_key/pubkey.pem', data)
    # data = privkey.save_pkcs1()
    # RSA.generator('rsa_key/privkey.pem', data)

    pubkey = RSA().read_pub_key('pubkey.pem')
    privkey = RSA().read_priv_key('privkey.pem')
    # 加密消息
    # msg = '0c4292f8-555313d1-ee437c28-b0ee8'
    msg = 'efc9d12a-5dd2f62b-3dbd5b99-223d8'
    encrypt_msg = RSA().encrypt(msg, pubkey)
    print encrypt_msg  # 输出加密消息
    # 解密消息
    decrypt_msg = RSA().decrypt(encrypt_msg, privkey)
    print decrypt_msg  # 输出解密加密消息
