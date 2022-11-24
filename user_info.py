import sqlite3
import bcrypt

def change_status_online(username,path):
    """This function changes the status of the username in the table users to "ONLINE"

    :param username: The username of the user whose status you want to change
    :type username: string
    :param path: The address of the user_info database
    :type path: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    query = '''UPDATE USERS SET status = 'ONLINE' where username = ? '''
    cur.execute(query,(username,))
    connection.commit()
    cur.close()
    connection.close()

def change_status_offline(username,path):
    """This function changes the status of the username in the table users to "OFFLINE"

    :param username:  The username of the user whose status you want to change
    :type username: string
    :param path: The address of the user_info database
    :type path: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    query = '''UPDATE users SET status = 'OFFLINE' where username = ? '''
    cur.execute(query,(username,))
    connection.commit()
    cur.close()
    connection.close()

def view_all(path):
    """This function prints all the users currently present in the database along with their status


    :param path: The address of the user_info database
    :type path: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute("SELECT username,status from users")
    user_info = cur.fetchall()
    for i in user_info:
        print(f"{i[0]} : {i[1]}")
    cur.close()
    connection.close()

def view_online(path):
    """This function prints all the users currently present in the database whose status is equal to "ONLINE"

    :param path: The address of the user_info database
    :type path: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute("SELECT username from users where status= 'ONLINE'")
    user_info = cur.fetchall()
    for i in user_info:
        print(i[0])
    cur.close()
    connection.close()

def create_user_table(path):
    """Creates the table user if the table is not already present

    :param path: The address of the user_info database
    :type path: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    query = '''CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY,salt TEXT,password TEXT, status TEXT, port INT, pub_key TEXT)'''
    cur.execute(query)
    connection.commit()
    cur.close()
    connection.close()

def insert_to_db(cur,username,salt, password, status, port, pub_key):
    """This function is used to insert data into the table users

    :param cur: The cursor to the connection made with the table users 
    :type cur: sqlite3.cursor
    :param username: The username of the user
    :type username: string
    :param salt: Random text added to the password to make it more secure before encryption 
    :type salt: string
    :param password: The password of the user
    :type password: string
    :param status: "ONLINE" or "OFFLINE" depending upon whether the user is currently active or not
    :type status: string
    :param port: The port of the server to which the user is connected
    :type port: int
    :param pub_key: The RSA public key of the user
    :type pub_key: Returns true if data is successfully inserted else returns false
    :return: _description_
    :rtype: bool
    """

    try:
        query = '''INSERT INTO users VALUES(?,?,?,?,?,?)'''
        cur.execute(query,(username,salt,password,status, port, pub_key))
        print(f"Successfully created user {username}")
        return True
    except:
        print(f"Failed to create user {username}")
        return False

def check_username(username,path):
    """Checks if the user with the given username is present in the database
    :param username: The username of the user
    :type username: string
    :param path: The address of the user_info database
    :type path: string
    :return:Returns true if user is present in the database else returns false
    :rtype: bool
    """
    #check if the username exist
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute("SELECT username from users where username=?",(username,))
    a = cur.fetchall()
    if len(a) != 0:
        return True
    else:
        return False
    # if username in a:
    #     return True
    # else:
    #     return False
    
def store_new_info(path, username, salt,password, status, port, pub_key):
    """This function is used to insert data into the table users after checking if the user with the given username is already present or not

    :param cur: The cursor to the connection made with the table users 
    :type cur: sqlite3.cursor
    :param username: The username of the user
    :type username: string
    :param salt: Random text added to the password to make it more secure before encryption 
    :type salt: string
    :param password: The password of the user
    :type password: string
    :param status: "ONLINE" or "OFFLINE" depending upon whether the user is currently active or not
    :type status: string
    :param port: The port of the server to which the user is connected
    :type port: int
    :param pub_key: The RSA public key of the user
    :type pub_key: Returns true if data is successfully inserted else returns false
    :return: _description_
    :rtype: bool
    """
    #return True if success register
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    if(check_username(username,path)):
        # print("shouldn't be here")
        cur.close()
        connection.commit()
        connection.close()
        return False
    else:
        if insert_to_db(cur,username, salt,password,status, port, pub_key):
            # print("working properly")
            cur.close()
            connection.commit()
            connection.close()
            return True
        else:
            return False

def show_all_user_info(path):
    """Prints all the data stored in the table users

    :param path: The address of the user_info database
    :type path: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute("SELECT * from users")
    user_info = cur.fetchall()
    for i in user_info:
        print(i)
    cur.close()
    connection.close()

