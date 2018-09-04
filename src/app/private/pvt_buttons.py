from __future__ import absolute_import, print_function
from ..tkimport import Tk

class CommandButtons(Tk.Frame):
    """docstring for TextInput"""
    def __init__(self, parent, commands):
        
        Tk.Frame.__init__(self, parent)
        self.config(width=5, height=25)

        self.num_buttons = 0

        self.commands = commands
        self.names    = list(commands.keys())

        self.button = {}

        for i, name in enumerate(self.names):

            self.button[name] = Button(self, text=name, borderwidth=1, command=self.commands[name]) # Maybe use a label
            self.button[name].grid(row=0, column=self.num_buttons, padx=4)
            self.num_buttons += 1


class Button(Tk.Button):
    def __init__(self, *args, **kwargs):
        Tk.Button.__init__(self, *args, **kwargs)
        self.config(relief=Tk.RAISED)
        self._switch = False

    def toggle(self):
        if self._switch is True:
            self._switch = False
            self.config(relief=Tk.RAISED)
        else:
            self._switch = True
            self.config(relief=Tk.SUNKEN)
        return

