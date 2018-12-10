from __future__ import absolute_import, print_function
from ..tkimport import Tk

class CommandButtons(Tk.Frame):
    """docstring for TextInput"""
    def __init__(self, parent, commands):
        
        Tk.Frame.__init__(self, parent)
        self.config(width=5, height=25, cursor="sb_v_double_arrow")

        self.parent = parent
        self.commands = commands

        self.buttons = {}
        self.num_buttons = 0

        for cmd in self.commands:

            self.buttons[cmd.name] = Button(self, cmd, cursor="hand2")
            self.buttons[cmd.name].grid(row=0, column=self.num_buttons, padx=4)
            self.num_buttons += 1

        self.bind("<Double-Button-1>", self.parent.drag_mouseclick)
        self.bind("<ButtonRelease-1>", self.parent.drag_mouserelease)
        self.bind("<B1-Motion>",       self.parent.drag_mousedrag)

        self.unbind("<Button-1>")

        self.set_to_equal_size() # better or not?

    def __getitem__(self, key):
        return self.buttons[key]

    def set_to_equal_size(self):
        max_size = max([len(cmd) for cmd in self.buttons]) + 2 # leave space
        for button in self.buttons.values():
            button.config(width = max_size)
        return

    def disable_all(self):
        for button in self.buttons.values():
            button.disable()
        return

    def enable_all(self):
        for button in self.buttons.values():
            button.enable()
        return

    def default_all(self):
        for button in self.buttons.values():
            button.set_to_default()
        return

class Button(Tk.Button):
    def __init__(self, master, command, *args, **kwargs):
        Tk.Button.__init__(self, master, *args, **kwargs)
        self.default_state = command.default_state
        self.config( relief=Tk.RAISED,
                     text=command.name, 
                     borderwidth=1, 
                     command=command.command) # Maybe use a label
        self._switch = False

    def disable(self):
        self.config(state=Tk.DISABLED)
        return

    def enable(self):
        self.config(state=Tk.NORMAL)
        return

    def set_to_default(self):
        self.config(state=self.default_state)
        return

    def toggle(self):
        if self._switch is True:
            self._switch = False
            self.config(relief=Tk.RAISED)
        else:
            self._switch = True
            self.config(relief=Tk.SUNKEN)
        return

class CmdButton:
    """ Abstraction for button behaviour """
    def __init__(self, name, func, default=Tk.NORMAL):
        self.name     = name.upper()
        self.command  = func
        self.default_state = default