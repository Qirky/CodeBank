from __future__ import absolute_import, print_function

import socket
from threading import Thread
from hashlib import md5
from ..utils import *
from ..app import *

import FoxDot # should pipe to FoxDot

# FoxDot = None

class Client:
    """ Represents the local client and talks to the server """
    def __init__(self):
        # Connection info
        self.hostname  = None
        self.port      = None
        self.address   = None
        self.socket    = None
        self.daemon    = None
        self.listening = False
        # User information
        self.users     = {}
        self.user_id   = None
        self.user_name = None
        # UI
        self.app       = App(self, FoxDot)

    def run(self):
        """ Calls the mainloop method on the application """
        self.app.run()

    def connect(self, hostname, port, username, password):
        """ Connects to the server instance """

        # Get details of remote
        self.hostname  = hostname
        self.port      = int(port)
        self.address   = (self.hostname, self.port)
        self.user_name = username

        # Connect to remote

        try:

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket.connect(self.address)

        except Exception as e:

            raise(e)

            raise(ConnectionError("Could not connect to host '{}'".format( self.hostname ) ) )

        # Password test

        self.authenticate_with_server(username, password)

        # Start listening

        self.listening = True
        self.daemon = Thread(target=self.listen)
        self.daemon.start()

        # Connect FoxDot isntances

        self.app.lang.Clock.connect(self.hostname)

        # Enable app

        self.app.enable()
        
        return self

    def authenticate_with_server(self, username, password):
        """ Encrypts password and send a basic message to the server with username and password."""
        self.send( [username, md5(password.encode("utf-8")).hexdigest()] )
        self.recv()
        return

    def is_connected(self):
        """ Returns True if the client is connected to the server """
        return self.listening

    def send(self, data):
        """ Sends data to server """
        return send_to_socket(self.socket, data)

    def recv(self):
        """ Read data from self.socket """
        try:
            data = read_from_socket(self.socket)
            if data is None:
                return 0
        except ValueError as e:
            raise ConnectionError("Connection lost to server. {}".format(e))
        self.app.handle_data(data)
        return 1

    def listen(self):
        """ Listens out for data coming from the server and passes it on
            to the handler.
        """
        while self.listening:
            if self.recv() is 0:
                break
        return      

    def kill(self):
        """ Properly terminates the connection to the server """
        self.listening = False
        if self.socket is not None:
            self.socket.close()
        if self.daemon is not None:
            self.daemon.join(1)
        self.app.lang.Clock.stop()
        return
