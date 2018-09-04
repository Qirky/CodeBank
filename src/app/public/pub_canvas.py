from __future__ import absolute_import, print_function

from ..tkimport import Tk

class SharedCanvas(Tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        Tk.Canvas.__init__(self, *args, **kwargs)
        self.parent = parent
        self._switch_view_hidden = False
        self.codeboxes = []
        self.padx = 10
        self.pady = 10

        self.bind("<Configure>", lambda e: self.redraw())

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
                
        return

    def get_width(self):
        return self.winfo_width() - self.padx
