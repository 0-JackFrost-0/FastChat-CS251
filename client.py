from user_info import change_status_offline, view_all, view_online, get_pubkey
from messages import *
from groups import view_all_members, view_all_groups
import sys, os
import socket
import rsa
from aes import AESEncryptor
import time
from time import ctime
import getpass
import pickle
import threading
from msg import *
from termcolor import colored
import base64
from PIL import Image



# basic variables
buffer = 4194304
username = ""
# path to database
user_info_db_path = "databases/userInfo.db"
group_db_path = "databases/groups.db"
messages_db_path = "databases/messages.db"


if len(sys.argv) == 3:
    host = sys.argv[1]
    port = int(sys.argv[2])
else:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

load_balance_addr = (host, port)

# Connecting to the load balancing server, to get the port to a server
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    welcm_msg = str(port)
    s.sendto(pickle.dumps(welcm_msg), load_balance_addr)
except:
    print(colored("Can't connect to the load balancing server", 'red'))
    sys.exit()

# finding the port of the server, to establish communication
port = int(pickle.loads(s.recv(buffer)))
try:
    pass
except:
    print("\33[31m\33[1m Can't connect to the server \33[0m")
    sys.exit()

# Initialising 
ncryptr = AESEncryptor(os.urandom(16))

def show_message(sender, msg):
    """displays the (individual) message on the screen

    :param sender: name of the sender
    :type sender: str
    :param msg: message to be displayed
    :type msg: str
    """
    if (sender != 'server'):
        pass
    if (sender != 'server'):
        msg = colored("[Direct]", 'cyan')+"-" + \
            colored(f"{sender}", 'green')+": "+msg
    else:
        msg = colored(msg, 'red')
    print(msg)


def show_group_message(grpname, sender, msg):
    """displays the (individual) message on the screen

    :param sender: name of the sender
    :type sender: str
    :param msg: message to be displayed
    :type msg: str
    :param grpname: group in which message needs to be shared
    :type grpname: str
    """
    if (sender != 'server'):
        pass
    if (sender != 'server'):
        msg = colored(f"[{grpname}]", 'cyan')+"-" + colored(f"{sender}", 'green')+": "+msg
    else:
        msg = colored(msg, 'red')
    print(msg)


lock = threading.Lock()
in_thread = False


def change_in_thread():
    """Used to lock one of the threads during execution, avoids the entangling of threads
    """
    global in_thread
    lock.acquire()
    if in_thread:
        in_thread = False
    else:
        in_thread = True
    lock.release()

