import sqlite3

def create_unread_table(path):
    """Creates a table to store the unread messages, if it doesn't exist

    :param path: Path of the messages database
    :type path: str
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    query = '''CREATE TABLE IF NOT EXISTS UNREAD(sender TEXT,receiver TEXT,message TEXT, type TEXT,time DATETIME,aes_key TEXT,grpname TEXT DEFAULT NULL)'''
    cur.execute(query)
    connection.commit()
    cur.close()
    connection.close()

def insert_to_unread_db(path,sender,receiver,message,type,datetime,aes_key,grp):
    """Insert new entries in the unread table

    :param path: Path of the messages database
    :type path: str
    :param sender: Sender of the message
    :type sender: str
    :param receiver: Receiver of the message
    :type receiver: str
    :param message: The actual message sent
    :type message: str
    :param type: The type of the messsage sent
    :type type: str
    :param datetime: The date and time when the message was sent
    :type datetime: str
    :param aes_key:  The encrypted AES key to be stored for decrypting the message
    :type aes_key: binary
    :param grp: Gives the grp_name in which the message was shared, otherwise gives None if Direct message
    :type grp: str
    :return: Returns True if inserted successfully, else returns False
    :rtype: bool
    """
    try:
        connection = sqlite3.connect(path)
        cur = connection.cursor()
        count = cur.execute(f"SELECT COUNT(*) FROM UNREAD WHERE receiver = '{receiver}'").fetchall()[0][0]
        if(count < 10):
            query = '''INSERT INTO UNREAD VALUES(?,?,?,?,?,?,?)'''
            cur.execute(query,(sender,receiver,message,type,datetime,aes_key,grp))
            print(f"Successfully stored the message for {receiver}")
            connection.commit()
            cur.close()
            connection.close()
            return True
        else:
            mintime = cur.execute(f"SELECT MIN(time) FROM UNREAD WHERE receiver = '{receiver}'").fetchall()[0][0]
            cur.execute(f"DELETE FROM UNREAD WHERE time= '{mintime}' ")
            query = '''INSERT INTO UNREAD VALUES(?,?,?,?,?,?,?)'''
            cur.execute(query,(sender,receiver,message,type,datetime,aes_key,grp))
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
    """Returns the last 10 unread messages of the user

    :param path: Path of the messages database
    :type path: str
    :param name: The name of the user to find the unread messages of
    :type name: str
    :return: Returns a list of one-element tuples consisting of the unread messages
    :rtype: list
    """
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
    """Creates a table to store the read messages, if it doesn't exist

    :param path: Path of the messages database
    :type path: str
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    query = '''CREATE TABLE IF NOT EXISTS READ(sender TEXT,receiver TEXT,message TEXT, type TEXT,time DATETIME,aes_key TEXT,grpname TEXT DEFAULT NULL)'''
    cur.execute(query)
    connection.commit()
    cur.close()
    connection.close()

def insert_to_read_db(path,sender,receiver,message,type,datetime,aes_key,grp):
    """Insert new entries in the read table

    :param path: Path of the messages database
    :type path: str
    :param sender: Sender of the message
    :type sender: str
    :param receiver: Receiver of the message
    :type receiver: str
    :param message: The actual message sent
    :type message: str
    :param type: The type of the messsage sent
    :type type: str
    :param datetime: The date and time when the message was sent
    :type datetime: str
    :param aes_key:  The encrypted AES key to be stored for decrypting the message
    :type aes_key: binary
    :param grp: Gives the grp_name in which the message was shared, otherwise gives None if Direct message
    :type grp: str
    :return: Returns True if inserted successfully, else returns False
    :rtype: bool
    """
    try:
        connection = sqlite3.connect(path)
        cur = connection.cursor()
        count = cur.execute(f"SELECT COUNT(*) FROM READ where receiver = '{receiver}'").fetchall()[0][0]
        if(count < 10):
            query = '''INSERT INTO READ VALUES(?,?,?,?,?,?,?)'''
            cur.execute(query,(sender,receiver, message,type,datetime,aes_key,grp))
            print(f"Successfully stored the message for {receiver}")
            connection.commit()
            cur.close()
            connection.close()
            return True
        else:
            mintime = cur.execute(f"SELECT MIN(time) FROM READ where receiver = '{receiver}'").fetchall()[0][0]
            cur.execute(f"DELETE FROM READ WHERE time= '{mintime}' ")
            query = '''INSERT INTO READ VALUES(?,?,?,?,?,?,?)'''
            cur.execute(query,(sender,receiver, message,type,datetime,aes_key,grp))
            print(f"Successfully stored the message for {receiver}")
            connection.commit()
            cur.close()
            connection.close()
            return True
    except Exception as e:
        print(e)
        print(f"Failed to store the message for {receiver}")
        return False

def insert_to_read_db_silent(path,sender,receiver,message,type,datetime,aes_key,grp):
    """Insert new entries in the read table

    :param path: Path of the messages database
    :type path: str
    :param sender: Sender of the message
    :type sender: str
    :param receiver: Receiver of the message
    :type receiver: str
    :param message: The actual message sent
    :type message: str
    :param type: The type of the messsage sent
    :type type: str
    :param datetime: The date and time when the message was sent
    :type datetime: str
    :param aes_key:  The encrypted AES key to be stored for decrypting the message
    :type aes_key: binary
    :param grp: Gives the grp_name in which the message was shared, otherwise gives None if Direct message
    :type grp: str
    :return: Returns True if inserted successfully, else returns False
    :rtype: bool
    """
    try:
        connection = sqlite3.connect(path)
        cur = connection.cursor()
        count = cur.execute(f"SELECT COUNT(*) FROM READ where receiver = '{receiver}'").fetchall()[0][0]
        if(count < 10):
            query = '''INSERT INTO READ VALUES(?,?,?,?,?,?,?)'''
            cur.execute(query,(sender,receiver, message,type,datetime,aes_key,grp))
            connection.commit()
            cur.close()
            connection.close()
            return True
        else:
            mintime = cur.execute(f"SELECT MIN(time) FROM READ where receiver = '{receiver}'").fetchall()[0][0]
            cur.execute(f"DELETE FROM READ WHERE time= '{mintime}' ")
            query = '''INSERT INTO READ VALUES(?,?,?,?,?,?,?)'''
            cur.execute(query,(sender,receiver, message,type,datetime,aes_key,grp))
            connection.commit()
            cur.close()
            connection.close()
            return True
    except Exception as e:
        print(e)
        print(f"Failed to store the message for {receiver}")
        return False
    
def return_all_read_messages(path,name):
    """Returns the last 10 read messages of the user

    :param path: Path of the messages database
    :type path: str
    :param name: The name of the user to find the unread messages of
    :type name: str
    :return: Returns a list of one-element tuples consisting of the read messages
    :rtype: list
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute(f"SELECT * from READ WHERE receiver = '{name}' ORDER BY time")
    messages = cur.fetchall()
    cur.close()
    connection.close()
    return messages

def clear_msgs(path):
    """Clears all read and unread messages from the tables

    :param path: Path of the messages database
    :type path: str
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute("DELETE FROM UNREAD")
    connection.commit()
    cur.execute("DELETE FROM READ")
    connection.commit()
    cur.close()
    connection.close()
    return