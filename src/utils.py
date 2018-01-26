import json
from socket import error as socket_error

# Handler codes

HANDLE_KILL    = 0
HANDLE_PUSH    = 1
HANDLE_DELETE  = 2
HANDLE_LOAD    = 3
HANDLE_DISABLE = 4
HANDLE_UNDO    = 5
HANDLE_NAME    = 6
HANDLE_REQUEST = 7
HANDLE_SET_ID  = 8
HANDLE_RELEASE = 9
HANDLE_UPDATE  = 10
HANDLE_ERROR   = 11
HANDLE_INFO    = 12
HANDLE_REMOVE  = 13
HANDLE_HISTORY = 14

def MESSAGE_KILL(user_id):
    return [HANDLE_KILL, user_id]

def MESSAGE_PUSH(user_id, codelet_id, string):
    return [HANDLE_PUSH, user_id, codelet_id, string]

def MESSAGE_UPDATE(user_id, codelet_id, string, order_id):
    return [HANDLE_UPDATE, user_id, codelet_id, string, order_id]

def MESSAGE_LOAD(user_id, codelet_id):
    return [HANDLE_LOAD, user_id, codelet_id]

def MESSAGE_RELEASE(user_id, codelet_id):
    return [HANDLE_RELEASE, user_id, codelet_id]

def MESSAGE_NAME(user_id, name):
    return [HANDLE_NAME, user_id, name]

def MESSAGE_REQUEST(user_id, codelet_id):
    return [HANDLE_REQUEST, user_id, codelet_id]

def MESSAGE_ERROR(user_id, err_msg):
    return [HANDLE_ERROR, user_id, err_msg]

def MESSAGE_INFO(user_id, string):
    return [HANDLE_INFO, user_id, string]

def MESSAGE_REMOVE(user_id):
    return [HANDLE_REMOVE, user_id]

def MESSAGE_HISTORY(user_id, codelet_id, data, order_id):
    return [HANDLE_HISTORY, user_id, codelet_id, data, order_id]

# Class and functions for creating and sending messages to the server/clients

class Message:
    """ Wrapper for JSON messages sent to the server """
    def __init__(self, data):
        self.data = data
    def __str__(self):
        """ Prepares the json message to be sent with first 4 digits
            denoting the length of the message """
        packet = str(json.dumps(self.data, separators=(',',':')))
        length = "{:04d}".format( len(packet) )
        return length + packet
    def __len__(self):
        return len(str(self))
    def as_string(self):
        return str(self)
    def as_bytes(self):
        return str(self).encode("utf-8")


def read_from_socket(sock):
    """ Reads data from the socket """
    # Get number single int that tells us how many digits to read
    try:
        bits = int(sock.recv(4))
        if bits > 0:
            # Read the remaining data (JSON)
            data = sock.recv(bits)
            # Convert back to Python data structure
            return json.loads(data)
    except (ConnectionAbortedError, ConnectionResetError):
        return None

def send_to_socket(sock, data):
    """ Converts Python data structure to JSON message and
        sends to a connected socket """
    msg = Message(data)
    # Get length and store as string
    msg_len, msg_str = len(msg), msg.as_bytes()
    # Continually send until we know all of the data has been sent
    sent = 0
    while sent < msg_len:
        bits = sock.send(msg_str[sent:])
        sent += bits
    return

# Codelet colour information

USER_COLOURS = [ 
    "#66D9EF", 
    "#ff8000", 
    "Gold", 
    "#A6E22E", 
    "Deep Pink",
    "Yellow", 
    "Dodger Blue",
    "DarkOrchid1", 
    "Orange Red", 
    "Lime Green" 
    ]

def GET_USER_COLOUR(i):
    return USER_COLOURS[i % len(USER_COLOURS)]

def GET_DISABLED_COLOUR(i=None):
    return "#b3b3b3"

def GET_ERROR_COLOUR(i=None):
    return

# Extracting informaton from code

import re
def get_players(string):
    """ Uses RegEx to return the FoxDot players in a block of text """
    return re.findall(r"(\w+)\s*>>", string)