# Function that receives the messages from the server, and takes appropriate action
def recv_message(private_key):
    """Encrypted messages sent by server are recieved and decrypted and finally displayed on the screen.
    Receives messages of type "receive", "group", "disconnect", "key", "group", "disconnect", "image"
    and "group-image". The type receive is for receiving direct messages, the rest are pretty self explanatory

    :param private_key: key for decryption
    """
    while True:
        msg_, addr = s.recvfrom(buffer)
        if not msg_:
            sys.exit(0)
        if len(msg_) != 0:
            message = pickle.loads(msg_)
            if (message.type == 'receive'):
                if message.sender != 'server':
                    decryptd_key = rsa.decrypt(base64.b64decode(message.aes_key), private_key)
                    decrypted_msg = ncryptr.decrypt(base64.b64decode(message.msg.encode()), decryptd_key)
                    # print(time.time())
                    show_message(message.sender, decrypted_msg.decode())
                else:
                    show_message(message.sender, message.msg)
            elif (message.type == 'key'):
                pass
            elif (message.type == 'disconnect'):
                pass
            elif (message.type == 'image'):
                print(f"Image received from {message.sender}")
                address = "newimage.jpeg"
                decryptd_key = rsa.decrypt(base64.b64decode(message.aes_key), private_key)
                image_str = ncryptr.decrypt(base64.b64decode(message.msg.encode()), decryptd_key)
                decodeit = open(address, 'wb')
                decodeit.write(base64.b64decode((image_str)))
                decodeit.close()
                img = Image.open(address)
                img.show()
            elif (message.type == 'group_image'):
                print(
                    f"Image received from {message.sender} on group {message.group_name}")
                address = "newimage.jpeg"
                decryptd_key = rsa.decrypt(base64.b64decode(message.aes_key), private_key)
                image_str = ncryptr.decrypt(base64.b64decode(message.msg.encode()), decryptd_key)
                decodeit = open(address, 'wb')
                decodeit.write(base64.b64decode((image_str)))
                decodeit.close()
                img = Image.open(address)
                img.show()
            if (message.type == 'group'):
                group_name = message.group_name
                if message.msg == 'admin':
                    pass
                elif message.msg == 'not_admin':
                    print("You do not have admin privileges for this group")
                elif message.msg == 'success_created_table':
                    print(f"Successfully created {group_name}")
                    print("Enter 'exit' when you have finished adding members")
                    while True:
                        member = input("Enter the username of the member: ")
                        if member == "exit":
                            data = pickle.dumps(
                                msg('group', username, member, 'exit', group_name))
                            s.sendto(data, (host, port))
                            break
                        data = pickle.dumps(
                            msg('group', username, member, 'add', group_name))
                        s.sendto(data, (host, port))
                        conf = s.recv(buffer)
                        message = pickle.loads(conf).msg
                        if message == 'success':
                            print(
                                f"{member} has been added to the group {group_name}")
                        elif message == 'user_not_exist':
                            print(colored("The user with this username does not exist",'red'))
                        else:
                            print(f"{member} could not be added to the group")
                    show_admin_commands()
                elif message.msg == 'failed_create_table':
                    print(f"Failed to create {group_name}")
                    # all add msgs
                elif message.msg == 'added_successfully':
                    member = input("Enter name of the member to add: ")
                    data = pickle.dumps(
                        msg('group', username, member, 'add', group_name))
                    s.sendto(data, (host, port))
                    conf = s.recv(buffer)
                    message = pickle.loads(conf).msg
                    if message == 'success':
                        print(
                            f"{member} has been added to the group {group_name}")
                    else:
                        print(f"{member} could not be added {group_name}")
                elif message.msg == 'kicked_successfully':
                    member = input("Enter name of the member to kick: ")
                    data = pickle.dumps(
                        msg('group', username, member, 'kick', group_name))
                    s.sendto(data, (host, port))
                    conf = s.recv(buffer)
                    message = pickle.loads(conf).msg
                    if message == 'success':
                        print(
                            f"{member} has been kicked from the group {group_name}")
                    elif message == 'user_not_exist':
                            print(colored("The user with this username does not exist",'red'))
                    else:
                        print(f"{member} is not present in the group")
                elif message.msg == 'failed_kicking':
                    print(f"Failed to kick {message.sender} from {group_name}")
                elif message.msg == 'group_deleted':
                    print(f"{group_name} has been deleted")
                elif message.msg == 'failed_deleting_group':
                    print(f"Failed to delete {group_name}")
                elif message.msg == 'made_admin':
                    member  = input("Enter name of the member to make admin: ")
                    data = pickle.dumps(msg('group',username,member,'admin',group_name))
                    s.sendto(data, (host, port))
                    conf = s.recv(buffer)
                    message = pickle.loads(conf).msg
                    if message == 'success':
                        print(f"{member} has been added to the group {group_name}")
                    else:
                        print(f"{member} could not be added {group_name}")
                else:
                    if message.sender != 'server':
                        decryptd_key = rsa.decrypt(base64.b64decode(message.aes_key), private_key)
                        decrypted_msg = ncryptr.decrypt(base64.b64decode(message.msg.encode()), decryptd_key)
                        show_group_message(message.group_name, message.sender, decrypted_msg.decode())
                    else:
                        show_group_message(
                            message.group_name, message.sender, message.msg)
                change_in_thread()


# Function to send the message to the given username
def send_message(message):
    """Message given by the user is processed, encrypted and packed and sent to the server.
    There are 4 types of messages that can be made, direct or group messages, and images or text.
    This function takes care of text messages

    :param message: message to be sent
    :type message: string
    """
    grp_or_ind = input("Enter i for individual message and g for group message: ")
    
    if grp_or_ind == "i":
        r_name = input("Whom to send message?: ")
        send_key = get_pubkey(user_info_db_path, r_name)
        if send_key != b"-1":
            public_partner = rsa.PublicKey.load_pkcs1(send_key)
            ###################################
            # print(time.time())
            AESkey = os.urandom(16)
            message = ncryptr.encrypt(message.encode(), AESkey)
            rsa_ncryptd_key = rsa.encrypt(AESkey, public_partner)
            # print(rsa_ncryptd_key)
            ###################################
            package = pickle.dumps(
                msg('receive', username, r_name, base64.b64encode(message).decode(),None, base64.b64encode(rsa_ncryptd_key)))
            s.sendto(package, (host, port))
        else:
            print(f"{r_name} doesn't exist")
    elif grp_or_ind == "g":
        in_grp = False
        grp_name = input("Which group to send message?: ")
        members = view_all_members(group_db_path, grp_name)
        for member in members:
            if member[0] == username:
                in_grp = True
        if in_grp:
            for r_name in members:
                if r_name[0] != username:
                    public_partner = rsa.PublicKey.load_pkcs1(
                        get_pubkey(user_info_db_path, r_name[0]))
                    ###################################
                    AESkey = os.urandom(16)
                    message_ = ncryptr.encrypt(message.encode(), AESkey)
                    rsa_ncryptd_key = rsa.encrypt(AESkey, public_partner)
                    ###################################
                    package = pickle.dumps(
                        msg('group', username, r_name[0], base64.b64encode(message_).decode(), grp_name, base64.b64encode(rsa_ncryptd_key)))
                    s.sendto(package, (host, port))
        else:
            print(colored("You are not a part of this group", 'red'))


