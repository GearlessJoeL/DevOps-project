import pymysql

class sqlconnector(object):
    #enviorment must contain a database named "userdata" and a table named "userinfo"
    def __init__(self) -> None:
        self.db = pymysql.connect(host="localhost", user="root", passwd="", database="userdata")
        self.cursor = self.db.cursor()
        self.cursor.execute("use userdata")
        sql = """CREATE TABLE IF NOT EXISTS userinfo (
        username  CHAR(20) NOT NULL,
        password  CHAR(20))"""
        self.cursor.execute(sql)
    
    def check(self, name, passwd):
        sql = "SELECT * FROM userinfo WHERE username='%s'" % name
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            password = result[0][1]
        except:
            print("Error: unable to find user named %s" % name)
            return False
        if passwd == password:
            print("match successfully")
            return True
        else:
            print("Error: incorrect password or username")
            return False

    def closedb(self):
        try:
            self.db.close()
        except:
            print("database cannot be closed")
        else:
            print("database closed")

#test
#conn = sqlconnector()
#conn.check("001", "123456")
#conn.check("ava", "123456")
#conn.check("ava", "xiangwan")
#conn.closedb()
#conn.closedb()