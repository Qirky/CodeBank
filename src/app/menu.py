from __future__ import absolute_import, print_function
from .tkimport import Tk
from .. utils import CONTROL_KEY

class MenuBar(Tk.Menu):
    def __init__(self, parent):
        self.parent = parent
        Tk.Menu.__init__(self, self.parent.root)

        # File menu

        filemenu =  Tk.Menu(self, tearoff=0)
        filemenu.add_command(label="Connect to server", command=self.parent.init_connection, accelerator="Ctrl+N")
        filemenu.add_command(label="Adjust clock nudge", command=self.parent.show_clock_nudge_popup, accelerator="Ctrl+K")
        self.add_cascade(label="File", menu=filemenu)        

        # Edit

        editmenu = Tk.Menu(self, tearoff=0)
        editmenu.add_command(label="Increase font size", command=self.parent.increase_font_size, accelerator="Ctrl+=")
        editmenu.add_command(label="Decrease font size", command=self.parent.decrease_font_size, accelerator="Ctrl+-")
        editmenu.add_separator()
        editmenu.add_command(label="Hide all codelets",  command=self.parent.hide_all_codelets)
        self.add_cascade(label="Edit",  menu=editmenu)

        # Actions

        actionmenu = Tk.Menu(self, tearoff=0)
        actionmenu.add_command(label="Push code to remote", command=self.parent.push_code_to_remote, accelerator="Ctrl+Shift+Enter")
        actionmenu.add_command(label="Solo local code", command=self.parent.solo_local_code)
        actionmenu.add_command(label="Reset program state", command=self.parent.reset_program_state)
        actionmenu.add_command(label="Rollback codelet history", command=self.parent.trigger_rollback)
        actionmenu.add_command(label="Hide codelet", command=self.parent.trigger_hide_codelet)
        actionmenu.add_command(label="Toggle hidden codelet visibility", command=self.parent.toggle_view_hidden)
        actionmenu.add_separator()
        actionmenu.add_command(label="Clear clock", command=self.parent.send_clear_clock_message, accelerator="Ctrl+>")
        # actionmenu.add_command(label="", command="", accelerator="")
        self.add_cascade(label="Action", menu=actionmenu)