def send_image(address):
    """Image given by the user is processed, encrypted and packed and sent to the server, similar to send_message.
    There are 4 types of messages that can be made, direct or group messages, and images or text.
    This function takes care of Images

    :param address: address of the image to be shared
    :type address: string
    """
    try:
        imageFile = open(address,"rb")
    except:
        print(colored("Wrong address entered",'red'))
        return
    image_str = base64.b64encode(imageFile.read())
    grp_or_ind = input(
        "Enter i for individual message and g for group message: ")
    if grp_or_ind == "i":
        r_name = input("Whom to send message?: ")
        # if r_name in pub_keys:
        send_key = get_pubkey(user_info_db_path, r_name)
        if send_key != b"-1":
            public_partner = rsa.PublicKey.load_pkcs1(send_key)
            ###################################
            AESkey = os.urandom(16)
            # message = ncryptr.encrypt(image_str.decode(), AESkey)
            # rsa_ncryptd_key = rsa.encrypt(AESkey, public_partner)
            message = ncryptr.encrypt(image_str, AESkey)
            rsa_ncryptd_key = rsa.encrypt(AESkey, public_partner)
            # print(base64.b64encode(rsa_ncryptd_key))
            ###################################
            package = pickle.dumps(
                msg('image', username, r_name, base64.b64encode(message).decode(), None,base64.b64encode(rsa_ncryptd_key)))
            s.sendto(package, (host, port))
        else:
            print(f"{r_name} doesn't exist")
    elif grp_or_ind == "g":
        grp_name = input("Which group to send message?: ")
        members = view_all_members(group_db_path, grp_name)
        in_grp = False
        for member in members:
            if member[0] == username:
                in_grp = True
        if in_grp:
            for r_name in members:
                if r_name[0] != username:
                    public_partner = rsa.PublicKey.load_pkcs1(
                        get_pubkey(user_info_db_path, r_name[0]))
                    ###################################
                    # print(time.time())
                    AESkey = os.urandom(16)
                    message_ = ncryptr.encrypt(image_str, AESkey)
                    rsa_ncryptd_key = rsa.encrypt(AESkey, public_partner)
                    # print(rsa_ncryptd_key)
                    ###################################
                    package = pickle.dumps(
                        msg('group_image', username, r_name[0], base64.b64encode(message_).decode(), grp_name, base64.b64encode(rsa_ncryptd_key)))
                    s.sendto(package, (host, port))


def login():
    """Function to verify login
    """
    global username
    print("1 - LOGIN")
    print("2 - SIGNUP")
    opt = int(input(">>> "))
    while True:
        if (opt == 1):
            username = input("Username: ")
            password = getpass.getpass()
            message = username+" "+password
            data = pickle.dumps(msg('login', username, 'server', message))
            s.sendto(data, (host, port))
            conf = s.recv(buffer)
            message = pickle.loads(conf).msg
            if message == 'success':
                print(f"Welcome back {username}")
                return opt
            else:
                print("Invalid login, please try again")
        elif (opt == 2):
            username = input("Username: ")
            password = getpass.getpass()
            message = username+" "+password
            data = pickle.dumps(msg('register', username, 'server', message))
            s.sendto(data, (host, port))
            public_key, private_key = rsa.newkeys(1024)
            mesg1 = public_key.save_pkcs1("PEM")
            priv_key = private_key.save_pkcs1("PEM")
            addr = f"{username}_priv.txt"
            file = open(addr, 'wb')
            file.write(priv_key)
            s.sendto(mesg1, (host, port))
            conf = s.recv(buffer)
            message = pickle.loads(conf).msg
            if message == 'success':
                print(f"You have successfully registered")
                return opt
            else:
                print("Username already taken. Try another username")


