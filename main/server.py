import socket
from data import *
from time import ctime, sleep
import sys
import pickle
from msg import *

# initializing database path, not required with postgresql
DBPATH = 'databases/userInfo.db'

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
# why storing pub_keys both on server and client side?
pub_keys = {}
received = b""

# binding server socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_sock.bind(ADDR)

print(f"Listening on {(HOST,PORT)}")
# TODO
# will have to be changed, if multiple servers are being implemented
###################
create_table(DBPATH)
###################

while True:
    print('waiting for message...')
    try:
        data, addr = server_sock.recvfrom(BUFSIZE)
    except:
        print('a connection closed')
        break
        # continue

    # to decode the data
    message = pickle.loads(data)
    msgtype = message.type
    sender = message.sender
    receiver = message.receiver
    length = message.length
    msg_ = message.msg
    # print(msg_)
    # print(msgtype)
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
            message = f'{sender} comes in\n'
            for name, addr in AD.items(): 
                package = pickle.dumps(msg('receive', 'server', name,message))
                server_sock.sendto(package, addr)
    elif msgtype == 'receive':
        # print(AD[receiver])
        server_sock.sendto(data, AD[receiver])
    elif msgtype == 'disconnect':
        AD.pop(sender)
        pub_keys.pop(sender)
        for name, addr in AD.items():
            package = pickle.dumps(msg('disconnect', sender, name,'cancel'))
            server_sock.sendto(package, addr)
    elif msgtype == 'register':
        username, password = (msg_).split(' ', 1)
        state = store_new_info(username, password,'ONLINE', DBPATH)
        if(state):
            package = pickle.dumps(msg('register', 'server', 'unknown','success'))
            server_sock.sendto(package, addr)
        else:
            package = pickle.dumps(msg('register', 'server', 'unknown','fail'))
            server_sock.sendto(package, addr)
    elif msgtype == 'login':
        username, password = (msg_).split(' ', 1)    
        state = check_login_info(username, password, DBPATH)
        if(state):
            package = pickle.dumps(msg('login', 'server', 'unknown','success'))
            server_sock.sendto(package, addr)
        else:
            package = pickle.dumps(msg('login', 'server', 'unknown', 'fail'))
            server_sock.sendto(package, addr)
    print(AD)
    #print(pub_keys)

server_sock.close()