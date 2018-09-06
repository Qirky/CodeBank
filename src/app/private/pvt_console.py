from __future__ import absolute_import, print_function

from ..tkimport import Tk

class Console(Tk.Text):
    """docstring for TextInput"""
    def __init__(self, *args, **kwargs):
        Tk.Text.__init__(self, *args, **kwargs)
        self.config(bg="black", height=10) # w = 50
        self.tag_config("console", foreground="white")
        self.disable()

    def write(self, string):
        """ Print to console """
        self.enable()
        self.insert(Tk.END, string, "console")
        self.see(Tk.END)
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