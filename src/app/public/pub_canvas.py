from __future__ import absolute_import, print_function

from ..tkimport import Tk

class SharedCanvas(Tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        Tk.Canvas.__init__(self, self.parent, **kwargs)
        self._switch_view_hidden = False
        self.codeboxes = []
        
        self.padx = 10
        self.pady = 10

        self._scrollable_region = None

        self.bind("<Configure>", lambda e: self.parent.redraw())

    def add(self, codebox):
        self.codeboxes.append(codebox)
        return

    def toggle_view_hidden(self):
        self._switch_view_hidden = not self._switch_view_hidden

    def ordered(self):
        """ Returns the codeboxes in order of top to bottom """
        return sorted(self.codeboxes, key=lambda x: x.get_order_id(), reverse=True)

    def visible_codelets(self):
        return [codebox for codebox in self.ordered() if codebox.is_visible()]

    def redraw(self):
        """ Redraws all the codebox labels in order of most recently edited """

        y = 0
        for codebox in self.ordered():
            
            # Clear screen
            codebox.clear()

            # Re-draw if not hidden or showing all hidden
            if not codebox.is_hidden() or self._switch_view_hidden is True:
            
                # Re-draw
                w, h = codebox.draw(self.padx, self.pady + y)
                y = y + h + self.pady

        # Update the scrollable region when re-drawing

        bbox = self.bbox(Tk.ALL)

        if bbox is not None:

            # Add padding to scrollable region

            x1, y1, x2, y2 = bbox

            self._scrollable_region = (x1, y1 - self.pady, x2, y2 + self.pady)

        else:

            self._scrollable_region = None
                
        return

    def get_width(self):
        return self.winfo_width() - self.padx

    def get_height(self):
        bbox = self._scrollable_region
        if bbox is None:
            height = self.winfo_height()
        else:
            height = bbox[3] - bbox[1]
        return height

    def get_scrollable_region(self):
        return self._scrollable_region

    def get_visible_area(self, event=None):
        x1 = self.canvasx(0)
        y1 = self.canvasy(0)
        x2 = self.canvasx(self.winfo_width())
        y2 = self.canvasy(self.winfo_height())
        return (x1,y1,x2,y2)
