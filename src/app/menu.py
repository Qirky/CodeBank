from .tkimport import Tk

class MenuBar(Tk.Menu):
    def __init__(self, parent):
        self.parent = parent
        Tk.Menu.__init__(self, self.parent.root)

        # File menu

        filemenu =  Tk.Menu(self, tearoff=0)
        filemenu.add_command(label="Connect to server", command=self.parent.init_connection)
        self.add_cascade(label="File", menu=filemenu)        
