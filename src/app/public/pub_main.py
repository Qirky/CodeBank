from __future__ import absolute_import, print_function

from ..tkimport import Tk
from .pub_canvas import SharedCanvas
from .pub_code_box import CodeBox
from .pub_peers import PeerBox

class SharedSpace(Tk.Frame):
    def __init__(self, parent):
        # Create a single frame to hold the representations of code chunks
        self.parent = parent
        Tk.Frame.__init__(self, self.parent.root)

        # Canvas and y-scroll
        self.canvas = SharedCanvas(self, width=640, height=480, bg="gray")
        self.canvas.grid(row=0, column=0, sticky=Tk.NSEW)

        self.y_scroll = Tk.Scrollbar(self.parent.root)
        self.y_scroll.config(command=self.canvas.yview, orient=Tk.VERTICAL)
        self.y_scroll.grid(row=0, column=2, sticky=Tk.NSEW)

        self.canvas.config(
            yscrollcommand=self.y_scroll.set,
            scrollregion=self.canvas.bbox(Tk.ALL)
            )

        # Peers list

        self.peer_box = PeerBox(self)
        self.peer_box.grid(row=0, column=1, sticky=Tk.NSEW)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)

        # Codelet / codebox information

        self.codelets = {}

    def add_codelet(self, codelet):
        """ Adds a new codelet to the canvas wrapped in a CodeBox instance """
        self.codelets[codelet.id] = CodeBox(self, codelet)
        return

    def redraw(self):
        self.canvas.redraw()