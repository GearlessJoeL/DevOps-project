from multipledispatch import dispatch
import pymysql
import math
from datetime import datetime
import time
class sqlconnector(object):
    def __init__(self,host,user,passwd,database) -> None:
        self.db = pymysql.connect(host=host, user=user, passwd=passwd, database=database)
        self.cursor = self.db.cursor()
    
    @dispatch(str,str,str)
    def get(self, table, key, value):
        sql="""select * from {} where {} = '{}';""".format(table,key,value)
        self.cursor.execute(sql)
        result0 = self.cursor.fetchone()
        if result0 == None:
            ex = Exception
            raise ex
        else:
            result={}
            result={ key : value }
            return result

    def add(self,table,key,value):
        if type(value) == str:
            try:
                self.cursor.execute("""INSERT INTO {} ({}) VALUES('{}')""".format(table,key,value))
                self.db.commit()
                
            except:
                self.db.rollback()
                
        elif type(value) == dict:
            try:
                pknames=self.get_pkname(table)
                for pkname in pknames:
                    allkey = pkname
                    allval = str(key)
                for k,v in value.items():
                    allkey=allkey+","+k
                    if v == None:
                        v = 'NULL'
                    elif type(v)==str:
                        v="'"+v+"'"
                    allval = allval +","+str(v)
                self.cursor.execute("""INSERT INTO {} ({}) VALUES({})""".format(table,allkey,allval))
                self.db.commit()
                
            except:
                self.db.rollback()
                

    def delete_all(self,key):
        try:
            tables=self.get_tables()
            for table in tables:
                pknames=self.get_pkname(table)
                for pkname in pknames:
                    self.cursor.execute("""SELECT * FROM {} WHERE {} = '{}'""".format(table,pkname,key))
                    result = self.cursor.fetchone()
                    if result == None:
                        continue
                    else:
                        self.cursor.execute("""DELETE FROM {} WHERE {}='{}'""".format(table,pkname,key))
                        continue
            self.db.commit()
            
        except:
            self.db.rollback()
            

    def delete(self,table,key,value):
        try:
            self.cursor.execute("""DELETE FROM {} WHERE {}='{}'""".format(table,key,value))
            self.db.commit()
            
        except:
            self.db.rollback()
            

    def alter(self,table,key,values):
        try:
            pks = self.get_pkname(table)
            for pk in pks:
                for k in values:
                    self.cursor.execute("""UPDATE {} SET {}="{}" WHERE {}= '{}'""".format(table,k,values[k],pk,key))
                self.db.commit()
            
        except:
            self.db.rollback()
            

    def get_tables(self):
        sql="""show tables;"""
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        tables=[]
        for i in result:
            tables.append(i[0])
        return tables

    def get_pks(self,table):
        pkname=self.get_pkname(table)
        for m in pkname:
            sql2="""SELECT {} FROM {};""".format(m,table)
            self.cursor.execute(sql2)
            result2 = self.cursor.fetchall()
            pks=[]
            for i in result2:
                pks.append(i[0])
            return pks

    @dispatch(str,str)
    def get(self,table,pk):
        pkname=self.get_pkname(table)
        for m in pkname:
            sql2="""SELECT * FROM {} WHERE {}={}""".format(table,m,pk)
            self.cursor.execute(sql2)
            result2 = self.cursor.fetchone()
            kvs=list(result2)
            return kvs

    def get_pkname(self,table):
        sql1="""SHOW KEYS FROM {} WHERE Key_name = 'PRIMARY'""".format(table)
        self.cursor.execute(sql1)
        result = self.cursor.fetchall()
        result0 = []
        for i in result:
            result0.append(i[4])
        return result0

    def dropTable(self,table):
        try:
            self.cursor.execute("""DROP TABLE {}""".format(table))
            self.db.commit()
        except:
            self.db.rollback()

    def closedb(self):
        try:
            self.db.close()
        except:
            print("database cannot be closed")
        else:
            print("database closed")
