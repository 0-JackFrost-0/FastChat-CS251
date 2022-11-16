import socket, select, string, sys

#Helper function (formatting)
def display() :
	you="\33[33m\33[1m"+" You: "+"\33[0m"
	sys.stdout.write(you)
	sys.stdout.flush()

def main():

    # simulates temp database
    user_info = {
        "jack": "jack",
        "john": "john12",
        "jill": "ligma@69"
    }
    # can also be added in the database
    user_active = {
        "jack": False,
        "john": False,
        "jill": False
    }
    if len(sys.argv)<2:
        host = input("Enter host ip address: ")
    else:
        host = sys.argv[1]

    port = 5001
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    
     # connecting host
    try :
        s.connect((host, port))
    except :
        print("\33[31m\33[1m Can't connect to the server \33[0m")
        sys.exit()
    
    login_option = int(input("\33[34m\33[1m Welcome to Command Line Messenger (CLM): \n 1) New User \n 2) Existing User \33[0m\n \33[36m\33[1m > \33[0m"))
    while True:
        if login_option == 1:
            #asks for user name
            name=input("\33[34m\33[1m CREATING NEW ID:\n Enter username: \33[0m")
            if name in user_info.keys():
                print("\33[31m\33[1m \rUsername already exists, please enter a new name.\n \33[0m")
            else:
                passw = input("\33[34m\33[1m Enter password: \33[0m")
                user_info[name] = passw
                user_active[name] = True
                break

        elif login_option == 2:
            name = input("\33[34m Enter username: \33[0m")
            if name not in user_info.keys():
                print("\33[31m\33[1m \rUsername doesn't exists, please try again.\n \33[0m")
            else:
                passw = input("\33[34m\33[1m Enter password: \33[0m")
                if user_info[name] == passw:
                    user_active[name] = True
                    break
                else:
                    print("\33[31m\33[1m \rIncorrect password entered, please try again.\n \33[0m")
    #if connected
    # s.send(name)
    s.send(name.encode('ascii'))

    display()
    # while True:
    #     msg_option = int(input("\33[34m\33[1m OPTIONS: \n 1) New Chat \n 2) New Group \n 3) Open Chat \n 4) Open Group \n 5) Quit"))

    while True:
        socket_list = [sys.stdin, s]
        
        # Get the list of sockets which are readable
        rList, wList, error_list = select.select(socket_list , [], [])
        
        for sock in rList:
            #incoming message from server
            if sock == s:
                data = sock.recv(4096)
                # print(data)
                if not data :
                    print('\33[31m\33[1m \rDISCONNECTED!!\n \33[0m')
                    user_active[name] = False
                    sys.exit()
                else :
                    ## TODO
                    ## modify stuff in server to only send name, rest will be handled here
                    sys.stdout.write(data.decode('ascii'))
                    if "joined the conversation" in data.decode('ascii'):
                        name = data.decode('ascii').replace("joined the conversation", "").strip()
                        user_info[name] = ""
                    display()
        
            #user entered a message
            else :
                msg=sys.stdin.readline()
                s.send(msg.encode('ascii'))
                to_name = input("\33[34m\33[1m WHOM TO SEND THE MESSAGE:\n Enter username: \33[0m")
                s.send(to_name.encode('ascii'))
                display()

if __name__ == "__main__":
    main()