# FastChat-CS251
In this project we create a fast, secure and scalable chat application.
The aim of our project was:
- To obtain **high throughput** with limited resources dedicated for the servers
- To ensure **low latency** of individual message deliveries
- To have **E2E encryption** between clients
- To have a **robust** application that can prevent password retrieval attacks
---
## Members
- Om Godage
- Shubham Hazra
- Harshit Morj
---
## Running Instructions
```python
mkdir databases
chmod +x kill_server.sh
# To install required libraries
pip install -r requirements.txt
python3 load_balancer.py <num_servers> <port>
python3 client.py 127.0.0.1 <load_balancer_port>
# this code will be run for as many users there are
```

### For MacOS Users
For sending images, you need to run this command first,
```bash
sudo sysctl -w net.inet.udp.maxdgram=65535
```
This increases the maximum UDP package size, allowing to share larger images.
---
## High Throughput
We have implemented _multiple servers_, with _load balancing strategies_.
Having seen the least connection and the round robin strategy, we chose to perform random allocation of the servers, to get the simplicity of the implementation, as well as the efficiency of the least connection method.

## Low Latency
We have used the _User Diagram Protocol (UDP)_ for communication between the clients and the servers.
UDP is considerably faster than traditional TCP, with transmission having no delays or extended latency times.User datagram protocol does not need an established connection to start sending packets. Therefore, it saves the time typically required to turn on the server and place it in a “passive open,” listening state.

## E2E encryption
We have implemented the infamous **RSA encryption** between any messsage sent from a user to a server.
Not even the servers can see what the message contains. All the text and images sent over the network are encrypted

## Robust Database
We have used Sqlite3 for the database, which is extremely portable, and most importantly, it is _fast_. As we needed a database that could perform fast read queries, with not many complex operations.We created tables to store User Info, Messages, Groups. We have maintained user privacy by **salting & hashing** of passwords stored in the database, and we have stored the messages in the encrypted form itself. There is no easy way to retrieve this information by an attacker, rainbow tables and brute force attacks will prove useless, as the _bcrypt_ library uses the popular **SHA-256** cryptographic hash.

## Other features
We used the threading library to receive and send messages simultaneously, incorporated a friendly look to the UI from _colorama_ and _termcolor_
