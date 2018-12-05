from __future__ import absolute_import, print_function

from ...utils import *
from ..tkimport import Tk

class CodeBox:
    padx = 10
    pady = 10
    bordersize = 4
    def __init__(self, parent, codelet):
        self.parent = parent # pub_main
        self.root   = parent.parent # client_app

        self.id = None # Used by canvas
        self.bg = None
        
        self.codelet = codelet

        self.parent.canvas.add(self)
        self.parent.canvas.redraw()

    def get_text(self):
        return self.codelet.get_text()

    def get_colour(self):
        """ Returns the appropriate background colour based on the state of the codelet """
        if self.codelet.is_being_edited():
            colour = GET_DISABLED_COLOUR()
        elif self.codelet.has_error():
            colour = GET_ERROR_COLOUR()
        else:
            colour = GET_USER_COLOUR(self.codelet.get_user_id())
        if self.codelet.is_hidden():
            colour = avg_colour(colour, "#d3d3d3", 0.75)
        return colour

    def get_font_colour(self):
        """ Returns the appropriate font colour based on the state of the codelet """
        if self.codelet.is_being_edited():
            return GET_DISABLED_FONT_COLOUR()
        elif self.codelet.has_error():
            return GET_ERROR_FONT_COLOUR()
        else:
            return GET_USER_FONT_COLOUR(self.codelet.get_user_id())
        return

    def get_user_colour(self):
        """ Returns the colour of the user editing this codebox - Black if not being edited """
        if self.codelet.is_being_edited():
            return GET_USER_COLOUR(self.codelet.get_editor())
        else:
            return "Black"
        return

    def get_outline_colour(self):
        if self.codelet.is_highlighted():
            return "White"
        else:
            return self.get_user_colour()
        return

    def get_highlight_colour(self):
        """ Returns the colour for textbox highlting, white if not currently editing """
        if self.root.disable_codelet_highlight():
            return self.get_user_colour()
        else:
            return "White"
        return

    def text_tag(self):
        return "tag_{}_text".format(self.codelet.get_id())

    def bg_tag(self):
        return "tag_{}_bg".format(self.codelet.get_id())

    def update(self, user_id, string, order_number):
        """ Called when a codelet is pushed with an existing ID """
        self.codelet.update(user_id, string, order_number)
        self.codelet.unassign_editor()
        self.parent.canvas.redraw()
        return

    def draw(self, x_pos, y_pos):
        """ Draws the codebox to fit, returns the dimensions """

        canvas = self.parent.canvas # for easier reference

        # Draw text -- not possible to do syntax highlighting?
        
        self.id = int(canvas.create_text(x_pos + self.padx, y_pos + self.pady, 
            anchor=Tk.NW, 
            text=self.get_text(),
            width=canvas.get_width() - (self.padx * 2), 
            tags=self.text_tag(),
            font=self.root.font,
            fill=self.get_font_colour())
        )

        # Work out height of text

        bounds = canvas.bbox(self.id) 

        # Draw background

        self.bg = int(canvas.create_rectangle([bounds[0] - self.padx, bounds[1] - self.pady, canvas.get_width(), bounds[3] + self.pady], 
            fill=self.get_colour(), 
            tag=self.bg_tag(),
            outline=self.get_outline_colour(),
            width=self.bordersize)
        )

        bounds = canvas.bbox(self.bg)

        width  = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]

        # Make sure background is lower than text

        canvas.tag_lower(self.bg, self.id)

        # Add callback bindings

        try:

            for item in (self.id, self.bg):

                self.parent.canvas.tag_bind(item, "<ButtonPress-1>", self.on_click)
                self.parent.canvas.tag_bind(item, "<Enter>", self.on_enter)
                self.parent.canvas.tag_bind(item, "<Leave>", self.on_leave)

        except Tk.TclError as e:

            print("BG: {}, ID: {}".format(self.bg, self.id))
            raise(e)
        
        return width, height

    def clear(self):
        if self.id is not None:
            self.parent.canvas.delete(self.id)
            self.parent.canvas.delete(self.bg)
        return
        
    def on_click(self, event=None):
        self.root.codelet_on_click(self.codelet.get_id())
        self.de_highlight()
        return

    def on_enter(self, event=None): # could use this instead of active colour?
        # if not currently editing
        if not self.root.disable_codelet_highlight():
            self.highlight()
            self.root.root.config(cursor=self.root.get_active_cursor_icon())
        else:
            self.root.root.config(cursor=self.root.get_cursor_icon())
        self.root.set_mouse_in_codebox(True)
        return

    def on_leave(self, event=None):
        # if not currently editing
        if not self.root.disable_codelet_highlight():
            self.de_highlight()
        self.root.root.config(cursor=self.root.get_cursor_icon())
        self.root.set_mouse_in_codebox(False)
        return

    def get_order_id(self):
        return self.codelet.get_order_id()

    def evaluate_history(self):
        """ Iterates over each item in the codelet's history and evaluates it """
        for user_id, string in self.get_history():

            self.root.evaluate(string)

        return

    def get_codelet(self):
        return self.codelet

    def bbox(self):
        return self.parent.canvas.bbox(self.bg)

    def in_view(self):
        """ Returns True if the code box is fully in view of the canvas """
        
        bbox = self.bbox()
        area = self.parent.canvas.get_visible_area()

        y1, y2 = bbox[1], bbox[3]
        v1, v2 = area[1], area[3]

        return (y1 > v1 and y2 < v2)

    # Higher level codelet methods

    def assign_editor(self, user_id):
        """ Flags the codelet as being edited by another user """
        self.codelet.assign_editor(user_id)
        return

    def unassign_editor(self):
        self.codelet.unassign_editor()
        return

    def is_being_edited(self):
        return self.codelet.is_being_edited()

    def get_id(self):
        return self.codelet.get_id()

    def get_user_id(self):
        return self.codelet.get_user_id()

    def get_history(self):
        return self.codelet.get_history()

    def load_history(self, data):
        return self.codelet.load_history(data)

    def flag_error(self):
        return self.codelet.flag_error()

    def has_error(self):
        return  self.codelet.has_error()

    def is_visible(self):
        return (not self.is_hidden() or self.parent.canvas._switch_view_hidden is True)

    def is_hidden(self):
        return self.codelet.is_hidden()

    def hide(self):
        return self.codelet.hide()

    def un_hide(self):
        return self.codelet.un_hide()

    def highlight(self):
        """ Calls de_highlight on all codelets then highlights this one """
        for codelet in self.parent.canvas.ordered():
            codelet.de_highlight()
        self.codelet.highlight()
        self.root.highlighted_codelet = self.codelet.id
        self.parent.canvas.itemconfig(self.bg, outline=self.get_outline_colour())
        return 

    def de_highlight(self):
        self.codelet.de_highlight()
        self.root.highlighted_codelet = NULL
        self.parent.canvas.itemconfig(self.bg, outline=self.get_outline_colour())
        return 
