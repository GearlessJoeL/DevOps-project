from xmlrpc.client import Fault
import websockets
import asyncio
import sys
import os
import encryption
import json
import re

def check_email(str):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, str)):
        return True
    else:
        return False

encryptor = encryption.prpcrypt()

async def client_connect(websocket):
    while True:
        await websocket.send("bind request")
        response_str = await websocket.recv()
        if "copy" in response_str:
            print("Connect correctly")
            return True

async def login_handler(websocket):
    username = input("Please input username: ")
    password = input("Please input password: ")
    #TODO: encode password
    password = encryptor.encrypt(password)
    msg = json.dumps(["login", username, password])
    await websocket.send(msg)
    recv_msg = await websocket.recv()
    print(f"{recv_msg}")
    
async def logout_handler(websocket):
    msg = json.dumps(["logout"])
    await websocket.send(msg)
    recv_msg = await websocket.recv()
    print(f"{recv_msg}")

async def regist_handler(websocket):
    method = input("Please select regist method(username/email): ")
    method = method.lower()
    if method == "username":
        username = input("Please input username: ")
        password = input("Please input password: ")
        
        password = encryptor.encrypt(password)
        msg = json.dumps(["regist-username", username, password])
        await websocket.send(msg)
        recv_msg = await websocket.recv()
        print(f"{recv_msg}")

    elif method == "email":
        email = input("Please input email: ")
        while not check_email(email):
            email = input("Invalid email address, please input again: ")
        password = input("Please input password: ")
        
        password = encryptor.encrypt(password)
        msg = json.dumps(["regist-regist", email, password])
        await websocket.send(msg)
        recv_msg = await websocket.recv()
        print(f"{recv_msg}")

    else:
        print("Incorrect option")

async def exit_handler(websocket):
    print("Client exit")
    msg = json.dumps(["exit"])
    await websocket.send(msg)
    recv_msg = await websocket.recv()
    print(f"{recv_msg}")

async def client_handler(websocket):
    while True:
        operation = input("Please input operation:")
        operation = operation.lower()
        if operation == "login":
            await login_handler(websocket)
        elif operation == "regist":
            await regist_handler(websocket)
        elif operation == "logout":
            await logout_handler(websocket)
        elif operation == "exit":
            await exit_handler(websocket)
            break


async def client_run(ipaddr):
    async with websockets.connect("ws://" + ipaddr) as websocket:
        await client_connect(websocket)
        await client_handler(websocket)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Incorrect argument count")
        os._exit()
    ipaddr = sys.argv[1] + ':' + sys.argv[2]
    encryptor = encryption.prpcrypt("ndwdndwdndwdndwd")
    asyncio.get_event_loop().run_until_complete(client_run(ipaddr))
