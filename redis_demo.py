import rediscontroller
import sqllib
import pymysql
import encryption

def init():
    conn = pymysql.connect(host='localhost',user='root',password='',charset='utf8mb4')
    cursor = conn.cursor()
    sql = "CREATE DATABASE IF NOT EXISTS testdb2" 
    cursor.execute(sql)
    cursor.execute("use testdb")
    sql1 = """CREATE TABLE IF NOT EXISTS userinfo (
        user_id   INTEGER  Primary key,
        username  VARCHAR(50),
        email     VARCHAR(40),
        phone     VARCHAR(40),
        password  VARCHAR(100) NOT NULL,
        privilege INT check(privilege=0 or privilege=1),
        otherinfo json);"""
    cursor.execute(sql1)
    sql2 = """CREATE TABLE IF NOT EXISTS devicesinfo (
        device_id INTEGER Primary key,
        devicename VARCHAR(50) NOT NULL,
        bussiness_data json
        );"""
    cursor.execute(sql2)
    sql3 = """CREATE TABLE IF NOT EXISTS Device_user_relation(
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES userinfo (user_id),
        device_id INTEGER NOT NULL,
        FOREIGN KEY (device_id) REFERENCES devicesinfo(device_id),
        PRIMARY KEY(user_id,device_id)
        );"""
    cursor.execute(sql3)

if __name__ == "__main__":
    init()
    rc = rediscontroller.redisconnector('localhost', '6379', 'root', '', 'testdb')
    info = {'username': 'lingyining', 'email': '010@ybb.com', 'phone': '123456789010', 'password': '010ybb', 'privilege': '1'}
    rc.add('userinfo', '010', info)
    print(rc.search('userinfo', 'user_id', '010'))
    # encryptor = encryption.prpcrypt('ndwdndwdndwdndwd')
    # print(len(encryptor.encrypt('lingyining')))