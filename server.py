import socket
from user_info import *
from time import ctime, sleep
import sys
import pickle
from msg import *
from colorama import init
from termcolor import colored
from unsent import *
import bcrypt

# initializing database path, not required with postgresql
user_info_db_path = "databases/userInfo.db"

# signin stuff
if len(sys.argv)==3:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
else:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

# other global variables and constants
BUFSIZE = 4096
ADDR = (HOST, PORT)
AD = {}
# TODO

pub_keys = {}
groups = {}
received = b""

# binding server socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sock.bind(ADDR)

print(f"Listening on {(HOST,PORT)}")
# TODO
# will have to be changed, if multiple servers are being implemented
###################
create_table(user_info_db_path)
###################

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
    length = message.length
    msg_ = message.msg
    if msgtype == 'connect':
        if addr not in AD.values():
            pub_keys[sender] = msg_
            for name, address in AD.items():
                package = pickle.dumps(msg('key', sender, name,msg_))
                server_sock.sendto(package, address)
            AD[sender] = addr
            for name, pubkey in pub_keys.items():
                if name == sender:
                    continue
                package = pickle.dumps(msg('key', name, sender,pubkey))
                server_sock.sendto(package, addr)
            message = f"{sender} has entered the chat "
            for name, address in AD.items():
                if name != sender: 
                    package = pickle.dumps(msg('receive', 'server', name,message))
                    server_sock.sendto(package, address)
    elif msgtype == 'receive':
        if(receiver in AD):
            server_sock.sendto(data, AD[receiver])
        else:
            message = f"{receiver} does not exist"
            package = pickle.dumps(msg('recieve','server', sender,message))
            server_sock.sendto(package, addr)
    # elif msgtype == 'group':
    #     print(msg_)
    #     for r_name,addr in 
    #     else:
    #         message = f"{receiver} does not exist"
    #         package = pickle.dumps(msg('recieve','server', sender,message))
    #         server_sock.sendto(package, addr)
    elif msgtype == 'disconnect':
        if(sender in AD):
            AD.pop(sender)
            pub_keys.pop(sender)
            for name, addr in AD.items():
                package = pickle.dumps(msg('disconnect', sender, name,'cancel'))
                server_sock.sendto(package, addr)
        else:
            message = f"{receiver} does not exist"
            package = pickle.dumps(msg('recieve','server', sender,message))
            server_sock.sendto(package, addr)
    elif msgtype == 'register':
        username, password = (msg_).split(' ', 1)
        password = password.encode()
        # Adding the salt to password
        salt = bcrypt.gensalt()
        # Hashing the password
        hashed = bcrypt.hashpw(password, salt)  
        state = store_new_info(username, salt,hashed,'ONLINE', user_info_db_path)
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
            server_sock.sendto(package, addr)
        else:
            package = pickle.dumps(msg('login', 'server', 'unknown', 'fail'))
            server_sock.sendto(package, addr)
server_sock.close()