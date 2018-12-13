from __future__ import absolute_import, print_function
from .main import *

class ClockNudgePopup:
    def __init__(self, parent):
        
        # Reference to App
        self.parent = parent

        # Create  new window
        self.top=Tk.Toplevel(parent.root)
        self.top.title("Set Clock Nudge")

        # Storing the nudge value

        self.value = self.parent.nudge
        self.inc   = 0.01

        # Label with information

        lbl = Tk.Label(self.top, text="Use the buttons to change the Clock nudge value", font=self.parent.font)
        lbl.grid(row=0, column=0, columnspan=4)

        # Buttons for changing nudge value


        self.button = (
            Tk.Button(self.top, text="<-", command=self.decrease, font=self.parent.font), 
            Tk.Button(self.top, text="->", command=self.increase, font=self.parent.font)
            )

        self.button[0].grid(row=1, column=0, sticky=Tk.NSEW)
        self.button[1].grid(row=1, column=3, sticky=Tk.NSEW)

        # Label for displaying nudge

        self.str_value = Tk.StringVar()
        self.display = Tk.Label(self.top, textvariable=self.str_value, font=self.parent.font)

        self.display.grid(row=1, column=1, columnspan=2, sticky=Tk.NSEW)

        # Reset button

        self.ok = Tk.Button(self.top, text="OK", command = self.set_value, font=self.parent.font)
        self.ok.grid(row=3, column=0, columnspan=2, sticky=Tk.NSEW)

        self.reset = Tk.Button(self.top, text="Reset", command = self.cleanup, font=self.parent.font)
        self.reset.grid(row=3, column=2, columnspan=2, sticky=Tk.NSEW)
        
        # Start

        self.update_display()
        self.center()

    def update_display(self):
        self.str_value.set("{:.2f}".format(self.value))
        return

    def cleanup(self, event=None):
        self.value = None
        self.top.destroy()
        return

    def set_value(self, event=None):
        self.top.destroy()
        return

    def increase(self, event=None):
        self.value += self.inc
        self.update_nudge()
        self.update_display()
        return

    def decrease(self, event=None):
        self.value -= self.inc
        self.update_nudge()
        self.update_display()
        return

    def update_nudge(self):
        self.parent.evaluate("Clock.nudge = {}".format(self.value), verbose=False)
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