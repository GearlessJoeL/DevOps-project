import pymysql
import re

db = pymysql.connect(host="localhost", user="root", password="", database="TESTDB")

cursor = db.cursor()

while True:
    op = input()
    patterns = re.split(r'\s+', op)
    sql = ""

    if patterns[0] == 'ADD':
        id = patterns[1]
        name = patterns[2]
        device_type = patterns[3]
        sql = "INSERT INTO DEVICE(device_id, device_name, type) VALUES ('%s', '%s', '%s')" % (id, name, device_type)
        cursor.execute(sql)
        db.commit()

    elif patterns[0] == 'DEL':
        id = patterns[1]
        sql = "DELETE FROM DEVICE WHERE device_id='%s'" % id
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

    elif patterns[0] == 'GET':
        if len(patterns) == 2:
            id = patterns[1]
            sql = "SELECT * FROM DEVICE WHERE device_id='%s'" % id
        elif len(patterns) == 1:
            sql = "SELECT * FROM DEVICE"
            
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            for row in result:
                print("id='%s', name='%s', type='%s'" % (row[0], row[1], row[2]))
        except:
            print("Error: Unable to fetch data.")

    elif patterns[0] == 'EXIT':
        print("BYE")
        break

    print("MISSION COMPLETED")

db.close()