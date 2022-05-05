import pymysql
import math
from datetime import datetime
import time
class sqlconnector(object):
    def __init__(self, host, user, passwd, database) -> None:
        self.db = pymysql.connect(host=host, user=user, passwd=passwd, database=database)
        self.cursor = self.db.cursor()
        self.cursor.execute("use userdata")
        sql1 = """CREATE TABLE IF NOT EXISTS userinfo (
        username  CHAR(20) NOT NULL,
        password  CHAR(20) NOT NULL,
        token CHAR(30) NOT NULL)"""
        self.cursor.execute(sql1)
        sql2 = """CREATE TABLE IF NOT EXISTS devicesinfo (
        device CHAR(20) NOT NULL,
        devicename CHAR(20) NOT NULL,
        status CHAR(20) NOT NULL,
        updatetime Datetime,
        humidity CHAR(20) NOT NULL,
        temperature CHAR(20) NOT NULL
        )"""
        self.cursor.execute(sql2)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS usersanddevices(
        username  CHAR(20) NOT NULL,
        device CHAR(20) NOT NULL)""")

    def checkLogin(self, username, passwd):
        sql = "SELECT * FROM userinfo WHERE username='%s'" % username
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            password = result[0][1]
        except:  # 用户不存在
            return "user doesnt exist"
        if passwd == password:  # 登录成功
            return "log succeeded"
        else:  # 密码错误
            return "password error"

    def getDevices(self, username):
        sql = "SELECT * FROM usersanddevices WHERE username='%s'" % username
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            res = []
            for i in result:
                self.cursor.execute("SELECT * FROM devicesinfo WHERE device='%s'"%i[1:2])
                result = self.cursor.fetchall()
                if result == ():
                    continue
                res.append(result)
            return res
        except:  # 用户不存在
            return -1

    def checkToken(self, token):
        sql = "SELECT * FROM userinfo WHERE token ='%s'" % token
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            return result[0][0]  # 返回用户名
        except:  # 用户不存在
            return -1

    def updateDeviceStatus(self, device,devicename, status,humidity,temperature):
        sql = "SELECT * FROM devicesinfo WHERE device ='%s'" % device
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            result[0][1]
            print(1)
            try:
                self.cursor.execute("""UPDATE devicesinfo SET status='{}',SET humidty='{}',SET temperature='{}',
                SET updatetime='""".format(status, humidity, temperature) + time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                                    + """'WHERE device = '{}'""".format(device))
                self.db.commit()
            except:
                self.db.rollback()
        except:
            try:
                self.cursor.execute("""INSERT INTO devicesinfo(device,devicename,status,updatetime,humidity,temperature)
                VALUES("{}", "{}", "{}", '""".format(device,devicename,status) + time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                            + """', "{}", "{}")""".format(humidity,temperature))
                self.db.commit()
            except:
                self.db.rollback()
        return

    def addDevice(self, username, device):
        try:
            self.cursor.execute("""INSERT INTO usersanddevices(username,device)
                    VALUES('{}','{}')""".format(username, device))
            self.db.commit()
            return "add succeeded"
        except:
            self.db.rollback()
            return "add failed"

    def deleteDevice(self, username, device):
        try:
            self.cursor.execute(
                """DELETE FROM usersanddevices WHERE username = '{}' AND device = '{}'""".format(username, device))
            self.db.commit()
            return "delete succeeded"
        except:
            self.db.rollback()
            return "delete failed"

    def updateToken(self, username, token):
        try:
            self.cursor.execute("""UPDATE userinfo SET token="{}" WHERE username = '{}'""".format(token, username))
            self.db.commit()
        except:
            self.db.rollback()
        return

    def register(self, username, password):
        try:
            self.cursor.execute(""""SELECT * FROM userinfo WHERE username ='%s'""" % username)  # 用户已经存在
            return "user exits"
        except:  # 用户不存在
            pass

        try:
            token = str(hash(0))
            sql = """INSERT INTO userinfo(username,password,token)
            VALUES("{}","{}","{}")""".format(username, password, token)
            self.cursor.execute(sql)
            self.db.commit()
            return "register succeeded"
        except:
            self.db.rollback()
            return "register failed"

    def closedb(self):
        try:
            self.db.close()
        except:
            print("database cannot be closed")
        else:
            print("database closed")
