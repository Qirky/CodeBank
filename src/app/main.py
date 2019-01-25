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
    text = None
    visible = True
    def __init__(self, client, *args, **kwargs):

        self.visible = kwargs.get("visible", True)

        if self.visible:

            try:

                self.root=Tk.Tk()

            except Tk.TclError as err:

                print("TclError: {}".format(err))
                sys.exit("Use 'python {} -n' to run in no-gui mode.".format(sys.argv[0]))

            # General config e.g. title
            self.root.protocol("WM_DELETE_WINDOW", self.kill )
            self.root.geometry("1440x720") # default size

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

        else:

            self.root = None

        # Socket is an instance of Client / Server
        self.socket = client
        self.users  = self.socket.users

        # Top canvas box for containing code blocks
        self.sharedspace = SharedSpace(self)

        if self.visible:

            self.sharedspace.grid(row=0, column=0, sticky=Tk.NSEW)
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)

            # Action for on-click of codelets -- maybe put  in def disable

            self.codelet_on_click = lambda *args, **kwargs: None
            self.disable_codelet_highlight = lambda *args, **kwargs: True

            self._mouse_in_codebox_flag = False

        # Interpreter

        self.lang = None
        self.seed = 0

    def set_interpreter(self, interpreter, *args, **kwargs):
        """ Starts up the interpreter """

        self.lang = interpreter(*args, **kwargs) # raises an error if file not found

        return

    def run(self):
        """ Starts the TKinter mainloop """
        try:
            self.root.mainloop()
        except (KeyboardInterrupt, SystemExit):
            self.kill()

    def kill(self, *args, **kwargs):
        """ Correctly shuts down the application """        
    
        self.socket.kill()
        self.reset_stdout()
    
        if self.visible:
    
            self.root.destroy()
    
        return

    def reset_stdout(self):
        """ Reset stdout for any error messages that are displayed when the window closes """
        sys.stdout = sys.__stdout__
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

        except RuntimeError as e:

            print(e)

            pass
        
        return

    def evaluate(self, code, verbose=True):
        """ Passes a string to FoxDot to exectute """
        
        if self.lang is not None:

            return self.lang.execute(code, verbose=verbose)

        return 

    def evaluate_codelet(self, codelet):
        """ Takes an instance of Codelet or CodeBox and evaluates the code. If there
            is an error, flag it with the codelet """

        string = self.evaluate(codelet.get_text())

        if self.lang.contains_error(string):

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
        self.evaluate(self.lang.get_random_seed_setter(seed), verbose=False)
        return

    def receive_chat_message(self, user_id, message):
        """ Handler for getting a chat message, displays in the sharedspace chat widget """
        self.sharedspace.add_new_chat_message(user_id, message)
        return

    def clear_clock(self, *args):
        """ Stops the scheduling clock """
        self.evaluate(self.lang.get_stop_sound())
        return

    def get_codelets(self):
        """ Returns the list of code-box abstractions of the stored codelets  """
        return self.sharedspace.codelets.values()

    def get_codelet(self, codelet_id):
        return self.sharedspace.codelets[codelet_id].get_codelet()

    def add_user(self, user_id, name):
        """ Stores a user's name and associates it with their ID - also updates UI based on this info """
        self.socket.users[user_id] = User(user_id, name)
        return

    def get_user_name(self, user_id):
        return self.socket.users[user_id].get_name()

    def remove_user(self, user_id):
        if user_id in self.socket.users:
            del self.socket.users[user_id]
        return

    def set_user_typing(self, user_id, flag):
        """ Flags whether a user is typing a new codelet or not """
        self.socket.users[user_id].set_is_typing(flag)
        return

    def increase_font_size(self, event=None):
        font = tkFont.nametofont("CodeFont")
        size = min(font.actual()["size"]+2, 28)
        font.configure(size=size)
        self.sharedspace.redraw()
        return "break"

    def decrease_font_size(self, event=None):
        font = tkFont.nametofont("CodeFont")
        size = max(font.actual()["size"]-2, 8)
        font.configure(size=size)
        self.sharedspace.redraw()
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
        self._mouse_in_codebox_flag = bool(active)
        return