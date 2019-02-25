from __future__ import absolute_import, print_function

from ..tkimport import Tk
from ...utils import CONTROL_KEY

class Console(Tk.Text):
    """docstring for TextInput"""
    def __init__(self, *args, **kwargs):
        Tk.Text.__init__(self, *args, **kwargs)
        self.config(bg="black", height=10) # w = 50
        self.text_colour = "console"
        self.tag_config(self.text_colour, foreground="white")
        self.bind("<{}-c>".format(CONTROL_KEY), self.copy)
        self.disable()

    def write(self, string):
        """ Print to console """
        self.enable()
        self.insert(Tk.END, string + "\n", self.text_colour)
        self.see(Tk.END)
        self.disable()
        return

    def insert_user_update(self, user, text):
        self.enable()
        self.tag_config(user.tag(), foreground=user.get_colour())
        self.insert(Tk.END, user.get_name(), user.tag())
        self.insert(Tk.END, " {}\n".format(text), self.text_colour)
        self.see(Tk.END)
        self.disable()
        return

    def copy(self, *args):
        self.enable()
        self.event_generate("<<Copy>>")
        self.disable()
        return

    def disable(self):
        return self.config(state=Tk.DISABLED)

    def enable(self):
        return self.config(state=Tk.NORMAL)

    def flush(self, *args, **kwargs):
        """ Overriden sys.stdout method """
        return
        
    def get_text(self):
        """ Returns the contents of the text box """
        return self.get(1.0, Tk.END)

    def set_text(self, text):
        """ Sets the contents of the text box """
        self.clear()
        self.insert("1.0", text)
        return

    def clear(self):
        """ Deletes the contents of the text box """
        self.delete(1.0, Tk.END)
        return