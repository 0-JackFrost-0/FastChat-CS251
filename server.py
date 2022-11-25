import socket
from user_info import *
from groups import *
from time import ctime
import datetime
import sys
import pickle
from msg import *
from messages import *
import bcrypt
import base64

# initializing database path, not required with postgresql
user_info_db_path = "databases/userInfo.db"
group_info_db_path ="databases/groups.db"
messages_db_path = "databases/messages.db"

#signin stuff
if len(sys.argv)==3:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
else:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

# other global variables and constants
BUFSIZE = 4194304
ADDR = (HOST, PORT)
AD = {}
# TODO
LOCAL = '127.0.0.1'
pub_keys = {}
groups = {}

# binding server socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sock.bind(ADDR)

print(f"Listening on {(HOST,PORT)}")
create_user_table(user_info_db_path)
set_all_offline(user_info_db_path)
# clear_msgs(messages_db_path)

def connection_messsage(sender):
    """Connects a user, and sends a message to all users

    :param sender: The username of the joined user
    :type sender: str
    """
    message = f"{sender} has entered the chat "
    change_status_online(sender, user_info_db_path)
    for name, port in get_all_active_ports(user_info_db_path):
        if name != sender:
            package = pickle.dumps(msg('receive', 'server', name,message))
            server_sock.sendto(package, (LOCAL, port))

def normal_message(msgtype,sender,receiver,msg_,grp,data,addr,aes_key):
    """Sends Direct messages to users

    :param msgtype: The type of message to be sent
    :type msgtype: str
    :param sender: The username of the sender of the message
    :type sender: str
    :param receiver: The username of the receiver of the message
    :type receiver: str
    :param msg_: The acutual message to be delivered
    :type msg_: str
    :param grp: The name of the group, which will be None for direct messages
    :type grp: str
    :param data: The binary data received from the client, to pass onto the next
    :type data: binary
    :param addr: contains the tuple of the ip and the port of the client
    :type addr: tuple
    :param aes_key: The encrypted AES key, used to decrypt the data
    :type aes_key: binary
    """
    if check_username(receiver, user_info_db_path):
        if check_username_online(user_info_db_path,receiver):
            # print(msg_)
            server_sock.sendto(data, (LOCAL, get_port(user_info_db_path, receiver)))
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
        
def create_group(sender,grp,addr,aes_key):
    """Creates a new group, and adds members

    :param sender: The username of the sender
    :type sender: str
    :param grp: The name of the group to be formed
    :type grp: str
    :param addr: contains the tuple of the ip and the port of the client
    :type addr: tuple
    :param aes_key: The encrypted AES key, used to decrypt the data
    :type aes_key: binary
    """
    if create_grp_table(group_info_db_path, grp, sender):
        server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'success_created_table', grp)), addr)
        addmem = pickle.loads(server_sock.recv(BUFSIZE))
        while addmem.msg != 'exit':
            if not check_username(addmem.receiver, user_info_db_path):
                message = "user_not_exist"
                package = pickle.dumps(msg('receive', 'server', addmem.receiver,message))
                server_sock.sendto(package,addr)
            elif add_member(group_info_db_path, addmem.group_name, addmem.receiver):
                server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'success', grp)), addr)
                if check_username_online(user_info_db_path,addmem.receiver):
                    message = f"You have been added to the group {addmem.group_name}"
                    package = pickle.dumps(msg('receive', 'server', addmem.receiver,message))
                    server_sock.sendto(package, (LOCAL, get_port(user_info_db_path, addmem.receiver)))
                    insert_to_read_db(messages_db_path,'server',addmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                else:
                    message = f"You have been added to the group {addmem.group_name}"
                    insert_to_unread_db(messages_db_path,'server',addmem.receiver,message,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
            addmem = pickle.loads(server_sock.recv(BUFSIZE))
    else:
        server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'failed_create_table', grp)), addr)

def add_group_mems(sender,grp,addr,aes_key):
    """Add new members to the group, checks if user is admin and adds new members appropriately

    :param sender: The username of the user wanting to add members
    :type sender: str
    :param grp: The name of the group
    :type grp: str
    :param addr: contains the tuple of the ip and the port of the client
    :type addr: tuple
    :param aes_key: The encrypted AES key, used to decrypt the data
    :type aes_key: binary
    """
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

def new_admin(sender,grp,addr,aes_key):
    """Creates a new admin of a group. If the user is an admin, then makes another user admin

    :param sender: The username of the user requesting make_admin
    :type sender: str
    :param grp: The name of the group to add the new admin
    :type grp: str
    :param addr: contains the tuple of the ip and the port of the client
    :type addr: tuple
    :param aes_key: The encrypted AES key, used to decrypt the data
    :type aes_key: bytes
    """
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

