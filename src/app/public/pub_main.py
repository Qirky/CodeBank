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

        self.y_scroll = Tk.Scrollbar(self)
        self.y_scroll.config(command=self.canvas.yview, orient=Tk.VERTICAL)

        self.canvas.config(
            yscrollcommand=self.y_scroll.set,
            scrollregion=self.canvas.bbox(Tk.ALL)
            )

        # Box for changing size - self.parent.root

        self.drag = Tk.Frame( self, bg="white", width=5, cursor="sb_h_double_arrow") # why does it need to be parent.root?
        self.drag.bind("<Button-1>",        self.drag_mouseclick)        
        self.drag.bind("<ButtonRelease-1>", self.drag_mouserelease)
        self.drag.bind("<B1-Motion>",       self.drag_mousedrag)

        self.drag_mouse_down = False

        # Peers list

        self.peer_box = PeerBox(self)

        # Only expand canvas

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Grid
        
        self.canvas.grid(row=0, column=0, sticky=Tk.NSEW)
        self.drag.grid(row=0, column=1, sticky=Tk.NSEW)
        self.peer_box.grid(row=0, column=2, sticky=Tk.NSEW)
        self.y_scroll.grid(row=0, column=3, sticky=Tk.NSEW)

        # Codelet / codebox information

        self.codelets = {}

    def add_codelet(self, codelet):
        """ Adds a new codelet to the canvas wrapped in a CodeBox instance """
        self.codelets[codelet.id] = CodeBox(self, codelet)
        return

    def redraw(self):
        self.canvas.redraw()

    def drag_mouseclick(self, event=None):
        self.drag_mouse_down = True
        self.grid_propagate(False)
        return

    def drag_mouserelease(self, event=None):
        self.drag_mouse_down = False
        # self.app.text.focus_set()
        return

    def drag_mousedrag(self, event=None):

        if self.drag_mouse_down:
            
            #line_height = self.peer_box.listbox.dlineinfo("@0,0")

            #print(line_height)

            # if textbox_line_h is not None:

            #     self.app.text.height = int(self.app.text.winfo_height() / textbox_line_h[3])
                
            # self.root_h = self.height + self.app.text.height

            # widget_y = self.canvas.winfo_rooty()

            # new_height = (self.canvas.winfo_height() + (widget_y - event.y_root) )

            # self.height, old_height = new_height, self.height

            # self.canvas.config(height = max(self.height, 50))

            return "break"

        return