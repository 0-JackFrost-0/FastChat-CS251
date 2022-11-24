import socket
from user_info import *
from groups import *
from time import ctime, sleep
import datetime
import sys
import pickle
from msg import *
from colorama import init
from termcolor import colored
from messages import *
import bcrypt


# initializing database path, not required with postgresql
user_info_db_path = "databases/userInfo.db"
group_info_db_path ="databases/groups.db"
messages_db_path = "databases/messages.db"

# signin stuff
if len(sys.argv)==3:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
else:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

# other global variables and constants
BUFSIZE = 4194304
ADDR = (HOST, PORT)
LOCAL = '127.0.0.1'

# binding server socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sock.bind(ADDR)

print(f"Listening on {(HOST,PORT)}")
create_user_table(user_info_db_path)
set_all_offline(user_info_db_path)
# clear_msgs(messages_db_path)

while True:
    try:
        data, addr = server_sock.recvfrom(BUFSIZE)
    except:
        print('a connection closed', PORT)
        break

    # to decode the data
    message = pickle.loads(data)
    msgtype = message.type
    sender = message.sender
    receiver = message.receiver
    msg_ = message.msg
    grp = message.group_name
    aes_key = message.aes_key
    if msgtype == 'connect':
            message = f"{sender} has entered the chat "
            change_status_online(sender, user_info_db_path)
            for name, port in get_all_active_ports(user_info_db_path):
                if name != sender:
                    # if check_username_online(user_info_db_path,name):
                        package = pickle.dumps(msg('receive', 'server', name,message))
                        server_sock.sendto(package, (LOCAL, port))
                        # insert_to_read_db(messages_db_path,'server',name,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                    # else:
                        # insert_to_unread_db(messages_db_path,'server',name,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
    elif msgtype == 'receive':
        if check_username(receiver, user_info_db_path):
            if check_username_online(user_info_db_path,receiver):
                # print("Encrypted msg: "+msg_)
                server_sock.sendto(data, ('localhost', get_port(user_info_db_path, receiver)))
                insert_to_read_db(messages_db_path,sender,receiver,msg_,msgtype,datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
            else:
                message = f"{receiver} is offline but message has been stored"
                package = pickle.dumps(msg('receive','server', sender,message))
                server_sock.sendto(package, addr)
                insert_to_unread_db(messages_db_path,sender,receiver,msg_,msgtype,datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
        else:
            message = f"{receiver} does not exist"
            package = pickle.dumps(msg('receive','server', sender,message))
            server_sock.sendto(package, addr)
    elif msgtype == 'group':
        if msg_ == "create":
            if create_grp_table(group_info_db_path, grp, sender):
                server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'success_created_table', grp)), addr)
                addmem = pickle.loads(server_sock.recv(BUFSIZE))
                while addmem.msg != 'exit':
                    if add_member(group_info_db_path, addmem.group_name, addmem.receiver):
                        server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'success', grp)), addr)
                        if check_username_online(user_info_db_path,addmem.receiver):
                            message = f"You have been added to the group {addmem.group_name}"
                            package = pickle.dumps(msg('receive', 'server', addmem.receiver,message))
                            # server_sock.sendto(package, AD[addmem.receiver])
                            server_sock.sendto(package, (LOCAL, get_port(user_info_db_path, addmem.receiver)))
                            insert_to_read_db(messages_db_path,'server',addmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"), aes_key,grp)
                        else:
                            message = f"You have been added to the group {addmem.group_name}"
                            insert_to_unread_db(messages_db_path,'group',addmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                    addmem = pickle.loads(server_sock.recv(BUFSIZE))
            else:
                # print("reading here")
                server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'failed_create_table', grp)), addr)
        elif msg_ == "add":
            if check_admin(group_info_db_path, grp, sender):
                server_sock.sendto(pickle.dumps(msg('group', sender, sender, 'added_successfully', grp)), addr)
                stuff = server_sock.recv(BUFSIZE)
                addmem = pickle.loads(stuff)
                if add_member(group_info_db_path, addmem.group_name, addmem.receiver):
                    server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'success', grp)), addr)
                    if check_username_online(user_info_db_path,addmem.receiver):
                        message = f"You have been added to the group {addmem.group_name}"
                        package = pickle.dumps(msg('receive', 'server', addmem.receiver,message))
                        server_sock.sendto(package, (LOCAL, get_port(user_info_db_path, addmem.receiver)))
                        insert_to_read_db(messages_db_path,'server',addmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                    else:
                        message = f"You have been added to the group {addmem.group_name}"
                        insert_to_unread_db(messages_db_path,'server',addmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                else:
                    server_sock.sendto(pickle.dumps(msg('group', addmem.receiver, sender, 'failed_adding', grp)), addr)
            else:
                server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'not_admin', grp)), addr)
        elif msg_ == "make_admin":
            if check_admin(group_info_db_path, grp, sender):
                server_sock.sendto(pickle.dumps(msg('group', sender, sender, 'made_admin', grp)), addr)
                stuff = server_sock.recv(BUFSIZE)
                addmem = pickle.loads(stuff)
                if make_admin(group_info_db_path, addmem.group_name, addmem.receiver):
                    server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'success', grp)), addr)
                    if check_username_online(user_info_db_path,addmem.receiver):
                        message = f"You have been made admin of the group {addmem.group_name} by {addmem.sender}"
                        package = pickle.dumps(msg('receive', 'server', addmem.receiver,message))
                        server_sock.sendto(package, (LOCAL, get_port(user_info_db_path, addmem.receiver)))
                        insert_to_read_db(messages_db_path,'server',addmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                    else:
                        message = f"You have been made admin of the group {addmem.group_name} by {addmem.sender}"
                        insert_to_unread_db(messages_db_path,'server',addmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                else:
                    server_sock.sendto(pickle.dumps(msg('group', addmem.receiver, sender, 'failed_adding', grp)), addr)
            else:
                server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'not_admin', grp)), addr)          
        elif msg_ == "delete":
            if check_admin(group_info_db_path, grp, sender):
                drop_table(group_info_db_path, grp)
                server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'group_deleted', grp)), addr)
                members = view_all_members(group_info_db_path, grp)
                for member in members:
                    if member[0] != sender:
                        if check_username_online(user_info_db_path,member[0]):
                            message = f"The group {grp} has been deleted by {sender}"
                            package = pickle.dumps(msg('receive', 'server', member[0],message))
                            # server_sock.sendto(package, AD[delmem.receiver])
                            server_sock.sendto(package, (LOCAL, get_port(user_info_db_path,member[0])))
                            insert_to_read_db(messages_db_path,'server',member[0],message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                        else:
                            message = f"The group {grp} has been deleted by {sender}"
                            insert_to_read_db(messages_db_path,'server',member[0],message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
            else:
                server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'failed_deleting_group', grp)), addr)
        elif msg_ == "kick":
            if check_admin(group_info_db_path, grp, sender):
                server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'kicked_successfully', grp)), addr)
                stuff = server_sock.recv(BUFSIZE)
                delmem = pickle.loads(stuff)
                if delete_member(group_info_db_path, grp, delmem.receiver):
                    server_sock.sendto(pickle.dumps(msg('group', delmem.receiver, sender, 'success', grp)), addr)
                    if check_username_online(user_info_db_path,delmem.receiver):
                        message = f"You have been kicked from the group {delmem.group_name} by {delmem.sender}"
                        package = pickle.dumps(msg('receive', 'server', delmem.receiver,message))
                        # server_sock.sendto(package, AD[delmem.receiver])
                        server_sock.sendto(package, (LOCAL, get_port(user_info_db_path, delmem.receiver)))
                        insert_to_read_db(messages_db_path,'server',delmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                    else:
                        message = f"You have been kicked from the group {delmem.group_name} by {delmem.sender}"
                        insert_to_unread_db(messages_db_path,'server',delmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                else:
                    server_sock.sendto(pickle.dumps(msg('group', delmem.receiver, sender, 'failed_kicking', grp)), addr)
            else:
                server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'not_admin', grp)), addr)
        elif msg_ == "make_admin":
            if check_admin(group_info_db_path, grp, sender):
                server_sock.sendto(pickle.dumps(msg('group', sender, sender, 'made_admin', grp)), addr)
                stuff = server_sock.recv(BUFSIZE)
                addmem = pickle.loads(stuff)
                if make_admin(group_info_db_path, addmem.group_name, addmem.receiver):
                    server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'success', grp)), addr)
                    if check_username_online(user_info_db_path,addmem.receiver):
                        message = f"You have been made admin of the group {addmem.group_name} by {addmem.sender}"
                        package = pickle.dumps(msg('receive', 'server', addmem.receiver,message))
                        server_sock.sendto(package, (LOCAL, get_port(user_info_db_path, addmem.receiver)))
                        insert_to_read_db(messages_db_path,'server',addmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                    else:
                        message = f"You have been made admin of the group {addmem.group_name} by {addmem.sender}"
                        insert_to_unread_db(messages_db_path,'server',addmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                else:
                    server_sock.sendto(pickle.dumps(msg('group', addmem.receiver, sender, 'failed_adding', grp)), addr)
        else:
            if check_username(receiver, user_info_db_path):
                if check_username_online(user_info_db_path,receiver):
                    server_sock.sendto(data, ('localhost', get_port(user_info_db_path, receiver)))
                    insert_to_read_db(messages_db_path,sender,receiver,msg_,msgtype,datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                else:
                    message = f"{receiver} is offline but message has been stored"
                    package = pickle.dumps(msg('receive','server', sender,message))
                    server_sock.sendto(package, addr)
                    insert_to_unread_db(messages_db_path,sender,receiver,msg_,msgtype,datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
            else:
                message = f"{receiver} does not exist"
                package = pickle.dumps(msg('receive','server', sender,message))
                server_sock.sendto(package, addr)
    elif msgtype == 'disconnect':
        if check_username_online(user_info_db_path, sender):
            for name, port in get_all_active_ports(user_info_db_path):
                package = pickle.dumps(msg('disconnect', sender, name,'cancel'))
                server_sock.sendto(package, (LOCAL, port))
            change_status_offline(sender,user_info_db_path)
        else:
            message = f"{receiver} does not exist"
            package = pickle.dumps(msg('receive','server', sender,message))
            server_sock.sendto(package, addr)
    elif msgtype == 'register':
        username, password = (msg_).split(' ', 1)
        password = password.encode()
        # Adding the salt to password
        salt = bcrypt.gensalt()
        # Hashing the password
        hashed = bcrypt.hashpw(password, salt)
        pubkey = server_sock.recv(BUFSIZE)
        state = store_new_info(user_info_db_path, username, salt,hashed,'ONLINE', addr[1], pubkey)
        if(state):
            package = pickle.dumps(msg('register', 'server', 'unknown','success'))
            server_sock.sendto(package, addr)
        else:
            package = pickle.dumps(msg('register', 'server', 'unknown','fail'))
            server_sock.sendto(package, addr)
    elif msgtype == 'login':
        username, password = (msg_).split(' ', 1) 
        password = password.encode() 
        state = check_login_info(username, password, user_info_db_path)
        if(state):
            package = pickle.dumps(msg('login', 'server', 'unknown','success'))
            change_status_online(sender, user_info_db_path)
            update_port(user_info_db_path, sender, addr[1])
            server_sock.sendto(package, addr)
        else:
            package = pickle.dumps(msg('login', 'server', 'unknown', 'fail'))
            server_sock.sendto(package, addr)
    else:
        if check_username(receiver, user_info_db_path):
            if check_username_online(user_info_db_path,receiver):
                print(pickle.loads(data).aes_key)
                server_sock.sendto(data, ('localhost', get_port(user_info_db_path, receiver)))
                insert_to_read_db(messages_db_path,sender,receiver,msg_,msgtype,datetime.datetime.strptime(ctime(), "%c"), aes_key,grp)
            else:
                message = f"{receiver} is offline but message has been stored"
                package = pickle.dumps(msg('receive','server', sender,message))
                server_sock.sendto(package, addr)
                insert_to_unread_db(messages_db_path,sender,receiver,msg_,msgtype,datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
        else:
            message = f"{receiver} does not exist"
            package = pickle.dumps(msg('receive','server', sender,message))
            server_sock.sendto(package, addr)

# print("HI")
server_sock.close()
