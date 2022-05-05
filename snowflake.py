import time
import random
import hashlib

class snowflake(object):
    def __init__(self) -> None:
        self.hashset = set()
        self.md5 = hashlib.md5()


    def generate(self, username) -> int:
        ans = '1'
        t = time.time()
        t = int(round(t * 1000))
        print(len(str(t)))
        t = str(t).rjust(13, '0')
        self.md5.update(username.encode('utf-8'))
        userinfo = self.md5.hexdigest()
        userinfo = '0x' + userinfo
        userinfo = int(userinfo, 16)
        userinfo = userinfo % 10**8
        userinfo = str(userinfo).rjust(8, '0')
        print(userinfo)
        raw = ans + t + userinfo
        tail = random.randint(0, 10**10)
        tail = str(tail).rjust(10, '0')
        ans = raw + tail
        ans = int(ans)
        while ans in self.hashset:
            tail = random.randint(0, 10**10)
            tail = str(tail).rjust(10, '0')
            ans = raw + tail
            ans = int(ans)
        return ans
