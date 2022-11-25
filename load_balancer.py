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
    """Subprocess used to start the servers

    :param command: The python command to run all the servers
    :type command: str
    """
    global servers
    servers = subprocess.Popen(command, shell=True)
    return

class LoadBalancer(object):
    # Change docstring lmao, this isn't correct
    """ Socket implementation of a load balancer. For the first time, the client connects to the load balancer. The load balancer assigns
        a server to the client, and from then on the client directly communicates with the server
    """
        # Flow Diagram:
        # +---------------+      +-----------------------------------------+      +---------------+
        # | client socket | <==> | client-side socket | server-side socket | <==> | server socket |
        # |   <client>    |      |          < load balancer >              |      |    <server>   |
        # +---------------+      +-----------------------------------------+      +---------------+
        #         ^                                                                        ^
        #         |                                                                        |
        #         |                                                                        |
        #         \\_______________________________________________________________________/

    def __init__(self, ip, port, num_servers, algorithm='random'):
        """Constructor for the load balancer

        :param ip: The ip on which the load balancer is run
        :type ip: str
        :param port: The port on which the load balancer is run
        :type port: int
        :param num_servers: The number of servers to run
        :type num_servers: int
        :param algorithm: The load balancing strategy to use, defaults to 'random'
        :type algorithm: str, optional
        """
        global server_command
        self.ip = ip
        self.port = port
        self.algorithm = algorithm
        
        self.server_pool = list()

        for i in range(num_servers):
            self.server_pool.append(('localhost', 5000+i))
            try:
                server_command += f"python3 server.py 'localhost' {5000+i} & "
            except Exception as e:
                print(e)

        start_server(server_command)
        self.iter = cycle(self.server_pool)
        # init a client-side socket
        self.cs_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.cs_socket.bind((self.ip, self.port))
        print ('init client-side socket: %s' % (self.cs_socket.getsockname(),))

    def start(self):
        """Upon starting the load balancer, it will find the address of the client, and send it to the accept function
        """
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
        """The function provides the client and the server ports of each other to establish communication

        :param cport: port of the client
        :type cport: int
        """
        server_ip, server_port = self.select_server(self.server_pool, self.algorithm)
        print("sending port", cport)
        self.cs_socket.sendto(pickle.dumps(str(server_port)), cport)
    
    def round_robin(self, iter):
        """A load balancing strategy, which selects the servers in an order
        For eg:
        round_robin([A, B, C, D]) --> A B C D A B C D A B C D ...

        :param iter: A cycle of server list
        :type iter: cycle
        :return: The next iteration (address) in the cycle
        :rtype: tuple
        """
        # round_robin([A, B, C, D]) --> A B C D A B C D A B C D ...
        return next(iter)

    def select_server(self, server_list, algorithm):
        """Selects the server for the client, by utilising one of the load balancing strategies

        :param server_list: list of servers to choose from
        :type server_list: _type_
        :param algorithm: The alogrithm to implement load balancing
        :type algorithm: str
        :raises Exception: If some other algorithm is typed then it will throw error
        :return: port of the assigned server
        :rtype: int
        """
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
