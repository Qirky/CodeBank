from __future__ import absolute_import, print_function
from .tkimport import Tk
from .. utils import CONTROL_KEY

class MenuBar(Tk.Menu):
    def __init__(self, parent):
        self.parent = parent
        Tk.Menu.__init__(self, self.parent.root)

        # File menu

        filemenu =  Tk.Menu(self, tearoff=0)
        filemenu.add_command(label="Connect to server", command=self.parent.init_connection)
        filemenu.add_command(label="Increase font size", command=self.parent.increase_font_size, accelerator="Ctrl+=")
        filemenu.add_command(label="Decrease font size", command=self.parent.decrease_font_size, accelerator="Ctrl=-")
        self.add_cascade(label="File", menu=filemenu)        
