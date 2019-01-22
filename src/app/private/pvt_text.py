from __future__ import absolute_import, print_function

from ..tkimport import Tk
from ...utils import CONTROL_KEY, NULL

class TextInput(Tk.Text):
    """docstring for TextInput"""
    def __init__(self, parent, main, *args, **kwargs):
        Tk.Text.__init__(self, parent, *args, **kwargs)
        self.parent = main # pvt_main
        self.root   = self.parent.parent # client_app
        
        self.lang   = None

        self.config(height=10, width=100)

        # Disable certain actions

        disable = lambda e: "break"

        import string

        for key in list(string.digits + string.ascii_letters) + ["slash"]:

            self.bind("<{}-{}>".format(CONTROL_KEY, key), disable)

        self.bind("<Key>",       self.keypress)
        self.bind("<Return>",    self.return_key)
        self.bind("<Delete>",    self.delete_key)
        self.bind("<Escape>",    lambda *e: self.root.reset_program_state())

        # Over-ride Key binding for undo/redo shortcuts : TODO - add to Menu

        self.bind("<{}-z>".format(CONTROL_KEY), lambda e: None)
        self.bind("<{}-y>".format(CONTROL_KEY), lambda e: None)

        self.bind("<{}-a>".format(CONTROL_KEY), self.select_all)

        self.config(undo=True, autoseparators=True, maxundo=50)

        self.key_down = False
        self.is_typing = False

    @staticmethod
    def convert_index(index1, index2=None):
        if type(index1) == str and index2 == None:
            return tuple(int(n) for n in index1.split('.'))
        return str(index1) + '.' + str(index2)

    def update_colour_map(self):
        """ Called when a language is chosen to apply syntax highlighting """
        self.lang = self.root.lang
        self.colour_map = self.lang.get_formatting()
        for tag_name in self.colour_map:
            self.tag_config(tag_name, foreground=self.colour_map[tag_name][1])
        self.tag_config("highlight", background="red", foreground="white")
        return
        
    def get_text(self):
        """ Returns the contents of the text box """
        return self.get(1.0, Tk.END).strip()

    def set_text(self, text):
        """ Sets the contents of the text box """
        self.clear()
        self.insert("1.0", text)
        self.edit_reset()
        self.update_colours()
        return

    def select_all(self, event=None):
        self.tag_add(Tk.SEL, "1.0", Tk.END)
        return "break"

    def clear(self):
        """ Deletes the contents of the text box """
        self.delete(1.0, Tk.END)
        self.edit_reset()
        self.set_typing(False)
        return

    def keypress(self, event):
        """ Inserts a character and then updates the syntax formatting """

        self.root.unhighlight_all_codelets()

        if event.keysym in ("BackSpace", "Delete"):
            
            self.edit_separator()

            # If we are deleting the last character, flag typing as False

            sel = self.delete_selection()

            if sel:

                return "break"

            elif len(self.get_text()) == 1:
        
                self.set_typing(False)
        
        elif event.char != "":
            
            if event.char == "\r":
                char = "\n"
            elif event.char == "\t":
                char = " "*4
            else:
                char = event.char
            
            index = self.index(Tk.INSERT)
            
            # if we have a selection, delete it first
            self.delete_selection()
            self.insert(index, char)
            self.update_colours()
            self.edit_separator()

            self.set_typing(True)
            
            return "break"
        
        return

    def return_key(self, event=None):
        """ If a codelet is highlighted, use PULL, if not, just use the return Key"""
        if self.root.highlighted_codelet != NULL and (not self.root.mouse_in_codebox()):
            self.root.request_codelet(self.root.highlighted_codelet)
            self.root.unhighlight_all_codelets()
            return "break"
        return

    def delete_key(self, event=None):
        """ If a codelet is highlighted, use HIDE, if not, just use the return Key"""
        if self.root.highlighted_codelet != NULL and (not self.root.mouse_in_codebox()):
            self.root.send_hide_codelet(self.root.highlighted_codelet)
            self.root.unhighlight_all_codelets()
            return "break"
        return

    def highlight(self):
        """ Highlights a chunk of text and schedules it to un-highlight 150ms later """

        # Get start and end of the buffer
        start, end = "1.0", self.index(Tk.END)
        lastline   = int(end.split('.')[0]) + 1

        # Indicies of block to execute
        block = [0,0]        
        
        # 1. Get position of cursor
        cur_x, cur_y = [int(x) for x in self.index(Tk.INSERT).split(".")]
        
        # 2. Go through line by line (back) and see what it's value is
        
        for line in range(cur_x, 0, -1):
            if not self.get("%d.0" % line, "%d.end" % line).strip():
                break

        block[0] = line

        # 3. Iterate forwards until we get two \n\n or index==END
        for line in range(cur_x, lastline):
            if not self.get("%d.0" % line, "%d.end" % line).strip():
                break

        block[1] = line

        # Now we have the lines of code!

        a, b = block
    
        if a == b: b += 1

        for line in range(a, b):

            start = "%d.0" % line
            end   = "%d.end" % line

            # Highlight text only to last character, not whole line

            if len(self.get(start, end).strip()) > 0:

                self.tag_add("highlight", start, end)

        self.after(150, self.unhighlight)

        return 

    def unhighlight(self):
        """ Removes the highlight from text """
        return self.tag_remove("highlight", "1.0", Tk.END)

    def update_colours(self, event=None):
        this_line = self.index(Tk.INSERT)
        line, col = this_line.split(".")
        self.colour_line(line)
        return

    def colour_line(self, line):
        """ Checks a line for any tags that match regex and updates IDE colours """

        line = int(line)

        start_of_line, end_of_line = self.convert_index(line,0), self.convert_index(line,"end")

        thisline = self.get(start_of_line, end_of_line)

        try:

            # Remove tags at current point

            for tag_name in self.tag_names():

                self.tag_remove(tag_name, start_of_line, end_of_line)

            # Re-apply tags

            for tag_name, start, end in self.lang.findstyles(thisline):
                
                self.tag_add(tag_name, self.convert_index(line, start), self.convert_index(line, end))

        except Exception as e:

            print(e)

        return

    def delete_selection(self):
        """ If an area is selected, it is deleted and returns True """
        try:
            text = self.get(Tk.SEL_FIRST, Tk.SEL_LAST)
            a, b = self.index(Tk.SEL_FIRST), self.index(Tk.SEL_LAST)
            self.delete(Tk.SEL_FIRST, Tk.SEL_LAST)
            # If there is no text left, flag the user as not typing
            if len(self.get_text()) == 0:
                self.set_typing(False)
            return True        
        except Tk.TclError:
            return False


    def set_typing(self, flag):
        """ Flags the user as typing or not, and sends the information
            to the server if it has changed
        """
        # Send to the server if the internal flag has changed
        if flag != self.is_typing:
            # Only set_typing if the user is editing a new codelet
            if self.root.get_codelet_id() is NULL:
                self.parent.flag_user_typing(flag)
            self.is_typing = flag
        return