import pymysql


def GetConn():
    try:
        conn = pymysql.connect(host='localhost', user='root', passwd='z499096', port=3306, database='university')
        print("数据库连接成功")
        return conn
    except Exception as e:
        print(e)
        return None


def CloseConn(conn, cursor):
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("数据库关闭成功")
    except Exception as e:
        print(e)
        return None
