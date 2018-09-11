from __future__ import absolute_import, print_function

from ..utils import *
from ..datatypes import *
from .tkimport import Tk, tkFont
from .menu import MenuBar
from .public import SharedSpace
from .private import Workspace

import socket
import random

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

        self.root.bind("<{}-equal>".format(CONTROL_KEY), self.increase_font_size)
        self.root.bind("<{}-minus>".format(CONTROL_KEY), self.decrease_font_size)

        # Socket is an instance of Client
        self.socket = client

        # Top canvas box for containing code blocks
        self.sharedspace = SharedSpace(self)
        self.sharedspace.grid(row=0, column=0)

        # Action for on-click of codelets

        self.codelet_on_click = lambda *args, **kwargs: None
        self.disable_codelet_highlight = lambda *args, **kwargs: True

        self._mouse_in_codebox_flag = False

        # FoxDot interpreter

        self.lang = lang
        self.seed = 0

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

        try:   
        
            handle(userid, *packet)

        except RuntimeError:

            pass
        
        return

    def evaluate(self, code):
        """ Passes a string to FoxDot to exectute """
        
        if self.lang is not None:

            return self.lang.execute(code)

        return

    def evaluate_codelet(self, codelet):
        """ Takes an instance of Codelet or CodeBox and evaluates the code. If there
            is an error, flag it with the codelet """

        string = self.evaluate(codelet.get_text())

        if contains_error(string):

            codelet.flag_error()

        self.sharedspace.redraw()

        return

    def evaluate_codelet_history(self, codelet):
        """ Iterates over the codelet.history and evaluates all strings  """
        for user_id, string in codelet.get_history():
            self.evaluate(string)
        return

    def update_random_seed(self, user_id=-1, seed=0):
        """ Sets the seed for random number generators"""
        self.evaluate("RandomGenerator.set_override_seed({})".format(seed), verbose=False)
        return

    def get_codelets(self):
        """ Returns the list of code-box abstractions of the stored codelets  """
        return self.sharedspace.codelets.values()

    def get_codelet(self, codelet_id):
        return self.sharedspace.codelets[codelet_id].get_codelet()

    def add_user(self, user_id, name):
        """ Stores a user's name and associates it with their ID - also updates UI based on this info """
        self.socket.users[user_id] = name
        self.sharedspace.peer_box.add_user(user_id, name)
        return

    def get_user_name(self, user_id):
        return self.socket.users[user_id]

    def remove_user(self, user_id):
        if user_id in self.socket.users:
            del self.socket.users[user_id]
            self.sharedspace.peer_box.remove_user(user_id)
        return

    def increase_font_size(self, event=None):
        font = tkFont.nametofont("CodeFont")
        size = min(font.actual()["size"]+2, 28)
        font.configure(size=size)
        return "break"

    def decrease_font_size(self, event=None):
        font = tkFont.nametofont("CodeFont")
        size = max(font.actual()["size"]-2, 8)
        font.configure(size=size)
        return "break"

    # Override
    def get_cursor_icon(self):
        return ""

    def get_active_cursor_icon(self):
        return ""

    def mouse_in_codebox(self):
        """ Returns True if the mouse is on a codebox """
        return self._mouse_in_codebox_flag

    def set_mouse_in_codebox(self, active):
        self.root._mouse_in_codebox_flag = bool(active)
        return