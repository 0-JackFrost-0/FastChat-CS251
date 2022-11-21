import sqlite3

def create_unsent_table(name,path):
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    query = '''CREATE TABLE IF NOT EXISTS ?(sender TEXT,message TEXT, type TEXT,time DATETIME)'''
    cur.execute(query,(name,))
    connection.commit()
    cur.close()
    connection.close()

def insert_to_unsent_db(path,name, sender,message,type,datetime):
    try:
        connection = sqlite3.connect(path)
        cur = connection.cursor()
        count = cur.execute(f"SELECT COUNT(*) FROM {name}")
        if(count < 10):
            query = '''INSERT INTO ? VALUES(?,?,?,?)'''
            cur.execute(query,(name,sender,message,type,datetime))
            print(f"Successfully stored the message for {name}")
            return True
        else:
            mintime = cur.execute(f"SELECT MIN(time) FROM {name}")
            cur.execute(f"DELETE FROM {name} WHERE time={mintime}")
            query = '''INSERT INTO ? VALUES(?,?,?,?)'''
            cur.execute(query,(name,sender,message,type,datetime))
            print(f"Successfully stored the message for {name}")
            return True
    except:
        print(f"Failed to store the message for {name}")
        return False
    
def return_all_messages(path,name):
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute(f"SELECT * from {name} ORDER BY time")
    messages = cur.fetchall()
    cur.execute(f"DELETE FROM {name}")
    cur.close
    connection.close()
    return messages


def create_read_table(name,path):
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    query = '''CREATE TABLE IF NOT EXISTS ?(sender TEXT,message TEXT, type TEXT,time DATETIME)'''
    cur.execute(query,(name,))
    connection.commit()
    cur.close()
    connection.close()

def insert_to_read_db(path,name, sender,message,type,datetime):
    try:
        connection = sqlite3.connect(path)
        cur = connection.cursor()
        count = cur.execute(f"SELECT COUNT(*) FROM {name}")
        if(count < 10):
            query = '''INSERT INTO ? VALUES(?,?,?,?)'''
            cur.execute(query,(name,sender,message,type,datetime))
            print(f"Successfully stored the message for {name}")
            return True
        else:
            mintime = cur.execute(f"SELECT MIN(time) FROM {name}")
            cur.execute(f"DELETE FROM {name} WHERE time={mintime}")
            query = '''INSERT INTO ? VALUES(?,?,?,?)'''
            cur.execute(query,(name,sender,message,type,datetime))
            print(f"Successfully stored the message for {name}")
            return True
    except:
        print(f"Failed to store the message for {name}")
        return False
    
def return_all_messages(path,name):
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute(f"SELECT * from {name} ORDER BY time")
    messages = cur.fetchall()
    cur.close
    connection.close()
    return messages