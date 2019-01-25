from __future__ import absolute_import, print_function

try:
    import socketserver
except ImportError:
    import SocketServer as socketserver

import socket
import json
import sys
import random
import queue

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
    def __init__(self, interpreter, **kwargs):

        # Get password
        try:

            self.password = md5(getpass("Password (leave blank for no password): ").encode("utf-8"))

        except KeyboardInterrupt:

            sys.exit("Exited")

        # Listen on any IP
        self.listening_address  = "0.0.0.0"
        self.port = SERVER_PORT_NUMER # from utils library
        
        # Get IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.hostname = s.getsockname()[0]
        s.close()

        self.address = (self.hostname, self.port)

        # Create a process queue

        self.queue = queue.Queue()

        # Keep track of all the connected clients

        self.__order_id    = 0
        self.__codelet_id  = 0
        self.__client_id   = 0
        self.__seed        = random.randint(0, 2048) # Force all clients to use the same seed

        self.clients       = [] # Client objects
        self.address_book  = {} # All client instances that connect / disconnect
        self.users         = {} # ID: instance of User

        # Instantiate server process

        RequestHandler.set_master(self)

        ThreadedServer.__init__(self, (self.listening_address, self.port), RequestHandler)

        self.server_thread = Thread(target=self.serve_forever)
        self.running = False

        # Create interface

        self.app = ServerApp(self, **kwargs)
        self.app.set_interpreter(interpreter)
        self.app.update_random_seed(seed=self.get_seed())

    def __str__(self):
        return "{} on port {}\n".format(self.hostname, self.port)

    def start(self):
        """ Starts listening on the socket """

        print("Server running @ {}".format(str(self)))

        self.app.lang.start_server()        
        self.running = True
        self.server_thread.start()
        self.app.run()

        return

    def add_to_queue(self, message):
        """ Adds a message to the process queue """
        return self.queue.put(message)

    def kill(self):
        """ Properly terminates the server instance """
        
        # Stop running loop

        self.running = False
        self.app.lang.stop_server()
        self.app.lang.kill()

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

    def get_from_address_book(self, name, address):
        """ """
        return self.address_book.get((name, address[0]), None)

    def add_new_client(self, address, socket, name):
        """ Creates a new client isntance and adds it to the GUI. If the name
            is already in the address book and not connected, that user re-assumes  
            their data """

        existing_client = self.get_from_address_book(name, address)

        if existing_client is not None:

            if existing_client.connected:

                raise LoginError("User '{}' already connected".format(name))

            user_id    = existing_client.get_id()
            new_client = existing_client.connect(socket)
            new_client.update_address(address)

        else:

            user_id = self.next_client_id()
            new_client = Client(user_id, address, socket, name)

            self.add_to_address_book( new_client )

        self.clients.append( new_client )
        self.app.add_user(user_id, name)
        
        return user_id

    def add_to_address_book(self, client):
        """ Stores a client in the address book dictionary """
        self.address_book[(client.name, client.host)] = client
        return

    def remove_from_server(self, client_address):
        """ Removes the reference to this client on the server"""
        for i, client in enumerate(self.clients):
            if client_address == client.address:

                client.disconnect()
                
                self.app.remove_user(client.id)
                
                del self.clients[i]

                # If the user has loaded a codelet, release it
                codelet_id = self.users.get(client.id, None)
                
                if codelet_id is not None:
                
                    self.app.handle_release_codelet(client.id, codelet_id)
                
                self.send_to_all(MESSAGE_REMOVE(client.id))
                
                break
        return

    def send_to_client(self, client_id, data):
        for client in list(self.clients):
            if client.id == client_id:
                client.send(data)
                return
        return

    def send_to_all(self, data):
        for client in list(self.clients):
            client.send(data)
        return

    def connections(self):
        for client in list(self.clients):
            yield client.socket

    def authenticate(self, password):
        """ Returns True if password is correct """
        return password == self.password.hexdigest()

    def check_lang_id(self, lang_id):
        """ Returns True if the lang_id matches that used by the server """
        return int(lang_id) == self.app.lang.get_id()


class RequestHandler(socketserver.BaseRequestHandler):
    """ Created whenever a new connection to the server is made:
        self.request = socket
        self.server  = Server instance
        self.client_address = (address, port)
    """
    master = None
    error_message = ""

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
            lang_id  = data[2]

            if not self.master.authenticate(password):

                raise LoginError("Failed Login: Incorrect password.")

            elif not self.master.check_lang_id(lang_id):

                raise LoginError("Failed Login: Incorrect interpreter. Please use '{}' to connect to the server.".format(self.master.app.lang.get_name()))

        self.name    = username
        self.user_id = self.master.add_new_client(self.client_address, self.request, self.name)

        return self.user_id, self.name

    def handle(self):
        """ Overload """

        try:

            data = self.get_user_details()

        except ValueError:

            # Just exit if the user disconnects during login

            return

        except LoginError as err:

            send_to_socket(self.request, MESSAGE_ERROR(-1, str(err)))

            print("Failed login attempt from {} - {}".format(*self.client_address))

            return

        # Login succesful

        print("New connection from {} - {}".format(*self.client_address))

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
        """ Adds the message to the server process Queue which is constantly being polled """

        # Handle on the server side

        self.master.add_to_queue(data)

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
        for id_num, user in list(self.master.users.items()):
            if id_num != self.get_user_id():
                self.send(MESSAGE_NAME(id_num, user.get_name()))

        # Get all the code
        for codelet in self.master.app.get_codelets():
            data = MESSAGE_HISTORY(-1, codelet.get_id(), codelet.get_history(), codelet.get_order_id(), codelet.is_hidden())
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
        self.host = self.address[0]
        self.port = self.address[1]

        self.socket  = socket
        self.id      = id_num
        self.name    = name

        self.connected = True

    def send(self, data):
        return send_to_socket(self.socket, data)

    def get_id(self):
        return self.id

    def connect(self, new_socket):
        self.socket    = new_socket
        self.connected = True
        return self

    def disconnect(self):
        self.connected = False
        return

    def update_address(self, new_address):
        self.address = new_address
        self.host    = self.address[0]
        self.port    = self.address[1]
        return

class LoginError(Exception):
    pass
