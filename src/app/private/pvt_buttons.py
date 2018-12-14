from __future__ import absolute_import, print_function
from ..tkimport import Tk

class CommandButtons(Tk.Frame):
    """docstring for TextInput"""
    def __init__(self, parent, commands):

        Tk.Frame.__init__(self, parent)

        self.height = 25
    
        self.config(width=5, height=self.height, cursor="sb_v_double_arrow")

        self.parent = parent
        self.commands = commands

        self.buttons = {}
        self.num_buttons = 0

        for cmd in self.commands:

            self.buttons[cmd.name] = Button(self, cmd, cursor="hand2")
            self.buttons[cmd.name].grid(row=0, column=self.num_buttons, padx=4)
            self.num_buttons += 1

        self.bind("<Button-1>",        self.parent.drag_mouseclick)
        self.bind("<ButtonRelease-1>", self.parent.drag_mouserelease)
        self.bind("<B1-Motion>",       self.parent.drag_mousedrag)

        # Add text for chatting

        self.chat_column_span = 4

        self.chat_container = Tk.Frame(self, height=self.height)
        self.chat_container.grid_propagate(False)
        self.chat_container.grid(row=0, column=self.num_buttons, columnspan=self.chat_column_span, sticky=Tk.NSEW)

        # Make chat box expand

        self.grid_columnconfigure(self.num_buttons, weight=1)
        self.chat_container.grid_columnconfigure(0, weight=1)
        self.chat_container.grid_rowconfigure(0, weight=1) 
        # self.chat_container.grid_columnconfigure(1, weight=1)

        self.chat_text = Tk.Text(self.chat_container, height=1, width=20, font=self.parent.font)
        self.chat_text.grid(row=0, column=0, sticky=Tk.NSEW)
        self.chat_text.bind("<Return>", self.send_chat_message)
        self.chat_text.bind("<Escape>", lambda e: self.parent.text.focus_set())
        self.chat_text.bind("<Tab>", lambda e: self.parent.text.focus_set())
        self.chat_text.bind("<Home>", lambda e: self.chat_text.see("1.0"))
        self.chat_text.bind("<End>",  lambda e: self.chat_text.see(Tk.END))

        self.num_buttons += self.chat_column_span
        
        self.chat_send = Tk.Button(self, text=" SEND ", cursor="hand2", command=self.send_chat_message)
        self.chat_send.grid(row=0, column=self.num_buttons, sticky=Tk.NSEW)

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

    def disable_chat(self):
        self.chat_text.config(state=Tk.DISABLED, bg="#b3b3b3")
        self.chat_send.config(state=Tk.DISABLED)
        return

    def enable_chat(self):
        self.chat_text.config(state=Tk.NORMAL, bg="white")
        self.chat_send.config(state=Tk.NORMAL)
        return

    def send_chat_message(self, event=None):
        text = self.chat_text.get("1.0", Tk.END).strip()
        if len(text):
            self.chat_text.delete("1.0", Tk.END)
            self.parent.send_chat_message(text)
        return "break"

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