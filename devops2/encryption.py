from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import sys

def encrypt(text,key):
    key = key.encode()

    cryptor = AES.new(key, AES.MODE_CBC, b'0000000000000000')
    # 这里密钥key 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用
    length = 16
    count = len(text)
    if count < length:
        add = (length - count)
        text = (' ' * add) + text
    elif count > length:
        add = (length - (count % length))
        text = (' ' * add) + text
    text = text.encode()
    ciphertext = cryptor.encrypt(
        text)  # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题,所以这里统一把加密后的字符串转化为16进制字符串
    return b2a_hex(ciphertext).decode()

    # 解密后，去掉补足的空格用strip() 去掉
def decrypt(text,key):
    key = key.encode()
    cryptor = AES.new(key, AES.MODE_CBC, b'0000000000000000')
    plain_text = cryptor.decrypt(a2b_hex(text))
    return plain_text.lstrip(' '.encode()).decode()

