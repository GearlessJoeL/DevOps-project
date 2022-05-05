from sanic import Sanic
import sanic.response
import asyncio
import websockets
from websockets import WebSocketServerProtocol
import time as Time
from sanic.response import text
from sqllib import sqlconnector

import json
import threading
import ctypes
import inspect

def _async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)

class ClearThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.threads = []
    def run(self):
        while 1:
            for tr in self.threads:
                if Time.time() - tr.time > 10:
                    stop_thread(tr)
                    self.threads.remove(tr)
            Time.sleep(10)
    def add(self,t):
        self.threads.append(t)

class ClientThread (threading.Thread):
    def __init__(self, ws,ip,user):
        threading.Thread.__init__(self)
        self.stopped = False
        self.ws = ws
        self.ip = ip
        self.user = user
        self.time = Time.time()
    def run(self):
        while 1:
            data = self.ws.recv()
            print(54354)
            print(data)
            print(type(data))
            data = json.loads(data)
            print(data)
            if(data["Method"] == "getdevices"):
                log1(self.ip + "getdevices")
                self.ws.send("""{"Result": sqldb.getDevices(self.user)}""")
            elif(data["Method"] == "adddevice"):
                log1(self.ip + "adddevices")
                res =sqldb.addDevice(self.user,data["Args"]["device"])
                self.ws.send("""{"Result": res})""")
            elif(data["Method"] == "deletedevice"):
                res = sqldb.deleteDevice(self.user,data["Args"]["device"])
                log1(self.ip + "deletedevice" + str(res))
                self.ws.send("""{"Result": res})""")
            elif(data["Method"] == "pulse"):
                self.time = Time.time()
                log1(self.ip + "pusle")
            else:
                log1(self.ip + "unknown command")
                self.ws.send("""{"ret":"unknown"})""")
app = Sanic("")
sqldb = 0
Clear = ClearThread()

@app.post("/checklog")
async def checklog(request):
    if sqldb.checkToken(request.json["token"])== -1:
        return sanic.response.json({"Result":'0'})
    return sanic.response.json({"Result" : '1'})
def log1(str):
    lo = open("log.log", "a")
    lo.writelines('\n' + str + Time.strftime("%Y-%m-%d %H:%M:%S", Time.localtime()))
    lo.close()

async def log(str):
    lo = open("log.log", "a")
    lo.writelines('\n' + str + Time.strftime("%Y-%m-%d %H:%M:%S", Time.localtime()))
    lo.close()

@app.websocket('/websocket/<token>')
async def pulse(request, ws,token):
    user = sqldb.checkToken(token)
    if user == -1:
        return
    t = Time.time()
    ip = request.ip
    while Time.time() - t < 10:
            data = await ws.recv()
            print(data)
            data = json.loads(data)
            if(data["Method"] == "getdevices"):
                await log(ip + "getdevices")
                res = sqldb.getDevices(user)
                await ws.send("""{"Result":" """+str(res)+""" "}""")
            elif(data["Method"] == "adddevice"):
                await log(ip + "adddevices")
                res =sqldb.addDevice(user,data["Args"]["device"])
                await ws.send("""{"Result": "%s"}""" % str(res))
            elif(data["Method"] == "deletedevice"):
                res = sqldb.deleteDevice(user,data["Args"]["device"])
                await log(ip + "deletedevice" + str(res))
                await ws.send("""{"Result": "%s"}""" % str(res))
            elif(data["Method"] == "pulse"):
                t = Time.time()
                await log(ip + "pusle")
            else:
                await log(ip + "unknown command")
    

@app.post("/updatestatus")
async def updatestatus(request):
    res = sqldb.updateDeviceStatus(request.json["device"],request.json["devicename"],request.json["status"],
                                   request.json["humidity"],request.json["temperature"])
    await log(request.ip + "updatestatus" + str(res))
    return sanic.response.json({"Result":res})

@app.post("/getdevices")
async def getdevices(request):
    username = sqldb.checkToken(request.json["token"])
    if username == -1:
        await log(request.ip + "getdevices" + "please login" )
        return sanic.response.json({"Result":"please login"})
    await log(request.ip + "getdevices" + "succeed")
    return sanic.response.json({"Result":"succeed",
                 "devices":sqldb.getDevices(username)})


@app.post("/deletedevice")
async def deletedevice(request):
    username = sqldb.checkToken(request.json["token"])
    if username == -1:
        await log(request.ip + "deletedevice" + "please login")
        return sanic.response.json({"Result": "please login"})
    res =  sqldb.deleteDevice(username,request.json["device"])
    await log(request.ip + "deletedevice" + str(res) )
    return sanic.response.json({"Result": res})

@app.post("/adddevice")
async def adddevices(request):
    username = sqldb.checkToken(request.json["token"])
    if username == -1:
        await log(request.ip + "adddevice" + "please login" )
        return sanic.response.json({"Result": "please login"})
    res =sqldb.addDevice(username,request.json["device"])
    await log(request.ip + "adddevice" + "succeed")
    return sanic.response.json({"Result": res})


@app.post("/login")
async def login(request):
    res = sqldb.checkLogin(request.json["username"],request.json["password"])
    await log(request.ip + "login" +request.json["username"]+ str(res))
    ret = {"token":""}
    ret["Result"] = res
    if res == "log succeeded":
        ret["token"] = str(hash(request.json["username"]+request.json["password"]))
        sqldb.updateToken(request.json["username"],ret["token"])
    return sanic.response.json(ret)


@app.post("/register")
async def register(request):
    res = sqldb.register(request.json["username"],request.json["password"])
    await log(request.ip+"register"+ str(res) )
    return sanic.response.json({"Result":res})

def initial_database():
    f = open("database.ini", "r")
    host = f.readline()[:-1]
    user = f.readline()[:-1]
    passwd = f.readline()[:-1]
    database = f.readline()
    return sqlconnector(host,user,passwd,database)


if __name__ == "__main__":
  sqldb = initial_database()
  d = {"WEBSOCKET_PING_TIMEOUT": 90}
  app.update_config(d)
  #Clear.start()
  app.run(port=8046)
