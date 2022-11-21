import sqlite3


def create_grp_table(grpname,path):
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    query = '''CREATE TABLE IF NOT EXISTS ?(members TEXT PRIMARY KEY,admin INT)'''
    cur.execute(query,(grpname,))
    connection.commit()
    cur.close()
    connection.close()

def view_all_members(grpname,path):
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute(f"SELECT members from {grpname}")
    user_info = cur.fetchall()
    for i in user_info:
        print(f"{i[0]}")
    cur.close()
    connection.close()

def insert_to_grp_db(path,grpname,username,isadmin):
    try:
        connection = sqlite3.connect(path)
        cur = connection.cursor()
        query = '''INSERT INTO users VALUES(?,?,?)'''
        cur.execute(query,(username,password,status))
        print(f"Successfully created user {username}")
        return True
    except:
        print(f"Failed to create user {username}")
        return False

def check_username(username,path):
    #check if the username exist
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute("SELECT username from users")
    a = cur.fetchall()
    if username in a:
        return True
    else:
        return False
    
def store_new_info(username, password, status,path):
    #return True if success register
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    if(check_username(username,path)):
        cur.close()
        connection.commit()
        connection.close()
        return False
    else:
        if insert_to_db(cur,username, password,status):
            cur.close()
            connection.commit()
            connection.close()
            return True
        else:
            return False

def show_all_user_info(path):
    connection = sqlite3.connect(path)
    cur = connection.cursor()
    cur.execute("SELECT * from users")
    user_info = cur.fetchall()
    for i in user_info:
        print(i)
    cur.close()
    connection.close()


    