def delete_group_(sender,grp,addr,aes_key):
    """Deletes a group, if the user is an admin

    :param sender: The username of user requesting deletion
    :type sender: str
    :param grp: The name of the group to be deleted
    :type grp: str
    :param addr: contains the tuple of the ip and the port of the client
    :type addr: tuple
    :param aes_key: The encrypted AES key, used to decrypt the data
    :type aes_key: bytes
    """
    if check_admin(group_info_db_path, grp, sender):
        server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'group_deleted', grp)), addr)
        members = view_all_members(group_info_db_path, grp)
        drop_table(group_info_db_path, grp)
        for member in members:
            if member[0] != sender:
                if check_username_online(user_info_db_path,member[0]):
                    message_ = f"The group {grp} has been deleted by {sender}"
                    package = pickle.dumps(msg('receive', 'server', member[0],message_))
                    server_sock.sendto(package, (LOCAL, get_port(user_info_db_path,member[0])))
                    insert_to_read_db(messages_db_path,'server',member[0],message_,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
                else:
                    message_ = f"The group {grp} has been deleted by {sender}"
                    insert_to_read_db(messages_db_path,'server',member[0],message_,'receive',datetime.datetime.strptime(ctime(), "%c"),aes_key,grp)
    else:
        server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'failed_deleting_group', grp)), addr)

def kick_users(sender,grp,addr,aes_key):
    """Removes users from a group, if the requesting user is an admin

    :param sender: Username of user requesting a kick
    :type sender: str
    :param grp: The group from which to delete user
    :type grp: str
    :param addr: contains the tuple of the ip and the port of the client
    :type addr: tuple
    :param aes_key: The encrypted AES key, used to decrypt the data
    :type aes_key: bytes
    """
    if check_admin(group_info_db_path, grp, sender):
        server_sock.sendto(pickle.dumps(msg('group', 'server', sender, 'kicked_successfully', grp)), addr)
        stuff = server_sock.recv(BUFSIZE)
        delmem = pickle.loads(stuff)
        if not check_username(delmem.receiver, user_info_db_path):
                message = "user_not_exist"
                package = pickle.dumps(msg('receive', 'server', delmem.receiver,message))
                server_sock.sendto(package,addr)
        elif delete_member(group_info_db_path, grp, delmem.receiver):
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

def normal_group_message(msgtype,sender,receiver,msg_,grp,data,addr,aes_key):
    """Sends a group message to all users

    :param msgtype: The type of message to be sent
    :type msgtype: str
    :param sender: The username of the sender of the message
    :type sender: str
    :param receiver: The username of the receiver of the message
    :type receiver: str
    :param msg_: The acutual message to be delivered
    :type msg_: str
    :param grp: The name of the group
    :type grp: str
    :param data: The binary data received from the client, to pass onto the next
    :type data: binary
    :param addr: contains the tuple of the ip and the port of the client
    :type addr: tuple
    :param aes_key: The encrypted AES key, used to decrypt the data
    :type aes_key: binary
    """
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
        
def disconnect_manager(sender,addr):
    """Manages the disconnection of a client

    :param sender: The username of the disconnecting user
    :type sender: str
    :param addr: contains the tuple of the ip and the port of the disconnecting user
    :type addr: tuple
    """
    if check_username_online(user_info_db_path, sender):
        for name, port in get_all_active_ports(user_info_db_path):
            package = pickle.dumps(msg('disconnect', sender, name,'cancel'))
            server_sock.sendto(package, (LOCAL, port))
        change_status_offline(sender,user_info_db_path)
    else:
        message = f"{sender} does not exist"
        package = pickle.dumps(msg('receive','server', sender,message))
        server_sock.sendto(package, addr)

def register_user(msg_,addr):
    """Registers a new user in the database

    :param msg_: The sign up info of the user
    :type msg_: str
    :param addr: contains the tuple of the ip and the port of the user
    :type addr: tuple
    """
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
        
def login_manager(sender,msg_,addr):
    """Handles login of users

    :param sender: The login username
    :type sender: str
    :param msg_: The login message
    :type msg_: str
    :param addr: contains the tuple of the ip and the port of the login user
    :type addr: tuple
    """
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


def main():
    """Main function of the server, does all the processing and sends/receives messages from clients
    """
    while True:
        try:
            data, addr = server_sock.recvfrom(BUFSIZE)
        except:
            print('a connection closed')
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
            connection_messsage(sender)
        elif msgtype == 'receive':
            normal_message(msgtype,sender,receiver,msg_,grp,data,addr,aes_key)
        elif msgtype == 'group':
            if msg_ == "create":
                create_group(sender,grp,addr,aes_key)           
            elif msg_ == "add":
                add_group_mems(sender,grp,addr,aes_key)
            elif msg_ == "make_admin":
                new_admin(sender,grp,addr,aes_key)
            elif msg_ == "delete":
                delete_group_(sender,grp,addr,aes_key)
            elif msg_ == "kick":
                kick_users(sender,grp,addr,aes_key)
            else:
                normal_group_message(msgtype,sender,receiver,msg_,grp,data,addr,aes_key)
                
        elif msgtype == 'disconnect':
            disconnect_manager(sender,addr)
        elif msgtype == 'register':
            register_user(msg_,addr)
        elif msgtype == 'login':
            login_manager(sender,msg_,addr)
        else:
            normal_message(msgtype,sender,receiver,msg_,grp,data,addr,aes_key)


    server_sock.close()
    
if __name__ == "__main__":
    main()