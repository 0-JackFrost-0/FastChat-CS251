from data import *
import sys
import socket, select
import rsa
from time import ctime
import getpass
import pickle
import threading
from msg import *

# basic variables
buffer = 4096
db_path = "databases/userInfo.db"
pub_keys={}
username = ""

# utilising command line arguments, throws error if not passed correctly.
if len(sys.argv)==3:
    host = sys.argv[1]
    port = int(sys.argv[2])
else:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

addr = (host,port)

# initialising the socket, throws error if not connected
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try :
    s.connect(addr)
except :
    print("\33[31m\33[1m Can't connect to the server \33[0m")
    sys.exit()

#Helper function (formatting)
def display() :
    you="\33[33m\33[1m"+" You: "+"\33[0m"
    sys.stdout.write(you)
    sys.stdout.flush()
    # print(you)

# Function that decrypts the message from the user, and prints it out
def show_message(sender, msg):
    # print('msg receive')
    if(sender != 'server'):
        pass
        # msg = rsa.decrypt(msg, priv)
    msg = msg+ " " +ctime()
    if(sender != 'server'):
        msg = sender+": "+msg   
    print(msg)

# Function that recieves the message from the server
def recv_message():
    while True:
        msg = s.recv(buffer)
        if not msg:
            sys.exit(0)
            # return
        if len(msg) != 0:
            message = pickle.loads(msg)
            print(message.type)
            if(message.type == 'receive'):
                print(message.sender)
                show_message(message.sender,message.msg)
            elif(message.type == 'key'):
                public_partner_key = message.msg
                pub_keys[message.sender] = public_partner_key
            elif(message.type == 'group'):
                pass
            elif(message.type == 'disconnect'):
                pub_keys.pop(message.sender)

# Function to send the message to the given username
def send_message():
    while True:
        message = input("Enter: ")
        r_name = input("Whom to send message?: ")
        # for r_name in pub_keys.keys():
            # print("halo")
        package = pickle.dumps(msg('receive', username, r_name, message))
        s.send(package)

def login():
    global username
    print(pub_keys)
    print("1 - LOGIN")
    print("2 - NEW USER")
    opt = int(input(">>> "))
    while True:
        if(opt == 1):
            username = input("Username: ")
            password = getpass.getpass()
            message = username+" "+password
            data = pickle.dumps(msg('login',username,'server',message))
            s.send(data)
            conf = s.recv(buffer)
            message = pickle.loads(conf).msg
            if message == 'success':
                print(f"Welcome back {username}")
                return opt
            else:
                print("Invalid login, please try again")
        elif(opt == 2):
            username = input("Username: ")
            password = getpass.getpass()
            message = username+" "+password
            data = pickle.dumps(msg('register',username,'server',message))
            s.send(data)
            conf = s.recv(buffer)
            message = pickle.loads(conf).msg
            if message == 'success':
                print(f"You have successfully registered")
                return opt
            else:
                print("Username already taken. Try another username")

# Main function, runs the whole Command Line GUI thingy, will decompose code further
def main():
    opt = login()
    public_key,private_key = rsa.newkeys(1024)
    # pub_keys[username] = public_key
    message = public_key.save_pkcs1("PEM").decode()
    data = pickle.dumps(msg('connect',username,'server',message))
    s.send(data)
    recieve_thread = threading.Thread(target=recv_message)
    recieve_thread.start()
    send_thread = threading.Thread(target=send_message)
    send_thread.start()

    # uname = input("who to send message? >> ")
    # send_message(uname)
    # display()
    # while True:
    #     socket_list = [sys.stdin, s]
        
    #     # Get the list of sockets which are readable
    #     rList, wList, error_list = select.select(socket_list , [], [])
        
    #     for sock in rList:
    #         #incoming message from server
    #         if sock == s:
    #             print('dafuq')
    #             recv_message()
    #             # data = sock.recv(buffer)
    #             # if not data :
    #             #     print('\33[31m\33[1m \rDISCONNECTED!!\n \33[0m')
    #             #     # TODO
    #             #     # call change status offline at the backend
    #             #     sys.exit()
    #             # else :
    #             #     ## TODO
    #             #     ## modify stuff in server to only send name, rest will be handled here
    #             #     sys.stdout.write(data.decode('ascii'))
    #             #     if "joined the conversation" in data.decode('ascii'):
    #             #         name = data.decode('ascii').replace("joined the conversation", "").strip()
    #             #         # user_info[name] = ""
    #             display()
    #         #user entered a message
    #         else :
    #             mesg=sys.stdin.readline()
    #             # s.send(mesg.encode('ascii'))
    #             to_name = input("\33[34m\33[1m WHOM TO SEND THE MESSAGE:\n Enter username: \33[0m")
    #             # s.send(to_name.encode('ascii'))
    #             send_message(to_name, mesg)
    #             display()
    # while opt != 6:
    #     print("1 - VIEW ALL")
    #     print("2 - VIEW ONLINE")
    #     print("3 - VIEW GROUPS")
    #     print("4 - ENTER DIRECT MESSAGE")
    #     print("5 - ENTER GROUP")
    #     print("6 - Quit")
    #     opt = int(input(">>> "))
    #     if(opt == 1):
    #         view_all(db_path)
    #     elif(opt == 2):
    #         view_online(db_path)
    #     elif(opt == 3):
    #         pass
    #     elif(opt == 4):
    #         to_name = input("Whom do you want to chat to: ")
    #         ins=input(">>> ")
    #         s.send(ins.encode('ascii'))
    #         while True:
    #             socket_list = [sys.stdin, s]
    #             # Get the list of sockets which are readable
    #             rList, wList, error_list = select.select(socket_list , [], [])
    #             for sock in rList:
    #                 #incoming message from server
    #                 if sock == s:
    #                     data = sock.recv(4096)
    #                     # print(data)
    #                     if not data :
    #                         print('\33[31m\33[1m \rDISCONNECTED!!\n \33[0m')
    #                         sys.exit()
    #                     else :
    #                         sys.stdout.write(data.decode('ascii'))
    #                 #user entered a message
    #                 else :
    #                     print("Hello Wordl")
    #                     # inp = sys.stdline.readline()
    #                     # s.send(inp.encode('ascii'))
    #                     # s.send(to_name.encode('ascii'))
    #     elif(opt == 5):
    #         group = input("Which group chat do you want to enter: ")
    #         if(group.capitalize().strip() == "ALL"):
    #             pass
    #     else:
    #         break
        
    
    change_status_offline(username,db_path)


if __name__ == "__main__":
    main()