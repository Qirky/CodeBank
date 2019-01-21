from __future__ import absolute_import, print_function

from ...utils import GET_USER_COLOUR, APP_TYPES
from ..tkimport import Tk

class PeerBox(Tk.Frame):
    def __init__(self, parent, *args, **kwargs):

        self.parent = parent # Is the "SharedSpace"
        self.app    = parent.parent # is the whole app

        self.font = self.app.font
    
        Tk.Frame.__init__(self, self.parent, width=350)

        self.padding = Tk.Frame(self, bg="white", height=5)
        self.padding.grid(row=0, column=0, stick=Tk.NSEW)

        # Peers

        self.listbox = Tk.Canvas(self, bg="White", width=20)
        
        self.listbox.grid(row=1, column=0, sticky=Tk.NSEW)

        self.listbox.bind("<Button-1>", lambda e: "break")
        self.listbox.bind("<B1-Motion>", lambda e: "break")

        # Chat

        self.chatbox = Tk.Text(self, bg="White", font=self.app.font, height=10, width=5, bd=1, relief=Tk.FLAT, wrap=Tk.WORD)
        self.chatbox.grid(row=2, column=0, sticky=Tk.NSEW)
        self.chatbox.bind("<FocusIn>", lambda e: self.parent.focus())
        self.num_messages = 0

        self.rowconfigure(1, weight=1) # Expand
        self.rowconfigure(2, weight=1) 
        self.columnconfigure(0, weight=1)

        # Use app font

        self.padx = 5
        self.pady = 2

        self.box_height = 0
        self.tick_box_size = 0

        self.colours = ["#565656", "#7f7f7f", "#7f7f7f"]

        # Counter for dots drawing

        self.ticker = 0
        self.frame  = 0
        self.refresh_rate = 20 # times per second

        self.refresh(internal_call=True)

    def refresh(self, internal_call=False):
        """ Clears the user list and redraws  """
        
        # Clear the contents
        
        self.listbox.delete("all")

        i = 0

        for user_id, user in list(self.app.users.items()):

            y_pos = i * self.box_height

            self.draw_user_box(y_pos, user)

            i += 1

        # Recursive call if we don't call from external (stops extra recursive calls)

        if internal_call:

            # Increase counter

            self.frame += 1

            if self.frame == self.refresh_rate // 2:

                self.ticker = (self.ticker + 1) % 3

                self.frame  = 0

            self.after(1000 // self.refresh_rate, lambda: self.refresh(internal_call=True))

        return 

    def add_chat_message(self, user, message):
        """ Adds a new message to the chat box """
        # Configure correct colours for the user and move insert to end
        self.chatbox.tag_config(user.tag(), foreground=user.get_colour())
        self.chatbox.mark_set(Tk.INSERT, Tk.END)
        # Go to newline if needed
        if self.num_messages > 0:
            self.chatbox.insert(Tk.INSERT, "\n")
        # Insert message
        self.chatbox.insert(Tk.INSERT, user.get_name(), user.tag())
        self.chatbox.insert(Tk.INSERT, ": {}".format(message))
        self.chatbox.see(Tk.END)
        self.num_messages += 1
        return

    def draw_user_box(self, y_pos, user):
        """ Draws user information based on y-position """

        # Draw monitoring box (if client side)

        if self.app.app_type == APP_TYPES.CLIENT:

            self.tick_box_size = int(self.box_height * 0.4)

        else:

            self.tick_box_size = 0

        # Draw text
        text = self.listbox.create_text((self.padx * 2) + self.tick_box_size, y_pos + self.pady, 
                    anchor=Tk.NW, 
                    text=user.get_name(),
                    width=self.get_width() - (self.padx * 2), 
                    font=self.font
                    )
        
        # Get bbox of font
        bounds = self.listbox.bbox(text) 
        
        # Draw background
        bbox = [0, bounds[1] - self.pady, self.get_width(), bounds[3] + self.pady]

        rect = self.listbox.create_rectangle( bbox, fill=user.get_colour() )

        if user.get_is_typing():

            # Draw dots

            dots = self.draw_dots(y_pos)

            # Move other boxes above

            self.listbox.tag_lower(text)
            self.listbox.tag_lower(rect)

        else:

            self.listbox.tag_lower(rect, text)

        # Draw client only tick box

        if self.app.app_type == APP_TYPES.CLIENT:

            self.draw_tick_box(y_pos, user)

        # Store height

        bounds = self.listbox.bbox(rect)
        
        self.box_height = (bounds[3] - bounds[1]) - self.pady
        
        return 

    def draw_dots(self, y_pos):
        """ Draws 3 circles and returns a list of their ID's """
        dots = []
        total_width = self.get_width()
        shade = self.get_colours()

        # Draw the circles in the 5/6th of the 

        x_pos = total_width * 2 / 3
        
        for n in range(3):
        
            w = h = int(self.box_height / 4)
            
            x = x_pos + (w * n * 1.5)
            y = int(y_pos + ((self.box_height * 2 / 3) - (h / 2)))

            n = self.listbox.create_oval([x, y, x + w, y + h], fill=shade[n], outline=shade[n])
            
            dots.append(n)
        
        return dots

    def draw_tick_box(self, y_pos, user):
        """ (client side only) Draws a box next to the user name enabling monitoring of private code pushes """

        local_user = self.app.get_user_id()

        # Calculate size of boxes

        offset1 = (self.box_height - self.tick_box_size) // 2

        bbox1 = [self.padx, y_pos + offset1, self.padx + self.tick_box_size, y_pos + self.tick_box_size + offset1]

        tick_box_outer = self.listbox.create_rectangle( bbox1 , fill="White" if user.id != local_user else "Gray") #

        offset2 = max(self.tick_box_size // 6, 2) # Minimum 2 pixels

        bbox2 = [bbox1[0] + offset2, bbox1[1] + offset2, bbox1[2] - offset2, bbox1[3] - offset2]

        tick_box_inner = self.listbox.create_rectangle( bbox2 , fill="Black" )

        # Put monitoring box on top

        self.listbox.tag_raise(tick_box_outer)

        # Bind to triggers

        if user.get_is_monitored():

            self.listbox.tag_raise(tick_box_inner)

            self.listbox.tag_bind(tick_box_inner, "<ButtonPress-1>", lambda e: self.trigger_stop_user_monitoring(user))

        elif user.id != local_user:

            self.listbox.tag_bind(tick_box_outer, "<ButtonPress-1>", lambda e: self.trigger_start_user_monitoring(user))

        return

    def get_colours(self):
        return self.colours[-self.ticker:] + self.colours[:-self.ticker]

    def get_width(self):
        return self.listbox.winfo_width()
        
    def trigger_start_user_monitoring(self, user):
        return self.app.start_monitoring_user(user)

    def trigger_stop_user_monitoring(self, user):
        return self.app.stop_monitoring_user(user)