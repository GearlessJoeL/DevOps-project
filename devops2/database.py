import pymysql
class sqlconnector(object):
    def __init__(self, host, user, passwd, database):
        self.db = pymysql.connect(host=host, user=user, passwd=passwd)
        self.cursor = self.db.cursor()
        self.cursor.execute('''select * 
from information_schema.SCHEMATA 
where SCHEMA_NAME = '%s';'''%database)
        res = self.cursor.fetchall()
        if res == ():
            self.cursor.execute('''create database %s''' % database)

        self.cursor.execute("use %s"%database)

        sql1 = """CREATE TABLE IF NOT EXISTS userinfo (
        user_id char(32) primary key,
        user_name  varchar(50) NOT NULL,
        email  varchar(40) default null,
        phone  varchar(50) default null,
        password  varchar(100) NOT NULL,
        privilege int not null,
        otherinfo json default null,
        CHECK ( privilege > -1 and privilege < 2 ))"""
        self.cursor.execute(sql1)

        sql2 = """CREATE TABLE IF NOT EXISTS deviceinfo (
        device_id char(32) primary key,
        device_name varchar(50) NOT NULL,
        bussiness_data json,
        ip varchar(50)
        )"""
        self.cursor.execute(sql2)
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS userdevice(
        user_id  char(32) NOT NULL,
        device_id char(32) NOT NULL,
        constraint pr primary key(user_id,device_id))""")

    def qus(self,dir,table):
        flag = 0
        sql = "SELECT * FROM %s " % table
        if dir == {}:
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
            return res
        sql = sql + "WHERE "
        for i in dir:
            if flag == 0:
                flag = 1
            else:
                sql = sql + "and "
            if dir[i][0] == 0:
                sql = sql + '''%s = '%s' ''' % (i,dir[i][1])
            else:
                sql = sql + '''%s = %s ''' % (i, dir[i][1])
        print(sql)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        print(res)
        return res

    def check(self, dir,table):
        res = self.qus(dir,table)
        return res != ()

    def update(self,dir,new,table):
        flag = 0
        sql = "update %s set " % table
        for i in new:
            if flag == 0:
                flag = 1
            else:
                sql = sql + ", "
            if dir[i][0] == 0:
                sql = sql + '''%s = '%s' ''' % (i, new[i][1])
            else:
                sql = sql + '''%s = %s ''' % (i, new[i][1])
        if dir != {}:
            flag = 0
            sql = sql + "where "
            for i in new:
                if flag == 0:
                    flag = 1
                else:
                    sql = sql + "and "
                if dir[i][0] == 0:
                    sql = sql + '''%s = '%s' ''' % (i, dir[i][1])
                else:
                    sql = sql + '''%s = %s ''' % (i, dir[i][1])
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        self.db.commit()
        return res

    def delete(self,dir,table):
        flag = 0
        sql = "delete from %s " % table
        if dir != {}:
            sql = sql + "where "
            for i in dir:
                if flag == 0:
                    flag = 1
                else:
                    sql = sql + "and "
                if dir[i][0] == 0:
                    sql = sql + '''%s = '%s' ''' % (i, dir[i][1])
                else:
                    sql = sql + '''%s = %s ''' % (i, dir[i][1])
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        self.db.commit()
        return res

    def insert(self,dir,table):
        sql = "insert into %s " % table
        if dir != {}:
            flag = 0
            a = "("
            b = "value("
            for i in dir:
                if flag == 0:
                    flag = 1
                else:
                    a = a + ", "
                    b = b + ", "
                a = a + i
                if dir[i][0] == 0:
                    b = b + ''''%s' ''' % dir[i][1]
                else:
                    b = b +  "%s "%dir[i][1]
            a = a + ')'
            b = b + ')'
            sql = sql + a + b
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
            self.db.commit()
            return res
        return "cant insert null value"
