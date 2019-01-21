from __future__ import absolute_import, print_function

import queue

from ..tkimport import Tk
from .pub_canvas import SharedCanvas
from .pub_code_box import CodeBox
from .pub_peers import PeerBox

class SharedSpace(Tk.Frame):
    def __init__(self, parent):
        # Create a single frame to hold the representations of code chunks
        self.parent = parent

        # Codelet / codebox information

        self.codelets = {}

        if self.parent.visible:

            Tk.Frame.__init__(self, self.parent.root)

            # Canvas and y-scroll
            self.canvas = SharedCanvas(self, width=640, height=480, bg="gray")

            self.y_scroll = Tk.Scrollbar(self)
            self.y_scroll.config(command=self.canvas.yview, orient=Tk.VERTICAL)

            self.canvas.config(
                yscrollcommand=self.y_scroll.set,
                scrollregion=self.canvas.bbox(Tk.ALL)
                )


            self.drag = Tk.Frame(self, bg="white", width=5, cursor="sb_h_double_arrow")
            self.drag.bind("<Button-1>",        self.drag_mouseclick)        
            self.drag.bind("<ButtonRelease-1>", self.drag_mouserelease)
            self.drag.bind("<B1-Motion>",       self.drag_mousedrag)

            self.drag_mouse_down = False

            # Scroll binds for canvas (button 4/5 is for Linux)

            self.mouse_scroll = MouseScroll(self)
            self.parent.root.bind("<MouseWheel>", self.mouse_scroll)
            self.parent.root.bind("<Button-4>",   self.mouse_scroll)
            self.parent.root.bind("<Button-5>",   self.mouse_scroll)

            # Peers list

            self.peer_box = PeerBox(self)

            # Only expand canvas

            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)

            # Grid

            self.padding = Tk.Frame(self, bg="white", width=5)
            
            self.canvas.grid(row=0, column=0, sticky=Tk.NSEW)
            self.drag.grid(row=0, column=1, sticky=Tk.NSEW)
            self.peer_box.grid(row=0, column=2, sticky=Tk.NSEW)
            self.peer_box.grid_propagate(False) # this is interesting
            self.padding.grid(row=0, column=3, sticky=Tk.NSEW)
            self.y_scroll.grid(row=0, column=4, sticky=Tk.NSEW)

            # Thread safe redraw queue
            self.queue = queue.Queue()
            self.poll_queue()

    def add_codelet(self, codelet):
        """ Adds a new codelet to the canvas wrapped in a CodeBox instance """
        self.codelets[codelet.id] = CodeBox(self, codelet)
        return

    def redraw(self):
        """ Schedules a redraw the canvas and update the scroll region that is thread-safe """
        if self.parent.visible:
            self.queue.put(self._thread_safe_redraw)
        return
    
    def _thread_safe_redraw(self):
        """ Canvas redraw functions to be called without race conditions """
        self.canvas.redraw()
        self.canvas.config(scrollregion=self.canvas.get_scrollable_region())
        return

    def poll_queue(self):
        """ Recursive call to poll the redraw queue and safely redraw the canvas """
        try:

            while True:
                
                func = self.queue.get_nowait()
                func.__call__()

        # Break the loop when the queue is empty        
        except queue.Empty:
            pass

        # Call ~33 times a second
        self.after(30, self.poll_queue)
        return

    def drag_mouseclick(self, event=None):
        """ Flags the mouse as clicked for drag action """
        self.drag_mouse_down = True
        self.grid_propagate(False)
        return

    def drag_mouserelease(self, event=None):
        """ Flags the mouse has been released and gives focus to the app.text if it exists """
        self.drag_mouse_down = False
        
        if self.parent.text is not None:
        
            self.parent.text.focus_set()
        
        return

    def drag_mousedrag(self, event=None):
        """ Resizes the canvas and listbox """

        if self.drag_mouse_down:

            delta = (self.drag.winfo_rootx() - event.x_root)

            self.peer_box.config(width=self.peer_box.winfo_width() + delta)
            self.canvas.config(width=self.canvas.winfo_width() - delta)

            return "break"

        return

    def is_scrollable(self):
        """ Returns True if the canvas get_height() - height of codeboxes - is greater than
            the height of the widget itself, i.e. should be scrollable."""
        return self.canvas.get_height() > self.canvas.winfo_height()

    def add_new_chat_message(self, user_id, message):
        """ Gets the user object and triggers new message """
        if self.parent.visible:
            user = self.parent.users[user_id]
            self.peer_box.add_chat_message(user, message)
        return


class MouseScroll:
    def __init__(self, parent):
        self.parent = parent
    def delta(self, event):
        if event.num == 5 or event.delta < 0:
            return 1 
        return -1
    def __call__(self, event):
        if self.parent.is_scrollable():
            delta = self.delta(event)
            self.parent.canvas.yview_scroll(delta, "units")
