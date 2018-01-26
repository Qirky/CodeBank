from ..tkimport import Tk

class TextInput(Tk.Text):
    """docstring for TextInput"""
    def __init__(self, *args, **kwargs):
        Tk.Text.__init__(self, *args, **kwargs)
        
    def get_text(self):
        """ Returns the contents of the text box """
        return self.get(1.0, Tk.END)

    def set_text(self, text):
        """ Sets the contents of the text box """
        self.clear()
        self.insert("1.0", text)
        return

    def clear(self):
        """ Deletes the contents of the text box """
        self.delete(1.0, Tk.END)
        return