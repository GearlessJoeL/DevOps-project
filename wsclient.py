from xmlrpc.client import Fault
import websockets
import asyncio
import sys
import os
import encryption
import json
import re
import hmac

def check_email(str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, str)):
        return True
    else:
        return False

#encryptor = encryption.prpcrypt()

def client_connect(websocket):
    websocket.send("bind request")
    response_str = websocket.recv()
    if "copy" == response_str:
        print("Connect correctly")
        return True

def login_handler(websocket):
    websocket.send(json.dumps("login"))
    username = input("Please input username: ")
    password = input("Please input password: ")
    #TODO: encode password
    challenge = websocket.recv()                  #recieve challenge
    print(f"{challenge}")
    print("end")
    password = encryption.hmac_md5(password, challenge)
    msg = json.dumps([username, password])
    websocket.send(msg)                           #send encoded password
    print(f"{msg}")
    recv_msg = websocket.recv()                   #recieve message
    print(f"{recv_msg}")
    
def logout_handler(websocket):
    msg = json.dumps(["logout"])
    websocket.send(msg)
    recv_msg = websocket.recv()
    print(f"{recv_msg}")

def regist_handler(websocket):
    method = input("Please select regist method(username/email): ")
    method = method.lower()

    if method == "username":
        username = input("Please input username: ")
        password = input("Please input password: ")
        challenge = websocket.recv()                  #recieve challenge
        password = encryption.hmac_md5(password, challenge)
        msg = json.dumps(["regist-username", username, password])
        websocket.send(msg)
        recv_msg = websocket.recv()
        print(f"{recv_msg}")

    elif method == "email":
        email = input("Please input email: ")
        while not check_email(email):
            email = input("Invalid email address, please input again: ")
        password = input("Please input password: ")
        challenge = websocket.recv()                  #recieve challenge
        password = encryption.hmac_md5(password, challenge)
        msg = json.dumps(["regist-regist", email, password])
        websocket.send(msg)
        recv_msg = websocket.recv()
        print(f"{recv_msg}")

    else:
        print("Incorrect option")

def exit_handler(websocket):
    print("Client exit")
    msg = json.dumps(["exit"])
    websocket.send(msg)
    recv_msg = websocket.recv()
    print(f"{recv_msg}")

def client_handler(websocket):
    while True:
        operation = input("Please input operation:")
        operation = operation.lower()
        if operation == "login":
            login_handler(websocket)
        elif operation == "regist":
            regist_handler(websocket)
        elif operation == "logout":
            logout_handler(websocket)
        elif operation == "exit":
            exit_handler(websocket)
            break


def client_run(ipaddr):
    with websockets.connect("ws://" + ipaddr) as websocket:
        client_connect(websocket)
        client_handler(websocket)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Incorrect argument count")
        os._exit()
    ipaddr = sys.argv[1] + ':' + sys.argv[2]
    #encryptor = encryption.prpcrypt("ndwdndwdndwdndwd")
    client_run(ipaddr)
