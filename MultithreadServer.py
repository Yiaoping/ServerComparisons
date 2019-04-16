import threading
import sys
import argparse
import socketserver
from statistics import mean
from sys import getsizeof

#This is the multi-threaded server that takes in user input
#and handles a connection by using thread. Each time a connection
#is created, a thread is forked and each connection is being
#processed by a thread. 

SERVER_IP = sys.argv[1]
PORT = sys.argv[2]
PORT_NUMBER = int(PORT)

parser = argparse.ArgumentParser()
parser.add_argument("IP", help="Type in the server ip")
parser.add_argument("Port", help="Type in the server port")
args = parser.parse_args()

BUFFER = 1024
peers={}
total_data = []

#This class handles incoming data from client up to a certain
#size of the buffer. For each connection, it gets threaded and 
#passes each thread into an array so client knows how many threads
#or clients are currently connected.
class myThread(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            data = self.request.recv(BUFFER)
            if data:
                current_thread = threading.current_thread()
                peers[current_thread]=getsizeof(data)
                total_data.append(getsizeof(data))
                response = "%s: %s" %(current_thread.name, data)
                print('echoing', 'to', self.client_address)
                try:
                    self.request.sendall(response.encode())
                except:
                    print('error in sending')
            else:

                self.finish()
#Uses ThreadingMixIn to be handled asynchronously
class mTCPServer(socketserver.ThreadingMixIn, socketserver.
TCPServer):
    pass

#Passes in the IP and PORT to TCPServer, while creating a
#thread to invoke the function and passing it in as an argument
#to TCPServer. It runs the server until a shutdown is explicitly
#told, then displays number of currently connected clients and
#the data that was received.
if __name__ == "__main__":
    server = mTCPServer((SERVER_IP, PORT_NUMBER), myThread)
    print("Listening on", server.server_address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    print("Accepted clients:", str(len(peers)),"clients")
    print("Total data received:",str(sum(total_data)))
