from subprocess import Popen, PIPE
import time
import pwnlib
import pwn


no_servers = 4
no_clients = 100

start = time.process_time()

process = pwn.process
balancer = process(["python3", "load_balancer.py"],
                   stdout=PIPE, stderr=PIPE, stdin=PIPE)

for x in range(1, no_servers + 1):
    globals()['server%s' % x] = process(["python3", "server.py",
                                         "127.0.0.1", f"500{x}"], stdout=PIPE, stderr=PIPE, stdin=PIPE)

for x in range(1, no_clients + 1):
    globals()['client%s' % x] = process(["python3", "client.py",
                                         "127.0.0.1", "5555"], stdout=PIPE, stderr=PIPE, stdin=PIPE)

for x in range(1, no_clients + 1):
    globals()['client%s' % x].sendline(b"2")
    globals()['client%s' % x].sendline(("user"+ str(x)).encode("UTF-8"))
    globals()['client%s' % x].sendline(("pwd"+ str(x)).encode("UTF-8"))
    
    globals()['client%s' % x].sendline(("hello").encode("UTF-8"))
    globals()['client%s' % x].sendline(("i").encode("UTF-8"))
    globals()['client%s' % x].sendline(("user1").encode("UTF-8"))
    
    # globals()['client%s' % x].sendline(("\\quit").encode("UTF-8"))
    


for x in range(no_clients, 0, -1):
    globals()['client%s' % x].kill()
for x in range(no_servers):
    globals()['server%s' % (no_servers - x)].kill()
balancer.kill()

stop = time.process_time()

print(stop-start)