def show_welcome_message():
    """The Welcome Message is displayed on the screen
    """
    print(colored("Welcome to Command Line Messenger (CLM)", 'cyan'))
    print(colored("Some common commands that you can run are:", 'cyan'))
    print(colored("1) \\quit: To quit the messenger", 'green'))
    print(colored("2) \\online - view all users that are currently online", 'green'))
    print(colored("3) \\all - view all users of CLM", 'green'))
    print(colored("4) \\groups - view all groups that you are currently a part of", 'green'))
    print(colored("5) \\create - create a new group", 'green'))
    print(colored("6) \\image - send images", 'green'))
    print(colored("7) \\read - displays upto last 10 read messages", 'green'))
    print(colored("8) \\unread - displays upto last 10 unread messages", 'green'))
    return


def show_admin_commands():
    """Group commands are shared to the user creating the group
    """
    print(colored("The commands available to the admin are:", 'cyan'))
    print(colored("- \\add - Add a new user to the group", 'cyan'))
    print(colored("- \\kick - Remove a user from a group", 'cyan'))
    print(colored("- \\delgrp - Deletes the group", 'cyan'))
    print(colored("- \\make_admin - To make another member an admin", 'cyan'))
    return


def get_privkey(username):
    """Retrieves the private key which is stored locally on the user's device

    :param username: The username whose private key is to be retrieved
    :type username: str
    :return: The private key of the username
    :rtype: bytes
    """
    address = f"{username}_priv.txt"
    file = open(address, 'rb')
    priv_key = file.read()
    return priv_key


