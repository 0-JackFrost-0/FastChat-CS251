import sys
import socket
import random
from itertools import cycle
import pickle
from messages import *
# from server import start_server
import subprocess, os, signal
import threading

messages_db_path = "databases/messages.db"
create_read_table(messages_db_path)
create_unread_table(messages_db_path)

# SERVER_POOL = [('localhost', 5000), ('localhost', 5001)]
server_command = ""
# servers = list()

def start_server(command):
    global servers
    servers = subprocess.Popen(command, shell=True)
    return

class LoadBalancer(object):
    # Change docstring lmao, this isn't correct
    """ Socket implementation of a load balancer.
    Flow Diagram:
    +---------------+      +-----------------------------------------+      +---------------+
    | client socket | <==> | client-side socket | server-side socket | <==> | server socket |
    |   <client>    |      |          < load balancer >              |      |    <server>   |
    +---------------+      +-----------------------------------------+      +---------------+
    Attributes:
        ip (str): virtual server's ip; client-side socket's ip
        port (int): virtual server's port; client-side socket's port
        algorithm (str): algorithm used to select a server
        sockets (list): current connected and open socket obj
    """


    def __init__(self, ip, port, num_servers, algorithm='random'):
        global server_command
        self.ip = ip
        self.port = port
        self.algorithm = algorithm
        
        self.server_pool = list()

        for i in range(num_servers):
            self.server_pool.append(('localhost', 5000+i))
            try:
                server_command += f"python3 server.py 'localhost' {5000+i} & "
                # start_server('server.py', 5000+i)
                # start_server('server.py', 5000+i)
                # print(f"server at port {5000+i} started")
            except Exception as e:
                print(e)

        start_server(server_command)
        self.iter = cycle(self.server_pool)
        # init a client-side socket
        self.cs_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.cs_socket.bind((self.ip, self.port))
        print ('init client-side socket: %s' % (self.cs_socket.getsockname(),))

    def start(self):
        while True:
            try:
                data, addr = self.cs_socket.recvfrom(4026)
            except:
                print('a connection closed')
                servers.terminate()
                subprocess.check_call(f"./kill_server.sh {num_servers}", shell=True)
                break
            # to decode the data
            # message = int(pickle.loads(data))
            self.on_accept(addr)

    def on_accept(self, cport):
        server_ip, server_port = self.select_server(self.server_pool, self.algorithm)
        print("sending port", cport)
        self.cs_socket.sendto(pickle.dumps(str(server_port)), cport)
    
    def round_robin(self, iter):
        # round_robin([A, B, C, D]) --> A B C D A B C D A B C D ...
        return next(iter)

    def select_server(self, server_list, algorithm):
        if algorithm == 'random':
            return random.choice(server_list)
        elif algorithm == 'round robin':
            return self.round_robin(self.iter)
        else:
            raise Exception('unknown algorithm: %s' % algorithm)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        num_servers = int(sys.argv[1])
        port = int(sys.argv[2])
    else:
        print(f"Usage: {sys.argv[0]} <num_servers> <port>")
        sys.exit(1)
    try:
        LoadBalancer('localhost', port,  num_servers,'random').start()
    except KeyboardInterrupt:
        print("Exiting Load Balancer")
        sys.exit(1)
