from sanic import Sanic
import sanic.response
import asyncio
import websockets
from websockets import WebSocketServerProtocol
import time
from sanic.response import text
from sanic import json
import json as js
import threading
import ctypes
import inspect
import random
from database import sqlconnector
from encryption import encrypt
from encryption import decrypt
from email_sender import var
import string
from snowflake import snowflake
sf = snowflake()
K = "QAQ1234567890QAQ"
app = Sanic("")
sqldb = 0

async def log(str):
    lo = open("log.log", "a")
    lo.writelines('\n' + str + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    lo.close()


def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

class session (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.session = {}
        self.num = 0

    def run(self):
        while 1:
            tem = []
            for i in self.session:
                if(time.time() - self.session[i]["time"] > 60):
                    tem.append(i)
            for i in tem:
                self.session.pop(i)
            time.sleep(60)

    def newtoken(self):
        chars = string.ascii_letters + string.digits
        size = 16
        token = random_string_generator(size, chars)
        while self.session.get(token) is not None:
            token = random_string_generator(size, chars)
        self.session[token] = {}
        self.session[token]["time"] = time.time()
        return token

    def newkey(self,token):
        if self.checktoken(token) is None:
            return None
        size = 16
        chars = string.ascii_letters + string.digits
        self.session[token]["key"] = random_string_generator(size, chars)
        return self.session[token]["key"]

    def checktoken(self,token):
        if self.session.get(token) is not None:
            self.session[token]["time"] = time.time()
            return True
        return False

    def getkey(self,token):
        if self.checktoken(token) is None:
            return None
        return self.session[token]["key"]

    def adduserid(self,token,user_id):
        if self.checktoken(token) is None:
            return None
        self.session[token]["user_id"] = user_id

    def getuserid(self,token):
        return self.session[token].get("user_id")

ses = session()

@app.get("/token")
async def token(request):
    token = ses.newtoken()
    await log(request.ip+" get token")
    return json({"token":token,"code":200,"massage":"成功获得token"})

@app.post("/key")
async def key(request):
    tk = request.json.get("token")
    if ses.checktoken(tk):
        await log(request.ip + " get key")
        return json({"key":ses.newkey(token=tk),
                     "code":200,
                     "massage":"成功获得key"})


@app.post('/pulse')
async def pulse(request):
    tk = request.json.get("token")
    if ses.checktoken(tk) :
        return json({"code": 204})
    return json({"code": 400, "massage": "token已失效"})


@app.websocket('/register')
async def register(request, ws):
    while 1:
        user_name = await ws.recv()
        password = await ws.recv()
        token = await ws.recv()
        key = ses.getkey(token)
        password = decrypt(password,key)
        qus = {"user_name":[0,user_name]}
        res = sqldb.check(qus,"userinfo")
        if res == False:
            await ws.send("check pass")
            break
        await ws.send("user exsist")
    email = await ws.recv()
    phone = ""
    while (1) :
        var1 = var(email)
        var2 = await ws.recv()
        if var1 == var2:
            await ws.send("successfully register")
            break
        await ws.send("varfication code error")
    qus = {"user_id":[0,sf.generate(user_name,"0000")],
        "user_name": [0, user_name],
           "password": [0, encrypt(password,K)],
           "email": [0, email],
           "phone": [0, phone],
           "privilege":[1,0]}
    sqldb.insert(qus,"userinfo")
    await ws.close()
    await log(request.ip + " register seccessfully ")
    return

def getprivilege(token):
    user_id = ses.session[token].get("user_id")
    if user_id is None:
        return -1
    dir = {"user_id":[0,user_id]}
    tem = sqldb.qus(dir,"userinfo")
    if tem == ():
        return -1;
    for i in tem:
        u = 0
        for t in i:
            u = u + 1
            if u == 6:
                return t

@app.post("/loggin")
async def loggin(request):
    inf = request.json
    user_name = inf.get("user_name")
    password = inf.get("password")
    token = inf.get("token")
    key = ses.getkey(token)
    password = decrypt(password, key)
    qus = {"user_name": [0, user_name],
           "password":[0,encrypt(password,K)]}
    res = sqldb.qus(qus,"userinfo")

    if res == ():
        return json({"code":400,
                     "massage":"user doesnt exist or password error"})
    await log("%s log in" % res[0][0])
    ses.adduserid(token,res[0][0])
    await log(request.ip + " register seccessfully ")
    return json({"code":200,
                     "massage":"successfully loggin"})


@app.post("/checktoken")
async def checktoken(request):
    inf = request.json
    token = inf.get("token")
    if ses.checktoken(token):
        return json({"code": 200,
                 "massage": "token valid"})
    return json({"code": 400,
                 "massage": "token invalid"})


@app.post("/checklog")
async def checklog(request):
    inf = request.json
    token = inf.get("token")
    if ses.session[token].get("user_id") is not None:
        return json({"code":200,
                     "massage":"loggin"})
    return json({"code":400,
                     "massage":"no loggin"})



@app.post("/updatestatus")
async def updatestatus(request):
    inf = request.json
    ip = request.ip
    device_id = inf.get("device_id")
    device_name = inf.get("device_id")
    bussiness_data = inf.get("bussiness_data")
    dir = {"device_id":[0,device_id]}
    dir2 = {"device_id": [0, device_id],
            "device_name": [0, device_name],
            "bussiness_data": [0, bussiness_data],
            "ip":[0,ip]}
    if sqldb.check(dir,"deviceinfo") is None:
        sqldb.insert(dir2,"deviceinfo")
    else:
        sqldb.update(dir,dir2)
    return json({"code":200,"massage":"update successfully"})

@app.post("/adddevice")
async def adddevices(request):
    inf = request.json
    token = inf.get("token")
    user_id = ses.getuserid(token)
    if user_id is None:
        return json({"code":400,
                     "massage":"please login"})
    device_id = inf.get("device_id")
    dir = {"device_id":[0,device_id]}
    if sqldb.check(dir,"deviceinfo") is None:
        return json({"code": 400,
                     "massage": "device doesnt exsist"})

    dir["user_id"] = [0,user_id]
    sqldb.insert(dir,"userdevice")


@app.get("/getdevice")
async def getdevices(request):
    inf = request.json
    token = inf.get("token")
    user_id = ses.getuserid(token)
    if user_id is None:
        return json({"code": 400,
                     "massage": "please login"})
    dir = {}
    dir["user_id"] = [0, user_id]
    res = sqldb.qus(dir, "userdevice")
    ret = {"code" : 200,"device":[]}
    for i in res:
        dir = {}
        dir["device_id"] = [0,i[1]]
        ret["device"].append(sqldb.qus(dir,"deviceinfo"))
    return ret

@app.post("/deleteuser")
async def deleteuser(request):
    inf = request.json
    user_name = inf["del_user_name"]
    token = inf.get("token")
    p = getprivilege(token)
    if p < 1:
        await log("%s try to delete %s fail" % (token,user_name))
        return json({"code" : 400,"massage":"Insufficient permissions"})
    await log("%s delete %s " % (token,user_name))
    dir = {"user_name":[0,user_name]}
    sqldb.delete(dir, "user_info")
    sqldb.delete(dir,"user_info")
    return json({"code" : 200,"massage":"delete succussfully"})

def initial_database():
    f = open("database.ini",'r')
    ini = js.load(f)
    f.close()
    host = ini["host"]
    user = ini["user"]
    password = ini["password"]
    database = ini["database"]
    return sqlconnector(host,user,password,database)

if __name__ == "__main__":
  sqldb = initial_database()
  ses.start()
  app.run(port=8010)