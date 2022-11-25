from subprocess import Popen, PIPE
import time
from time import sleep
import pwnlib
import pwn
import sys

no_clients = int(sys.argv[1])

start = time.process_time()

process = pwn.process
# balancer = process(["python3", "load_balancer.py",f"{no_servers}","5555"],
#                    stderr=PIPE, stdin=PIPE)

# for x in range(1, no_servers + 1):
#     globals()['server%s' % x] = process(["python3", "server.py",
#                                          "127.0.0.1", f"500{x}"], stdout=PIPE, stderr=PIPE, stdin=PIPE)

for x in range(1, no_clients + 1):
    globals()['client%s' % x] = process(["python3", "client.py",
                                         "127.0.0.1", "5555"], stderr=PIPE, stdin=PIPE)

for x in range(1, no_clients + 1):
    globals()['client%s' % x].sendline(b"2")
    sleep(0.5)
    globals()['client%s' % x].sendline(("user"+ str(x)).encode())
    sleep(0.5)
    globals()['client%s' % x].sendline(("pwd"+ str(x)).encode())
    sleep(0.5)
    # b"" == globals()['client%s' % x].recvline()

    # globals()['client%s' % x].sendline(("\\quit").encode("UTF-8"))
    
for x in range(1, no_clients + 1):
    for x in range(1, no_clients + 1):
            globals()['client%s' % x].sendline(("hello").encode())
            sleep(0.5)
            globals()['client%s' % x].sendline(("i").encode())
            sleep(0.5)
            globals()['client%s' % x].sendline((f"user{(x+1)%no_clients}").encode())
            sleep(0.5)
for x in range(no_clients, 0, -1):
    globals()['client%s' % x].kill()

stop = time.process_time()

print(stop-start)

# process(["rm", "-rf","databases"],
#                    stderr=PIPE, stdin=PIPE)
# process(["mkdir","databases"],
#                    stderr=PIPE, stdin=PIPE)
