from ...utils import GET_USER_COLOUR, GET_DISABLED_COLOUR
from ..tkimport import Tk

class CodeBox:
    def __init__(self, parent, codelet, order_number):
        self.parent = parent
        self.root   = parent.parent

        self.id = None # Used by canvas
        self.bg = None
        
        self.codelet = codelet
        self.order_number = int(order_number)

        self.parent.canvas.add(self)
        self.parent.canvas.redraw()

    def get_text(self):
        return self.codelet.get_text()

    def get_colour(self):
        return GET_USER_COLOUR(self.codelet.get_user_id()) if self.codelet.editor is None else GET_DISABLED_COLOUR()

    def text_tag(self):
        return "tag_{}_text".format(self.codelet.get_id())

    def bg_tag(self):
        return "tag_{}_bg".format(self.codelet.get_id())

    def update(self, user_id, string, order_number):
        """ Called when a codelet is pushed with an existing ID """
        self.codelet.update(user_id, string)
        self.codelet.unassign_editor()
        self.order_number = order_number
        self.parent.canvas.redraw()
        return

    def draw(self, x_pos, y_pos):
        """ Draws the codebox to fit, returns the dimensions """

        # First, delete

        self.clear()

        canvas = self.parent.canvas # for easier reference

        # Draw text
        
        self.id = canvas.create_text(x_pos, y_pos, 
            anchor=Tk.NW, 
            text=self.get_text(), 
            width=canvas.get_width(), 
            tags=self.text_tag(),
            font=self.root.font)

        # Work out height of text

        bounds = canvas.bbox(self.id) 

        width  = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]

        # Draw background

        self.bg = canvas.create_rectangle([bounds[0], bounds[1], canvas.get_width(), bounds[3]], fill=self.get_colour(), tag=self.bg_tag())

        bounds = canvas.bbox(self.bg)

        width  = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]

        # Make sure background is lower than text

        canvas.tag_lower(self.bg, self.id)

        if self.codelet.editor is not None:

            pass # TODO -- give some information about the user edting that code

        # Add callback

        for item in (self.id, self.bg):

            self.parent.canvas.tag_bind(item, "<ButtonPress-1>", self.on_click)
        
        return width, height

    def clear(self):
        if self.id is not None:
            self.parent.canvas.delete(self.id)
            self.parent.canvas.delete(self.bg)
        return
        
    def on_click(self, event=None):
        self.root.codelet_on_click(self.codelet.get_id())
        return

    def get_order_id(self):
        return self.order_number

    def evaluate_history(self):
        """ Iterates over each item in the codelet's history and evaluates it """
        for user_id, string in self.get_history():

            self.root.evaluate(string)

        return

    def get_codelet(self):
        return self.codelet

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
