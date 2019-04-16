#!/usr/sbin/python3
import socket
import sys
import argparse
import time
from statistics import mean
from sys import getsizeof
from concurrent.futures.thread import ThreadPoolExecutor


time_list = []
clients = []

SERVER_IP = sys.argv[1]
PORT = sys.argv[2]
CLIENT_ARG = sys.argv[3]
REQUESTS_ARG = sys.argv[4]


#Parsed to int
CLIENTS = int(CLIENT_ARG)
REQUESTS = int(REQUESTS_ARG)
PORT_NUMBER = int(PORT)


parser = argparse.ArgumentParser()
parser.add_argument("IP", help="Type in the server ip")
parser.add_argument("Port", help="Type in the server port")
parser.add_argument("Clients", help="Type in the number of clients")
parser.add_argument("Requests", help="Type in the number of requests")	
parser.add_argument("File name to open", help="Type file name")
args = parser.parse_args()

f=open(sys.argv[5], "r")
MESSAGE = f.read()
f.close()



#This class sets the socket information for IP, Ports, requests, clients 
#taken from user input and passes it along to the socket information 
#to be handled when the class runs. It starts timing when it sends messages
#back to the server, looping forward to keep sending the maximum buffer until 
#the message is completely sent. Then it displays the time it took to the user.
#It cleans up and closes the socket upon finishing sending message.
class Client():

    def __init__(self, ip, port, message, requests, name):
        self.request = 0
        self.data_sent = 0
        self.name = name
        self.message = message
        self.serv_ip = ip
        self.serv_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((self.serv_ip, self.serv_port))
    def run(self):

        try:
            for i in range(REQUESTS):
                totalsent=0
                start = time.time()
                while totalsent < getsizeof(self.message):
                    sent = self.sock.send(self.message[totalsent:(totalsent+1024)].encode())
                    totalsent = totalsent + 1024
                    response = self.sock.recv(1024).decode()
                    print(response, end = "")
                    print("size of msg-", getsizeof(self.message), "totalsent-", totalsent, end = "\n")
                
                end = time.time()
                time_list.append((end-start)*1000)
                self.request += 1
                self.data_sent += getsizeof(self.message.encode())
                time.sleep(1/REQUESTS)



        finally:
            self.sock.close()

        print("Client information-", self.name, "sent", self.data_sent,
              "bytes, and made", self.request, "requests\n")

if __name__ == "__main__":
    with ThreadPoolExecutor(CLIENTS) as executor:
        for CLIENT in range(CLIENTS):
            executor.submit(
                clients.append(Client(SERVER_IP, PORT_NUMBER, MESSAGE, REQUESTS, CLIENT)))

    with ThreadPoolExecutor(CLIENTS) as executor:
        for client in clients:

            executor.submit(client.run())
    total_requests_sent = 0
    for c in clients:
        total_requests_sent += c.request
    print("Created", str(len(clients)),"clients")
    print("Total requests sent:", str(total_requests_sent))
    print("Average time of getting response: " + str(mean(time_list)) + " ms" + "\n")
