import sys, json
import os.path
from socket import error as socket_error

# If this is compiled file, just use python for speaking to FoxDot

if sys.argv[0] == sys.executable: 

    PYTHON_EXECUTABLE = "python"

else:

    PYTHON_EXECUTABLE = os.path.basename(sys.executable)

# System info

SYSTEM  = 0
WINDOWS = 0
LINUX   = 1
MAC_OS  = 2

if sys.platform.startswith('darwin'):

    SYSTEM = MAC_OS

elif sys.platform.startswith('win'):

    SYSTEM = WINDOWS

elif sys.platform.startswith('linux'):

    SYSTEM = LINUX

CONTROL_KEY = "Command" if SYSTEM == MAC_OS else "Control"

# boot file directories

BOOT_DIR = os.path.join(os.path.dirname(__file__), "boot")
TIDAL_BOOT_FILE = os.path.join(BOOT_DIR, "tidal.boot") 
# App Types

class APP_TYPES:
    SERVER = 0
    CLIENT = 1

# Handler codes

HANDLE_KILL     = 0
HANDLE_PUSH     = 1
HANDLE_DELETE   = 2
HANDLE_LOAD     = 3
HANDLE_DISABLE  = 4
HANDLE_UNDO     = 5
HANDLE_NAME     = 6
HANDLE_REQUEST  = 7
HANDLE_SET_ID   = 8
HANDLE_RELEASE  = 9
HANDLE_UPDATE   = 10
HANDLE_ERROR    = 11
HANDLE_INFO     = 12
HANDLE_REMOVE   = 13
HANDLE_HISTORY  = 14
HANDLE_HIDE     = 15
HANDLE_SHUTDOWN = 16
HANDLE_SEED     = 17
HANDLE_TYPING   = 18
HANDLE_CHAT     = 19
HANDLE_CLEAR    = 20

HANDLE_MONITOR_START = 21
HANDLE_MONITOR_STOP  = 22
HANDLE_MONITOR_EVAL  = 23

# user_id is always source

def MESSAGE_KILL(user_id):
    """ Correctly shut down application """
    return [HANDLE_KILL, user_id]

def MESSAGE_PUSH(user_id, codelet_id, string):
    """ Push new codelet to server """
    return [HANDLE_PUSH, user_id, codelet_id, string]

def MESSAGE_UPDATE(user_id, codelet_id, string, order_id):
    """ Update codelet with new data """
    return [HANDLE_UPDATE, user_id, codelet_id, string, order_id]

def MESSAGE_LOAD(user_id, codelet_id):
    """ Load / pull codelet to loca workspace """
    return [HANDLE_LOAD, user_id, codelet_id]

def MESSAGE_RELEASE(user_id, codelet_id):
    """ Push codelet with no change (does not update user_id) """
    return [HANDLE_RELEASE, user_id, codelet_id]

def MESSAGE_NAME(user_id, name):
    """ Adds a user to the directory """
    return [HANDLE_NAME, user_id, name]

def MESSAGE_REQUEST(user_id, codelet_id):
    """ Used to request access to send MESSAGE_LOAD """
    return [HANDLE_REQUEST, user_id, codelet_id]

def MESSAGE_ERROR(user_id, err_msg):
    """ Raises ConnectionError(err_msg) """
    return [HANDLE_ERROR, user_id, err_msg]

def MESSAGE_INFO(user_id, string):
    """ Prints information to console """
    return [HANDLE_INFO, user_id, string]

def MESSAGE_REMOVE(user_id):
    """  """
    return [HANDLE_REMOVE, user_id]

def MESSAGE_HISTORY(user_id, codelet_id, data, order_id, hidden=0):
    return [HANDLE_HISTORY, user_id, codelet_id, data, order_id, int(hidden)]

def MESSAGE_UNDO(user_id, codelet_id):
    return [HANDLE_UNDO, user_id, codelet_id]

def MESSAGE_HIDE(user_id, codelet_id):
    return [HANDLE_HIDE, user_id, codelet_id]

def MESSAGE_SHUTDOWN(user_id=-1):
    return [HANDLE_SHUTDOWN, user_id]

def MESSAGE_SEED(user_id=-1, seed=0):
    return [HANDLE_SEED, user_id, seed]

def MESSAGE_TYPING(user_id, flag):
    return [HANDLE_TYPING, int(user_id), int(flag)]

def MESSAGE_CHAT(user_id, message):
    return [HANDLE_CHAT, user_id, str(message)]

def MESSAGE_CLEAR(user_id):
    return [HANDLE_CLEAR, user_id]

def MESSAGE_MONITOR_START(user_id, req_id):
    return [HANDLE_MONITOR_START, user_id, req_id]

def MESSAGE_MONITOR_STOP(user_id, req_id):
    return [HANDLE_MONITOR_STOP, user_id, req_id]

def MESSAGE_MONITOR_EVAL(user_id, string):
    return [HANDLE_MONITOR_EVAL, user_id, str(string)]

# Special case codelet IDs

NULL = -1

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

def bytes_to_str(data):
    return data.decode("utf-8") if type(data) is bytes else str(data)

def read_from_socket(sock):
    """ Reads data from the socket """
    # Get number single int that tells us how many digits to read
    try:
        bits = int(sock.recv(4))
        if bits > 0:
            # Read the remaining data (JSON)
            data = sock.recv(bits)
            # Convert back to Python data structure
            return json.loads(bytes_to_str(data))
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

def rgb2hex(*rgb): 
    r = int(max(0, min(rgb[0], 255)))
    g = int(max(0, min(rgb[1], 255)))
    b = int(max(0, min(rgb[2], 255)))
    return "#{0:02x}{1:02x}{2:02x}".format(r, g, b)

def hex2rgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i+2], 16) for i in range(0,6,2) )

def avg_colour(col1, col2, weight=0.5):
    rgb1 = hex2rgb(col1)
    rgb2 = hex2rgb(col2)
    avg_rgb = tuple(rgb1[i] * (1-weight) + rgb2[i] * weight for i in range(3))
    return rgb2hex(*avg_rgb)

USER_COLOURS = [ 
    "#66D9EF", # light blue
    "#ff8000", # orange
    "#1e90ff", # blue
    "#A6E22E", # light green
    "#ff1493", # pink
    "#ffff00", # yellow
    "#f93e00", # red
    "#de0cff", # purple
    ]

def GET_USER_COLOUR(i):
    return USER_COLOURS[i % len(USER_COLOURS)]

def GET_USER_FONT_COLOUR(i):
    return "Black"

def GET_DISABLED_COLOUR(i=None):
    return "#b3b3b3"

def GET_DISABLED_FONT_COLOUR(i=None):
    return "#565656"

def GET_ERROR_COLOUR(i=None):
    return "#ffa0be"

def GET_ERROR_FONT_COLOUR(i=None):
    return "#e1325f"