from ..utils import *
from ..datatypes import *
from .tkimport import Tk, tkFont
from .menu import MenuBar
from .public import SharedSpace
from .private import Workspace

import socket

# This removed blurry fonts on Windows
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# Baseclass

class BasicApp:

    def __init__(self, client, lang):
        self.root=Tk.Tk()

        # General config e.g. title
        self.root.protocol("WM_DELETE_WINDOW", self.kill )

        Tk.Grid.columnconfigure(self.root, 0, weight=1)
        Tk.Grid.rowconfigure(self.root, 0, weight=1)

        self.default_font = 'Consolas'

        if self.default_font not in tkFont.families():

            if SYSTEM == WINDOWS:

                self.default_font = "Consolas"

            elif SYSTEM == MAC_OS:

                self.default_font = "Monaco"

            else:

                self.default_font = "Courier New"

        self.font = tkFont.Font(font=(self.default_font, 12), name="CodeFont")
        self.font.configure(family=self.default_font)

        # Socket is an instance of Client
        self.socket = client

        # Top canvas box for containing code blocks
        self.sharedspace = SharedSpace(self)
        self.sharedspace.grid(row=0, column=0)

        # Action for on-click of codelets

        self.codelet_on_click = lambda *args, **kwargs: None

        # FoxDot interpreter

        self.lang = lang

    def run(self):
        """ Starts the TKinter mainloop """
        try:
            self.root.mainloop()
        except (KeyboardInterrupt, SystemExit):
            self.kill()

    def kill(self, *args, **kwargs):
        """ Correctly shuts down the application """        
        self.socket.kill()
        self.root.destroy()
        return

    def handle_data(self, data):
        """ Passes the data to the correct workspace handler based on the second item in the data:
            [header, src_user_id, data, ...] """
        
        header = data[0]
        userid = data[1]
        packet = data[2:]
    
        handle = self.handlers[header]
    
        handle(userid, *packet)
        
        return

    def evaluate(self, code):
        """ Passes a string to FoxDot to exectute """
        
        if self.lang is not None:

            self.lang.execute(code)

        return

    def evaluate_codelet_history(self, codelet):
        """ Iterates over the codelet.history and evaluates all strings  """
        for user_id, string in codelet.get_history():
            self.evaluate(string)
        return

    def get_codelets(self):
        """ Returns the list of code-box abstractions of the stored codelets  """
        return self.sharedspace.codelets.values()

    def add_user(self, user_id, name):
        """ Stores a user's name and associates it with their ID - also updates UI based on this info """
        self.socket.users[user_id] = name
        self.sharedspace.peer_box.add_user(user_id, name)
        return

    def remove_user(self, user_id):
        del self.socket.users[user_id]
        self.sharedspace.peer_box.remove_user(user_id)
        return