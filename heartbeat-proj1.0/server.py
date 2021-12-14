import socket
import time

host = socket.gethostname()
port = 8080
addr = (host, port)

app = socket.socket()
app.bind(addr)

app.listen(5)
print("listening...")
app.settimeout(5)

while True:
    client_connection, client_address = app.accept()
    print('link address:')
    print(client_address)
    pre = time.time()
    while True:
        cur = time.time()
        try:
            client_connection, client_address = app.accept()
        except:
            if (cur - pre) > 5:
                print("offline")
                break
            elif (cur - pre) <= 5 and (cur - pre) >= 2:
                print("timeout")
        else:
            data = client_connection.recv(1024)
            print(data)
            pre = cur
    client_connection.close()