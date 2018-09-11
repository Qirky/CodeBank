from __future__ import absolute_import, print_function

try:
    import socketserver
except ImportError:
    import SocketServer as socketserver

import socket
import json
import sys
import random

from threading import Thread
from time import sleep
from getpass import getpass
from hashlib import md5

from ..utils import *
from ..app import *

class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """ Base class """
    pass

class Server(ThreadedServer):
    """ Wrapper to the threaded server instance """
    def __init__(self, port=57890):

        # Get password
        try:

            self.password = md5(getpass("Password (leave blank for no password): ").encode("utf-8"))

        except KeyboardInterrupt:

            sys.exit("Exited")

        # Listen on any IP
        self.listening_address  = "0.0.0.0"
        self.port     = int(port)
        
        # Get IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.hostname = s.getsockname()[0]
        s.close()

        self.address = (self.hostname, self.port)

        # Keep track of all the connected clients

        self.__order_id    = 0
        self.__codelet_id  = 0
        self.__client_id   = 0
        self.__seed        = random.randint(0, 2048) # Force all clients to use the same seed

        self.clients       = [] # Client objects
        self.users         = {} # ID: Name

        # Instantiate server process

        RequestHandler.set_master(self)

        ThreadedServer.__init__(self, (self.listening_address, self.port), RequestHandler)

        self.server_thread = Thread(target=self.serve_forever)
        self.running = False

        # Create interface

        import FoxDot

        self.app = ServerApp(self, FoxDot)

    def __str__(self):
        return "{} on port {}\n".format(self.hostname, self.port)

    def start(self):
        """ Starts listening on the socket """

        print("Server running @ {}".format(str(self)))

        self.app.lang.allow_connections()
        self.app.seed = self.get_seed()
        self.running = True
        self.server_thread.start()
        self.app.run()

        return

    def kill(self):
        """ Properly terminates the server instance """
        
        # Stop running loop

        self.running = False
        self.app.lang.allow_connections(False)

        self.send_to_all(MESSAGE_SHUTDOWN())

        # Remove users
        for user_id in list(self.users.keys()):

            self.app.remove_user(user_id)

        # Close server
        self.shutdown()
        self.server_close()
        return

    def next_client_id(self):
        self.__client_id += 1
        return self.__client_id

    def next_codelet_id(self):
        self.__codelet_id += 1
        return self.__codelet_id

    def next_order_id(self):
        self.__order_id += 1
        return self.__order_id

    def get_seed(self):
        return self.__seed

    def add_new_client(self, address, socket, name):
        """ """
        user_id = self.next_client_id()
        self.clients.append( Client(user_id, address, socket, name) )
        self.app.add_user(user_id, name)
        return user_id

    def remove_from_server(self, client_address):
        """ Removes the reference to this client on the server"""
        for i, client in enumerate(self.clients):
            if client_address == client.address:
                self.app.remove_user(client.id)
                del self.clients[i]

                # If the user has loaded a codelet, release it
                codelet_id = self.app.users.get(client.id, None)
                
                if codelet_id is not None:
                
                    self.app.handle_release_codelet(client.id, codelet_id)
                
                self.send_to_all(MESSAGE_REMOVE(client.id))
                
                break
        return

    def send_to_client(self, client_id, data):
        for client in self.clients:
            if client.id == client_id:
                client.send(data)
        return

    def send_to_all(self, data):
        for client in self.clients:
            client.send(data)
        return

    def connections(self):
        for client in self.clients:
            yield client.socket

    def authenticate(self, password):
        """ Returns True if password is correct """
        return password == self.password.hexdigest()


class RequestHandler(socketserver.BaseRequestHandler):
    """ Created whenever a new connection to the server is made:
        self.request = socket
        self.server  = Server instance
        self.client_address = (address, port)
    """
    master = None

    @classmethod
    def set_master(cls, server):
        cls.master = server

    def get_user_details(self):
        # Get name and password

        data = read_from_socket(self.request)           

        if data is None:

            print("Client disconnected from {}".format(self.client_address))

            raise ValueError

        else:

            username = data[0]
            password = data[1]

            if not self.master.authenticate(password):

                return

        self.name    = username
        self.user_id = self.master.add_new_client(self.client_address, self.request, self.name)

        return self.user_id, self.name

    def handle(self):
        """ Overload """

        try:

            data = self.get_user_details()

        except ValueError:

            return

        if data is None:

            send_to_socket(self.request, MESSAGE_ERROR(-1, "Failed login."))

            print("Failed login attempt from {} - {}".format(*self.client_address))

            return

        else:

            print("new connection from {} - {}".format(*self.client_address))

            self.handle_new_connection()

        # Continually read from client until disconnected

        while True:

            data = read_from_socket(self.request)           

            if data is None:

                print("Client disconnected from {}".format(self.client_address))

                self.master.remove_from_server(self.client_address)

                break

            self.process_data(data)
            
        return

    def process_data(self, data):
        """ Method for handling data that arrives and sends appropriate
            data out to connected clients """

        # Handle on the server side

        self.master.app.handle_data(data)

        return

    def handle_new_connection(self):
        """ Called during a connection, updates connected clients with name information
            and resets the seed for random number generation etc.  """

        # Send the user_id to the client

        self.send([HANDLE_SET_ID, self.user_id])

        # Notify other users

        self.send_to_all( MESSAGE_NAME(self.user_id, self.name) )

        # Rest the seed

        self.send( MESSAGE_SEED(seed=self.master.get_seed()) )

        # Grab current code

        self.pull_all_code()

        return

    def pull_all_code(self):
        """ Sends all current codelet data to the client """
        # Get all the connected users
        for id_num, name in self.master.users.items():
            if id_num != self.get_user_id():
                self.send(MESSAGE_NAME(id_num, name))

        # Get all the code
        for codelet in self.master.app.get_codelets():
            data = MESSAGE_HISTORY(-1, codelet.get_id(), codelet.get_history(), codelet.get_order_id())
            self.send(data)
        return

    def send(self, data):
        """ Sends the data to THIS connected client """
        self.master.send_to_client(self.user_id, data)
        return

    def send_to_all(self, data):
        """ Forwards 'data' to all connected clients """

        for socket in self.master.connections():

            send_to_socket(socket, data)

        return

    def get_user_id(self):
        return self.user_id

    def get_username(self):
        return self.name

    def get_user_info(self):
        return (self.get_user_id(), self.get_username())


class Client:
    """ Keeps track of information on connected clients """
    def __init__(self, id_num, address, socket, name):
        self.address = address
        self.socket  = socket
        self.id      = id_num
        self.name    = name

    def send(self, data):
        return send_to_socket(self.socket, data)

if __name__ == "__main__":

    test = Server()
    test.start()







