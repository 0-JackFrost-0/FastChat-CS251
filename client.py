from user_info import *
import sys
import socket, select
import rsa
import datetime
from time import ctime
import getpass
import pickle
import threading
from msg import *
from colorama import init
from termcolor import colored

# datetime.datetime.strptime(time.ctime(), "%c")

# basic variables
buffer = 4096

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
    print(colored("Can't connect to the server",'red'))
    sys.exit()

# Function that decrypts the message from the user, and prints it out
def show_message(sender, msg):
    # print('msg receive')
    if(sender != 'server'):
        pass
    if msg[-1] != '\n':
        msg = msg+ " " +colored(ctime(),'blue')
    else:
        msg = msg + ctime()
    if(sender != 'server'):
        msg = colored(f"{sender}: ",'green')+msg
    else:
        msg = colored(msg,'red')  
    print(msg)

# Function that recieves the message from the server
def recv_message(private_key):
    while not stop_recieve_thread:
        msg = s.recv(buffer)
        if not msg:
            sys.exit(0)
            # return
        if len(msg) != 0:
            message = pickle.loads(msg)
            if(message.type == 'receive'):
                if message.sender != 'server':
                    decrypted_msg = rsa.decrypt(message.msg,private_key).decode()
                    show_message(message.sender,decrypted_msg)
                else:
                    show_message(message.sender,message.msg)
            elif(message.type == 'key'):
                public_partner_key = message.msg
                pub_keys[message.sender] = public_partner_key
            elif(message.type == 'group'):
                pass
            elif(message.type == 'disconnect'):
                pub_keys.pop(message.sender)
    print("receive stopped")
# Function to send the message to the given username
def send_message(message):
        r_name = input("Whom to send message?: ")
        if r_name in pub_keys:
            public_partner = rsa.PublicKey.load_pkcs1(pub_keys[r_name])
            message = rsa.encrypt(message.encode(),public_partner)
            package = pickle.dumps(msg('receive', username, r_name, message))
            s.send(package)
        else:
            print(f"{r_name} is offline")

def send_group_message(message):
        r_name = input("Whom to send message?: ")
        if r_name in pub_keys:
            public_partner = rsa.PublicKey.load_pkcs1(pub_keys[r_name])
            message = rsa.encrypt(message.encode(),public_partner)
            package = pickle.dumps(msg('receive', username, r_name, message))
            s.send(package)
        else:
            print(f"{r_name} is offline")

def login():
    global username
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
    global stop_recieve_thread
    stop_recieve_thread = False
    opt = login()
    public_key,private_key = rsa.newkeys(1024)
    pub_keys[username] = public_key.save_pkcs1("PEM")
    message = public_key.save_pkcs1("PEM")
    data = pickle.dumps(msg('connect',username,'server',message))
    s.send(data)
    recieve_thread = threading.Thread(target=recv_message,args=(private_key,))
    recieve_thread.start()
    while True:
        chat = input()
        if(chat[0] == '/'):
            # if(chat == "/quit"):
            #     data = pickle.dumps(msg('disconnect',username,'server','cancel'))
            #     s.send(data)
            #     stop_recieve_thread = True
            #     break
            pass
        else:
            send_message(chat)



if __name__ == "__main__":
    main()