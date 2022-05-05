import datetime
import websocket
import asyncio
import requests
import json

url = "://8.130.20.66:8046"

token = ""
async def deletedevice(ws):
    print("please enter device")
    loop = asyncio.get_event_loop()
    device =  str(await loop.run_in_executor(None, input, ""))
    ws.send("""{"Method":"deletedevice",
                  "Args":{"device":"%s"}}""" % device)
    res = ws.recv()
    print(res)
    res = json.loads(res)
    print(res["Result"])

async def getdevices(ws):
    ws.send("""{"Method": "getdevices"}""")
    res = ws.recv()
    res = json.loads(res)
    print(res["Result"])

async def adddevice(ws):
    loop = asyncio.get_event_loop()
    print("please enter device")
    device = str(await loop.run_in_executor(None, input, ""))
    ws.send("""{"Method": "adddevice",
                  "Args": {"device": "%s"}}""" % device)
    res = ws.recv()
    res = json.loads(res)
    print(res["Result"])

async def mune(ws,p):
    while True:
        print("please enter command")
        loop = asyncio.get_event_loop()
        command = str(await loop.run_in_executor(None, input, "")).lower()
        if command == "login":
            print("You're already logged in")
        elif command == "register":
            await register()
        elif command == "getdevices":
            await getdevices(ws)
        elif command == "adddevice":
            await adddevice(ws)
        elif command == "deletedevice":
            await deletedevice(ws)
        elif command == "close":
            quit(1)
        elif command == "quit":
            global token
            token = ""
            p.stop = True
            ws.close()
            return
        else:
            print("unknown command")
async def login():
    global token
    loop = asyncio.get_event_loop()

    print("please enter username")
    username =  str(await loop.run_in_executor(None, input, ""))
    print("please enter password")
    password = str(await loop.run_in_executor(None, input, ""))
    res = requests.post(url="http://8.130.20.66:8046/login", json = {"username" : username,
                                                "password":password})
    
    if res.json()["Result"] == 0:
        print("You are already logged in")
        return
    print(res.json()["Result"])
    if res.json()["Result"] == "log succeeded":
        token = res.json()["token"]
        ws = websocket.create_connection("ws://8.130.20.66:8046/websocket/"+token)
        loop = asyncio.get_event_loop()
        p = pusle(ws)
        loop.create_task(p.pus())
        await mune(ws,p)



class pusle :
    def __init__(self,ws):
        self.ws = ws
        self.stop = False
    async def pus(self):
        while not self.stop:
            self.ws.send("""{"Method" : "pulse"}""")
            await asyncio.sleep(1)


async def register():
    print("please enter username")
    loop = asyncio.get_event_loop()
    username = str(await loop.run_in_executor(None, input, "")).lower()
    print("please enter password")
    password  = str(await loop.run_in_executor(None, input, "")).lower()
    res = requests.post(url="http://8.130.20.66:8046/register", json={"username": username,
                                                     "password": password})
    print(res.json()["Result"])

async def m1():
    while True:
        print("please enter command")
        loop = asyncio.get_event_loop()
        command = str(await loop.run_in_executor(None, input, "")).lower()
        if command == "login":
            await login()
        elif command == "register":
            await register()
        elif command == "getdevices":
            print("please log in")
        elif command == "adddevice":
            print("please log in")
        elif command == "deletedevice":
            print("please log in")
        elif command == "close":
            quit(1)
        else:
           print("unknown command")

async def main():
    loop = asyncio.get_event_loop()
    loop.create_task(m1())
    while 1:
        await asyncio.sleep(0)
if __name__ == "__main__":
    asyncio.run(main())