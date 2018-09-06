from __future__ import absolute_import, print_function

from ...utils import *
from ..tkimport import Tk
from .pvt_text import TextInput
from .pvt_buttons import CommandButtons
from .pvt_console import Console
import sys

class Workspace(Tk.Frame):
    def __init__(self, parent):
        Tk.Frame.__init__(self, parent.root)
        
        self.parent = parent
        self.config(height=100)

        # Buttons

        self.commands = CommandButtons(self, commands={
                "PUSH"          : self.parent.push_code_to_remote,
                "SOLO"          : self.parent.solo_local_code,
                "RESET"         : self.parent.reset_program_state,
                "ROLLBACK"      : self.parent.trigger_rollback,
                "HIDE"          : self.parent.trigger_hide_codelet,
                "TOGGLE HIDDEN" : self.parent.toggle_view_hidden,
                "CLEAR CLOCK"   : self.parent.clear_clock,
            }
        )

        # Make sure widgets expand
        Tk.Grid.columnconfigure(self, 0, weight=1)
        Tk.Grid.columnconfigure(self, 1, weight=1)
        Tk.Grid.rowconfigure(self, 1, weight=1)

        self.commands.grid(row=0, column=0, sticky=Tk.W)

        # Textbox

        self.container = Tk.Frame(self, height=250, width=0)
        self.container.grid(row=1, column=0, sticky=Tk.NSEW)
        self.container.grid_propagate(False)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.text = TextInput(self.container, main=self, font=self.parent.font)
        self.text.grid(row=0, column=0, sticky=Tk.NSEW)

        self.text.bind("<{}-Return>".format(CONTROL_KEY),       self.evaluate_code_locally)
        self.text.bind("<{}-Shift-Return>".format(CONTROL_KEY), self.push_code_to_remote)

        self.text.bind("<{}-equal>".format(CONTROL_KEY), self.parent.increase_font_size)
        self.text.bind("<{}-minus>".format(CONTROL_KEY), self.parent.decrease_font_size)

        # Canvas bindings

        self.text.bind("<Alt-Up>", self.parent.highlight_codelet_up)
        self.text.bind("<Alt-Down>", self.parent.highlight_codelet_down)

        # Console

        self.c_container = Tk.Frame(self)
        self.c_container.grid(row=1, column=1, sticky=Tk.NSEW)
        self.c_container.grid_propagate(False)
        self.c_container.grid_rowconfigure(0, weight=1)
        self.c_container.grid_columnconfigure(0, weight=1)

        self.console = Console(self.c_container, font=self.parent.font)
        self.console.grid(row=0, column=0, sticky=Tk.NSEW)

        sys.stdout = self.console # routes stdout to print to console

        self.y_scroll = Tk.Scrollbar(self.parent.root)
        self.y_scroll.config(command=self.console.yview, orient=Tk.VERTICAL)
        self.y_scroll.grid(row=2, column=2, sticky=Tk.NSEW)

        self.console.config(
            yscrollcommand=self.y_scroll.set,
            )

        # Placeholders for sending data to/from the server

        self.socket = None

    # Methods for connecting and sending data to sockets

    def set_connection(self, conn):
        """ Connects to the remote and imports foxdot """
        self.socket = conn
        return

    def clear(self):
        """ Deletes the contents of the text box and sets current_codelet to None """
        self.text.clear()
        self.parent.set_codelet_id(NULL)
        return

    def load_from_codelet(self, codelet_id):
        """ Takes a codelet id and loads the current text into the text box """
        codelet = self.parent.sharedspace.codelets[codelet_id]
        self.parent.set_codelet_id(codelet_id)
        self.text.set_text(codelet.get_text().strip())
        return

    # Methods for running code

    def evaluate_code_locally(self, event=None):
        """ Runs code in the text box immediately without pushing to the remote """

        self.text.highlight()

        code = self.text.get_text()

        self.parent.evaluate(code)

        return "break"

    def push_code_to_remote(self, event=None):
        """ Clears the txt box and sends code to server """

        self.parent.push_code_to_remote()

        return "break"
