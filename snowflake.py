import time
import random
import hashlib

class snowflake(object):
    def __init__(self) -> None:
        self.hashset = set()
        self.md5 = hashlib.md5()

    def generate(self, username, header) -> int:
        #header is a 4byte stirng that specify the type of the series number
        ans = header
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
        tail = random.randint(0, 10**7)
        tail = str(tail).rjust(7, '0')
        ans = raw + tail
        ans = int(ans)
        while ans in self.hashset:
            tail = random.randint(0, 10**7)
            tail = str(tail).rjust(7, '0')
            ans = raw + tail
            ans = int(ans)
        return ans


# def main() -> None:
#     sf = snowflake()
#     val = sf.generate("010ybb")
#     print(val)
#     print(len(str(val)))

# if __name__ == "__main__":
#     main()