def check_login_info(username, password, path):
    """This function is used to authenticate the login info entered by the user

    :param username: The username of the user 
    :type username: string
    :param password: The password entered by the user
    :type password: string
    :param path: The address of the user_info database
    :type path: string
    :return: Returns true if the entered username and password is successfully authenticated else returns false
    :rtype: bool
    """

    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute("select salt from users where username=?",(username,))
    a = cur.fetchall()
    if len(a) == 0:
        return False
    salt = a[0][0]
    hashed = bcrypt.hashpw(password, salt)
    a = cur.execute("select password from users where username=?",(username,))
    a = cur.fetchall()
    if len(a) == 0:
        return False
    passw = a[0][0]
    if passw == hashed:
        return True
    else:
        return False

def get_pubkey(path, username):
    """This function is used to query for the public key of the user with the given username 

    :param path: The address of the user_info database
    :type path: string
    :param username: The username of the user 
    :type username: string
    :return: Returns the public key if found else returns -1 as binary text  
    :rtype: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    try:
        key = cur.execute("SELECT pub_key FROM USERS WHERE username=?", (username,)).fetchall()
        cur.close()
        connection.close()
        # print(key[0][0])
        try:
            return key[0][0]
        except:
            return b"-1"
    except:
        cur.close()
        connection.close()
        return b"-1"

def isPortinTable(path, port):
    """Checks if a given port is present in the tabel

    :return: Returns true if found else false
    :rtype: bool
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    if len(cur.execute("SELECT port FROM USERS WHERE port=?", (port,)).fetchall()) != 0:
        cur.close()
        connection.close()
        return True
    else:
        cur.close()
        connection.close()
        return False

def get_port(path, username):
    """Returns the port to which a given user is connected to

    :return: Returns the port if found else returns -1 as binary text  
    :rtype: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    try:
        key = cur.execute("SELECT port FROM USERS WHERE username=?", (username,)).fetchall()
        cur.close()
        connection.close()
        # print(key[0][0])
        return key[0][0]
    except:
        cur.close()
        connection.close()
        return -1

def get_all_active_ports(path):
    """Returns all ports which are connected to users whose status is "ONLINE"

    :return: Returns the port if found else returns -1 as binary text  
    :rtype: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    out = cur.execute("SELECT username, port FROM USERS WHERE status = 'ONLINE' ").fetchall()
    cur.close()
    connection.close()
    return out

def check_username_online(path, username):
    """Checks if a user with the given username is offline or online

    :return: Returns True if status is "ONLINE else returns False  
    :rtype: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    out = cur.execute("SELECT * FROM USERS WHERE status = 'ONLINE' AND username=?", (username,)).fetchall()
    cur.close()
    connection.close()
    if len(out) != 0:
        return True
    else:
        return False

def check_status(path, username):
    """Returns the status of the user with the given username

    :param path: The address of the user_info database
    :type path: string
    :param username: The username of the user 
    :type username: string
    :return: Returns "ONLINE" or "OFFLINE" depending upon the status
    :rtype: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    out = cur.execute("SELECT status FROM USERS WHERE username=?", (username,)).fetchall()
    cur.close()
    connection.close()
    return out

def update_port(path, username, port):
    """Updates the port to which the user is connected to the given port

    :param path: The address of the user_info database
    :type path: string
    :param username: The username of the user 
    :type username: string
    :param port: The port to which the user is connected
    :type port: int
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute(f"UPDATE USERS SET port = {port} WHERE username=?", (username,))
    connection.commit()
    cur.close()
    connection.close()

def set_all_offline(path):
    """Sets all users' status to "OFFLINE"

    :param path: address of the database
    :type path: string
    """
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute(f"UPDATE USERS SET status = 'OFFLINE'")
    connection.commit()
    cur.close()
    connection.close()