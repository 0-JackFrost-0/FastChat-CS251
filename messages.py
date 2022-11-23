import sqlite3

def create_unread_table(path):
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    query = '''CREATE TABLE IF NOT EXISTS UNREAD(sender TEXT,receiver TEXT,message TEXT, type TEXT,time DATETIME,grpname TEXT DEFAULT NULL)'''
    cur.execute(query)
    connection.commit()
    cur.close()
    connection.close()

def insert_to_unread_db(path,sender,receiver,message,type,datetime,grp):
    try:
        connection = sqlite3.connect(path)
        cur = connection.cursor()
        count = cur.execute(f"SELECT COUNT(*) FROM UNREAD WHERE receiver = '{receiver}'").fetchall()[0][0]
        if(count < 10):
            query = '''INSERT INTO UNREAD VALUES(?,?,?,?,?,?)'''
            cur.execute(query,(sender,receiver,message,type,datetime,grp))
            print(f"Successfully stored the message for {receiver}")
            connection.commit()
            cur.close()
            connection.close()
            return True
        else:
            mintime = cur.execute(f"SELECT MIN(time) FROM UNREAD WHERE receiver = '{receiver}'").fetchall()[0][0]
            cur.execute(f"DELETE FROM UNREAD WHERE time='{mintime}' ")
            query = '''INSERT INTO UNREAD VALUES(?,?,?,?,?,?)'''
            cur.execute(query,(sender,receiver,message,type,datetime,grp))
            print(f"Successfully stored the message for {receiver}")
            connection.commit()
            cur.close()
            connection.close()
            return True
    except Exception as e:
        print(e)
        print(f"Failed to store the message for {receiver}")
        return False
    
def return_all_unread_messages(path,name):
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute(f"SELECT * from UNREAD WHERE receiver = '{name}' ORDER BY time")
    messages = cur.fetchall()
    cur.execute(f"DELETE FROM UNREAD WHERE receiver = '{name}'")
    connection.commit()
    cur.close()
    connection.close()
    return messages


def create_read_table(path):
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    query = '''CREATE TABLE IF NOT EXISTS READ(sender TEXT,receiver TEXT,message TEXT, type TEXT,time DATETIME,grpname TEXT DEFAULT NULL)'''
    cur.execute(query)
    connection.commit()
    cur.close()
    connection.close()

def insert_to_read_db(path,sender,receiver,message,type,datetime,grp):
    try:
        connection = sqlite3.connect(path)
        cur = connection.cursor()
        count = cur.execute(f"SELECT COUNT(*) FROM READ where receiver = '{receiver}'").fetchall()[0][0]
        if(count < 10):
            query = '''INSERT INTO READ VALUES(?,?,?,?,?,?)'''
            cur.execute(query,(sender,receiver, message,type,datetime,grp))
            print(f"Successfully stored the message for {receiver}")
            connection.commit()
            cur.close()
            connection.close()
            return True
        else:
            mintime = cur.execute(f"SELECT MIN(time) FROM READ where receiver = '{receiver}'").fetchall()[0][0]
            cur.execute(f"DELETE FROM READ WHERE time='{mintime}' ")
            query = '''INSERT INTO READ VALUES(?,?,?,?,?,?)'''
            cur.execute(query,(sender,receiver, message,type,datetime,grp))
            print(f"Successfully stored the message for {receiver}")
            connection.commit()
            cur.close()
            connection.close()
            return True
    except Exception as e:
        print(e)
        print(f"Failed to store the message for {receiver}")
        return False
    
def return_all_read_messages(path,name):
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute(f"SELECT * from READ WHERE receiver = '{name}' ORDER BY time")
    messages = cur.fetchall()
    connection.commit()
    cur.close()
    connection.close()
    return messages