# Main function, runs the whole Command Line GUI thingy, will decompose code further
def main():
    """This is executed for the functioning on the client side.
    All the processes required are run by this.
    First it takes the login, then does whatever is asked by the user accordingly.
    """
    login()
    show_welcome_message()
    public_key = rsa.PublicKey.load_pkcs1(
        get_pubkey(user_info_db_path, username))
    private_key = rsa.PrivateKey.load_pkcs1(get_privkey(username))
    message = public_key.save_pkcs1("PEM").decode()
    data = pickle.dumps(msg('connect', username, 'server', message))
    s.sendto(data, (host, port))
    receive_thread = threading.Thread(target=recv_message, args=(private_key,))
    receive_thread.start()
    while True:
        if in_thread:
            continue
        chat = input()
        if (len(chat) == 0):
            continue
        if (chat[0] == '\\'):
            if (chat == "\\quit"):
                data = pickle.dumps(
                    msg('disconnect', username, 'server', 'cancel'))
                s.sendto(data, (host, port))
                s.connect((host, port))
                s.shutdown(socket.SHUT_RDWR)
                receive_thread.join()
                sys.exit()
            if (chat == "\\online"):
                print(f"Online Users are:")
                lines = view_online(user_info_db_path)
            elif (chat == "\\all"):
                view_all(user_info_db_path)
            elif (chat == "\\groups"):
                print(f"Existing groups are:")
                lines = view_all_groups(group_db_path, username)
            elif (chat == '\\image'):
                address = input("Enter the address of the image: ")
                send_image(address)
            elif chat == "\\read":
                msg_list = return_all_read_messages(messages_db_path, username)
                if len(msg_list) == 0:
                    print("No read messages")
                else:
                    print(f"Last {len(msg_list)} read messages:")
                for row in msg_list:
                    if row[3] == 'group':
                        if row[0] != 'server':
                            decryptd_key = rsa.decrypt(base64.b64decode(row[5]), private_key)
                            decrypted_msg = ncryptr.decrypt(base64.b64decode(row[2].encode()), decryptd_key)
                            show_group_message(row[6], row[0], decrypted_msg.decode())
                        else:
                            show_group_message(row[6], row[0], row[2])
                    elif row[3] == 'receive':
                        if row[0] != 'server':
                            decryptd_key = rsa.decrypt(base64.b64decode(row[5]), private_key)
                            decrypted_msg = ncryptr.decrypt(base64.b64decode(row[2].encode()), decryptd_key)
                            show_message(row[0], decrypted_msg.decode())
                        else:
                            show_message(row[0], row[2])
                    elif row[3] == 'image':
                        print(f"Image received from {row[0]}")
                        address = "newimage.jpeg"
                        decryptd_key = rsa.decrypt(base64.b64decode(row[5]), private_key)
                        image_str = ncryptr.decrypt(base64.b64decode(row[2]), decryptd_key)
                        decodeit = open(address, 'wb')
                        decodeit.write(base64.b64decode((image_str)))
                        decodeit.close()
                        img = Image.open(address)
                        img.show()
                    elif row[3] == 'group_image':
                        print(
                            f"Image received from {row[0]} on group {row[6]}")
                        address = "newimage.jpeg"
                        decryptd_key = rsa.decrypt(base64.b64decode(row[5]), private_key)
                        image_str = ncryptr.decrypt(base64.b64decode(row[2]), decryptd_key)
                        decodeit = open(address, 'wb')
                        decodeit.write(base64.b64decode((image_str)))
                        decodeit.close()
                        img = Image.open(address)
                        img.show()
                    else:
                        if row[0] != 'server':
                            decryptd_key = rsa.decrypt(base64.b64decode(row[5]), private_key)
                            decrypted_msg = ncryptr.decrypt(base64.b64decode(row[2].encode()), decryptd_key)
                            show_message(row[0], decrypted_msg.decode())
                        else:
                            show_message(row[0], row[2])
            elif chat == "\\unread":
                msg_list = return_all_unread_messages(
                    messages_db_path, username)
                if len(msg_list) == 0:
                    print("No unread messages")
                else:
                    print(f"Last {len(msg_list)} read messages:")
                for row in msg_list:
                    if row[3] == 'group':
                        if row[0] != 'server':
                            decryptd_key = rsa.decrypt(base64.b64decode(row[5]), private_key)
                            decrypted_msg = ncryptr.decrypt(base64.b64decode(row[2].encode()), decryptd_key)
                            show_group_message(row[6], row[0], decrypted_msg.decode())
                        else:
                            show_group_message(row[6], row[0], row[2])
                    elif row[3] == 'receive':
                        if row[0] != 'server':
                            decryptd_key = rsa.decrypt(base64.b64decode(row[5]), private_key)
                            decrypted_msg = ncryptr.decrypt(base64.b64decode(row[2].encode()), decryptd_key)
                            show_message(row[0], decrypted_msg.decode())
                        else:
                            show_message(row[0], row[2])
                    elif row[3] == 'image':
                        print(f"Image received from {row[0]}")
                        address = "newimage.jpeg"
                        decryptd_key = rsa.decrypt(base64.b64decode(row[5]), private_key)
                        image_str = ncryptr.decrypt(base64.b64decode(row[2]), decryptd_key)
                        decodeit = open(address, 'wb')
                        decodeit.write(base64.b64decode((image_str)))
                        decodeit.close()
                        img = Image.open(address)
                        img.show()
                    elif row[3] == 'group_image':
                        print(f"Image received from {row[0]} on group {row[5]}")
                        address = "newimage.jpeg"
                        decryptd_key = rsa.decrypt(base64.b64decode(row[5]), private_key)
                        image_str = ncryptr.decrypt(base64.b64decode(row[2]), decryptd_key)
                        decodeit = open(address, 'wb')
                        decodeit.write(base64.b64decode((image_str)))
                        decodeit.close()
                        img = Image.open(address)
                        img.show()
                    else:
                        if row[0] != 'server':
                            decryptd_key = rsa.decrypt(base64.b64decode(row[5]), private_key)
                            decrypted_msg = ncryptr.decrypt(base64.b64decode(row[2].encode()), decryptd_key)
                            show_message(row[0], decrypted_msg.decode())
                        else:
                            show_message(row[0], row[2])
                    insert_to_read_db_silent(messages_db_path,row[0],row[1],row[2],row[3],row[4],row[5],row[6])
            elif (chat == "\\kick"):
                grp = input("Enter name of the group: ")
                data = pickle.dumps(msg('group', username, 'server', 'kick', grp))
                s.sendto(data, (host, port))
                change_in_thread()
            elif (chat == "\\add"):
                grp = input("Enter name of the group: ")
                data = pickle.dumps(msg('group', username, 'server', 'add', grp))
                s.sendto(data, (host, port))
                change_in_thread()
            elif (chat == "\\delgrp"):
                grp = input("Enter name of the group: ")
                data = pickle.dumps(msg('group', username, 'server', 'delete', grp))
                s.sendto(data, (host, port))
                change_in_thread()
            elif (chat == "\\create"):
                grp = input("Enter name of the group: ")
                data = pickle.dumps(msg('group', username, 'server', 'create', grp))
                s.sendto(data, (host, port))
                change_in_thread()
            elif (chat == "\\make_admin"):
                grp = input("Enter name of the group: ")
                data = pickle.dumps(msg('group', username, 'server', 'make_admin', grp))
                s.sendto(data, (host, port))
                change_in_thread()
            else:
                print(colored("INVALID COMMAND", 'red'))
        else:
            chat = f"{chat} " + colored(ctime(), 'blue')
            send_message(chat)


if __name__ == "__main__":
    try:
        main()
    except:
        change_status_offline(username, user_info_db_path)
