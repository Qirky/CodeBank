from __future__ import absolute_import, print_function
from .main import *
from ..interpreter import LANGUAGE_NAMES

class popup_window:
    def __init__(self, master, title=""):
        top=self.top=Tk.Toplevel(master)
        self.top.title(title)
        # Host
        lbl = Tk.Label(top, text="Host:")
        lbl.grid(row=0, column=0, stick=Tk.W)
        self.host=Tk.Entry(top)
        self.host.grid(row=0, column=1, sticky=Tk.NSEW)
        
        # Name
        lbl = Tk.Label(top, text="Name:")
        lbl.grid(row=1, column=0, sticky=Tk.W)
        self.name=Tk.Entry(top)
        self.name.grid(row=1, column=1, sticky=Tk.NSEW)
        
        # Password
        lbl = Tk.Label(top, text="Password: ")
        lbl.grid(row=2, column=0, sticky=Tk.W)
        self.password=Tk.Entry(top, show="*")
        self.password.grid(row=2, column=1, sticky=Tk.NSEW)
        
        # Interpreter
        options = list(LANGUAGE_NAMES.keys())

        lbl = Tk.Label(top, text="Language: ")
        lbl.grid(row=3, column=0, sticky=Tk.W)
        self.lang = Tk.StringVar(top)
        self.lang.set(options[0])
        self.drop = Tk.OptionMenu(top, self.lang, *options)
        self.drop.grid(row=3, column=1, sticky=Tk.NSEW)
        
        # Ok button
        self.button=Tk.Button(top,text='Ok',command=self.cleanup)
        self.button.grid(row=4, column=0, columnspan=2, sticky=Tk.NSEW)
        
        # Value
        self.value = None
       
        # Enter shortcut
        self.top.bind("<Return>", self.cleanup)
        
        # Start
        self.center()

    def cleanup(self, event=None):
        """ Stores the data in the entry fields then closes the window """
        host = self.host.get()
        port = 57890 ## TODO - get this from somewhere else
        name = self.name.get()
        password = self.password.get()
        lang = LANGUAGE_NAMES[self.lang.get()]
        if name.strip() != "" and host.strip() != "":
            self.value = (host, port, name, password, lang)
            self.top.destroy()
        return

    def center(self):
        """ Centers the popup in the middle of the screen """
        self.top.update_idletasks()
        w = self.top.winfo_screenwidth()
        h = self.top.winfo_screenheight()
        size = tuple(int(_) for _ in self.top.geometry().split('+')[0].split('x'))
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        self.top.geometry("%dx%d+%d+%d" % (size + (x, y)))
        return