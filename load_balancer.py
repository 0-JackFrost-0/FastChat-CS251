import sys
import socket
import select
import random
from itertools import cycle
import pickle

SERVER_POOL = [('localhost', 5001), ('localhost', 5000)]


ITER = cycle(SERVER_POOL)
def round_robin(iter):
    # round_robin([A, B, C, D]) --> A B C D A B C D A B C D ...
    return next(iter)


class LoadBalancer(object):
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

    sockets = list()

    def __init__(self, ip, port, algorithm='random'):
        self.ip = ip
        self.port = port
        self.algorithm = algorithm

        # init a client-side socket
        self.cs_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire.
        # self.cs_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.cs_socket.bind((self.ip, self.port))
        print ('init client-side socket: %s' % (self.cs_socket.getsockname(),))
        self.sockets.append(self.cs_socket)

    def start(self):
        while True:
            try:
                data, addr = self.cs_socket.recvfrom(4026)
            except:
                print('a connection closed')
                break
            # to decode the data
            # message = int(pickle.loads(data))
            self.on_accept(addr)

    def on_accept(self, cport):
        server_ip, server_port = self.select_server(SERVER_POOL, self.algorithm)
        print("sending port", cport)
        self.cs_socket.sendto(pickle.dumps(str(server_port)), cport)

    def select_server(self, server_list, algorithm):
        if algorithm == 'random':
            return random.choice(server_list)
        elif algorithm == 'round robin':
            return round_robin(ITER)
        else:
            raise Exception('unknown algorithm: %s' % algorithm)


if __name__ == '__main__':
    try:
        LoadBalancer('localhost', 5555, 'round robin').start()
    except KeyboardInterrupt:
        print("Ctrl C - Stopping load_balancer")
        sys.exit(1)