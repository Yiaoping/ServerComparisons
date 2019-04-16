#!/usr/sbin/python3
import sys
import argparse
import selectors
import socket,time

#This file is the tcp Epoll server, where it uses EPOLL to 
#process the connections, not requiring to check whether
#each socket has activity since it's been informed already
#upon the first time socket had activity occurring.
#User arguments server IP and PORT are taken in and 
#passed to create socket connection. It listens for data from
#client and upon listening, sends the data back to the client.
#User is displayed stats such as time and number of active connections.


SERVER_IP = sys.argv[1]
PORT = sys.argv[2]

PORT_NUMBER = int(PORT)

parser = argparse.ArgumentParser()
parser.add_argument("IP", help="Type in the server ip")
parser.add_argument("Port", help="Type in the server port")
args = parser.parse_args()

BUF_SIZE = 1024
sel = selectors.EpollSelector()
peers = {}
peers_count = 0

#This function accepts the socket connection incoming from client
#and sets blocking to false. It then runs the read function
def accept(sock, mask):
    conn, addr = sock.accept()
    print('accepted from', addr)
    conn.setblocking(False)
    peers[conn.fileno()] = conn.getpeername()
    sel.register(conn, selectors.EVENT_READ, read)


#This function is invoked by the accept function, receiving incoming data
#up to a certain buffer size. Once data is received, it sends the data back
#to the client.
def read(conn, mask):
    data = conn.recv(BUF_SIZE)

    if data:
        peername = conn.getpeername()
        conn.send(data)

    else:
        peername = peers[conn.fileno()]
        print('closing', peername)
        del peers[conn.fileno()]
        sel.unregister(conn)
        conn.close()


sock = socket.socket()
sock.bind((SERVER_IP, PORT_NUMBER))
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)
last_report_time = time.time()
while True:
    events = sel.select(timeout=0.2)
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)
    cur_time = time.time()
    if cur_time - last_report_time > 1:
        print('Running report...')
        print('Num active peers = {0}'.format(len(peers)))
        last_report_time = cur_time
