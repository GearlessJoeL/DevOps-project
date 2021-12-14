import socket
import time

host = socket.gethostname()
port = 8080
addr = (host, port)

i = 1
while True:
    app = socket.socket()
    app.connect(addr)
    app.send(str.encode("counting...%d" % i))
    i += 1
    time.sleep(1)
    app.close()
