import imp
from multiprocessing.dummy import Process
import redis
import pymysql
import sqllib

def func1(cursor, table, column, value):
    sql1 = "select * from %s where %s='%s'" % (table, column, value)
    cursor.excute(sql1)
    result = cursor.fetchall()
    return result

def init(cursor):
    sql1 = """CREATE TABLE IF NOT EXISTS userinfo (
    username  CHAR(20) NOT NULL,
    password  CHAR(20) NOT NULL,
    token CHAR(30) NOT NULL)"""
    cursor.execute(sql1)
    sql2 = """CREATE TABLE IF NOT EXISTS devicesinfo (
    device CHAR(20) NOT NULL,
    devicename CHAR(20) NOT NULL,
    status CHAR(20) NOT NULL,
    updatetime Datetime,
    humidity CHAR(20) NOT NULL,
    temperature CHAR(20) NOT NULL
    )"""
    cursor.execute(sql2)
    cursor.execute("""CREATE TABLE IF NOT EXISTS usersanddevices(
    username  CHAR(20) NOT NULL,
    device CHAR(20) NOT NULL)""")

class redisconnector(object):
    def __init__(self, host, port, user, passwd, database, init):
        self.sqlconnector = sqllib.__init__(host, user, passwd, database, init)
        self.pool = redis.ConnectionPool(host = host, port = port, decode_responses = True)
        self.r = redis.Redis(connection_pool=self.pool)
        self.update_redis()
        
    def specify(self, s):       #default specify function
        return s+":relation"

    def search(self, table, key, value):#return a dict
        result = self.r.hgetall(value)
        if not result:
            try:
                result = self.sqlconnector.get(table, key, value)   #require a dict, key is the name of primary key, value is the value of primary key
                self.add(table, value, result)
            except:
                print("No related information in sql")
        return result

    def add(self, table, key, value):#value is the value of primary key(key), info is a dict storing key : value
        if type(value) == str:
            relation_key = self.specify(key)
            relation_val = self.specify(value)
            try:
                self.r.sadd(relation_key, value)
                self.r.sadd(relation_val, key)
            except:
                print("Cannot add relations to redis")
            try:
                self.sqlconnector.add(table, relation_key, value)   #second parameter is primary key, third parameter is the value of primary key
                self.sqlconnector.add(table, relation_val, key)
            except:
                print("Cannot add relations to sql")
        elif type(value) == dict:
            try:
                self.r.hmset(key, value)
            except:
                print("Cannot add information to redis")
            try:
                self.sqlconnector.add(table, key, value)            #same as above
            except:
                print("Cannot add information to sql")
        else:
            raise Exception("Type error")

    def delete_all(self, key):#delete all info of specified key, specify is a function to generate a sepecified key
        try:
            relations = list(self.r.smembers(self.specify(key)))
            for relation in relations:
                self.r.srem(self.specify(relation), key)
            self.r.delete(key)
            self.r.delete(self.specify(key))
        except:
            print("Cannot delete specified key from redis")
        try:
            self.sqlconnector.delete_all(key)       #delete information of "key" in all tables
        except:
            print("Cannot delete specified key from sql")

    def delete(self, table, key, value):#delete only a relationship in particular table
        try:
            self.r.srem(self.specify(key), value)
            self.r.srem(self.specify(value), key)
        except:
            print("Cannot delete specified (key : value) relation from redis")
        try:
            self.sqlconnector.delete(table, key, value) #delete information of this pair of {key : value} in this table
        except:
            print("Cannot delete specified key from sql")

    def alter(self, table, key, values):
        if type(values) == dict:
            try:
                self.r.hmset(key, values)
            except:
                print("Cannot change information in redis")
            try:
                self.sqlconnector.alter(table, key, values) #change the value of key in table
            except:
                print("Cannot change informations in sql")
        else:
            raise Exception("Value type error")
        

    def update_redis(self):
        self.r.flushdb()
        tables = self.sqlconnector.get_tables()     #require a list contains all tables' names
        for table in tables:
            pks = self.sqlconnector.get_pks(table)  #require a list contains all primary keys
            for pk in pks:
                kvs = self.sqlconnector.get(table, pk)
                if len(kvs) == 1:
                    value = kvs.values()[0]
                    try:
                        self.r.sadd(self.specify(pk), value)
                        self.r.sadd(self.specify(value), pk)
                    except:
                        print("Cannot add relations to redis")
                else:
                    try:
                        self.r.hmset(pk, value)
                    except:
                        print("Cannot add information to redis")
