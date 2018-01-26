from ..tkimport import Tk

class SharedCanvas(Tk.Canvas):
    def __init__(self, parent, *args, **kwargs):
        Tk.Canvas.__init__(self, *args, **kwargs)
        self.parent = parent
        self.codeboxes = []
        self.padx = 10
        self.pady = 10

        self.bind("<Configure>", lambda e: self.redraw())

    def add(self, codebox):
        self.codeboxes.append(codebox)
        return

    def redraw(self):
        """ Redraws all the codebox labels in order of most recently edited """
        ordered = sorted(self.codeboxes, key=lambda x: x.order_number, reverse=True)
        y = 0
        for codebox in ordered:
            # Re-draw
            w, h = codebox.draw(self.padx, self.pady + y)
            y = y + h + self.pady
            
        return

    def get_width(self):
        return self.winfo_width() - self.padx