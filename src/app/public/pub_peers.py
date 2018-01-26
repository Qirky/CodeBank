from ...utils import GET_USER_COLOUR
from ..tkimport import Tk

class PeerBox(Tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        Tk.Frame.__init__(self, *args, **kwargs)
        
        self.parent = parent

        # List

        self.listbox = Tk.Listbox(self, width=20, bg="White", font=self.parent.parent.font)
        
        self.listbox.grid(row=0, column=1, sticky=Tk.NSEW)

        self.listbox.bind("<Button-1>", lambda e: "break")
        self.listbox.bind("<B1-Motion>", lambda e: "break")

        Tk.Grid.rowconfigure(self, 0, weight=1) # Expans

        self.users = {}    

    def refresh(self):
        """ Clears the user list and redraws  """
        
        self.listbox.delete(0, Tk.END)
        
        i = 0

        for user_id, name in self.users.items():
            
            self.listbox.insert(Tk.END, name)

            self.listbox.itemconfig(i, {'bg': GET_USER_COLOUR(user_id)})

            i += 1

        return

    def add_user(self, user_id, name):
        """ Adds a user to the directory and redraws """
        self.users[user_id] = name
        self.refresh()
        return

    def remove_user(self, user_id):
        """ Removes a user from the directory and redraws """
        del self.users[user_id]
        self.refresh()
        return
