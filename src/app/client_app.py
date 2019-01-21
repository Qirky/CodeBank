from __future__ import absolute_import, print_function

from .main import *
from .connection_input import popup_window
from .clock_nudge import ClockNudgePopup
from ..utils import get_players, NULL, CONTROL_KEY, APP_TYPES

# Class for interface for client-side

class App(BasicApp):
    app_type = APP_TYPES.CLIENT
    def __init__(self, *args, **kwargs):
        
        BasicApp.__init__(self, *args, **kwargs)

        try:

            self.root.state("zoomed")
            
        except Tk.TclError:

            pass

        # Menu bar

        self.menu = MenuBar(self)
        self.root.config(menu=self.menu)

        # Popup information

        self.popup_open = False
        self.nudge_popup_open = False
        self.nudge = 0

        # Lower text box for client text entry

        self.workspace = Workspace(self)
        self.workspace.grid(row=1, column=0, sticky=Tk.NSEW)
        self.root.grid_rowconfigure(1, weight=0) # make sure workspace expands
        self.text = self.workspace.text # Give the app a direct reference to text

        # Data handlers to handle messages from the server

        self.handlers = {
            HANDLE_KILL     : self.kill,
            HANDLE_UPDATE   : self.recv_codelet,
            HANDLE_HIDE     : self.hide_codelet,
            HANDLE_LOAD     : self.load_codelet,
            HANDLE_DISABLE  : self.disable_codelet,
            HANDLE_UNDO     : self.rollback,
            HANDLE_NAME     : self.add_user,
            HANDLE_SET_ID   : self.set_user_id,
            HANDLE_TYPING   : self.set_user_typing,
            HANDLE_RELEASE  : self.release_codelet,
            HANDLE_ERROR    : self.raise_error,
            HANDLE_INFO     : self.print_msg,
            HANDLE_REMOVE   : self.remove_user,
            HANDLE_HISTORY  : self.load_codelet_history,
            HANDLE_SHUTDOWN : self.shutdown_from_server,
            HANDLE_SEED     : self.update_random_seed,
            HANDLE_CHAT     : self.receive_chat_message,
            HANDLE_CLEAR    : self.clear_clock,
            HANDLE_MONITOR_EVAL : self.evaluate_monitored_user,
        }

        # This stores the codelet being currently edited

        self.current_codelet  = NULL
        self.highlighted_codelet = NULL

        self.sharedspace.canvas.bind("<Enter>", self.unhighlight_all_codelets)
        self.sharedspace.canvas.bind("<Leave>", self.unhighlight_all_codelets)

        # Keyboard bindings

        self.root.bind("<{}-n>".format(CONTROL_KEY), self.init_connection)

        # Boolean flags

        self.solo_on = False
        self.selecting_codelet_to_hide = False

        # Banned local commands

        self.banned_commands = [re.compile(r".*(Clock\s*\.\s*bpm\s*[\+\-\*\/]*\s*=\s*.+)"), re.compile(r".*(Clock\s*\.\s*clear\(\s*\))")]

        # Don't allow users to use buttons / text box until connected

        self.disable()

    def get_connection_info(self):
        """ Open dialog for a user to enter their connection information """
        
        self.popup = popup_window(self.root, title="Connect to server")
        self.popup.host.focus_set()

        # Put the popup on top
        
        self.root.wait_window(self.popup.top)

        return self.popup.value

    def init_connection(self, event=None):
        """ Create an input dialog for entering information about the user and server """
        if not self.socket.is_connected() and self.popup_open == False:

            self.popup_open = True
            
            info = self.get_connection_info()

            if info is not None:

                try:
                
                    self.socket.connect(*info)
                    
                    self.workspace.set_connection(self.socket)

                    self.connected = True

                    self.workspace.text.focus_set()

                except ConnectionError as e:

                    print("Connection Error: {}".format(e))

            self.popup_open = False
            
        return

    def get_clock_nudge_value(self):

        self.nudge_popup = ClockNudgePopup(self)
        self.nudge_popup.display.focus_set()
        self.root.wait_window(self.nudge_popup.top)

        return self.nudge_popup.value

    def show_clock_nudge_popup(self, event=None):
        """ Shows a popup that allows the user to change the "nudge" value for the clock """

        if self.socket.is_connected() and self.nudge_popup_open is False:

            self.nudge_popop_open = True

            nudge = self.get_clock_nudge_value()

            if nudge is not None:

                self.nudge = nudge

            self.evaluate("Clock.nudge = {}".format(self.nudge), verbose=False)

            self.nudge_popup_open = False

        return

    def disable(self):
        """ Stop textbox and buttons from being used """
        self._is_enabled = False
        self.root.title("CodeBank Client: Not Connected")

        self.workspace.disable()
        
        # Dissalow codelets to be highlighted
        self.codelet_on_click = lambda *args, **kwargs: None
        self.disable_codelet_highlight = lambda *args, **kwargs: True
        
        return

    def enable(self):
        """ Allows textbox and buttons being used """ # 
        self._is_enabled = True
        self.root.title("CodeBank Client. Logged in as {}".format(self.get_client_name()))

        self.workspace.enable()

        # Allow clicking
        self.codelet_on_click = self.request_codelet
        self.disable_codelet_highlight = self.is_editing_codelet
        return

    def clear(self):
        """ Clears the text box and resets the codelet we're working on """
        
        self.workspace.text.clear()

        # Send a message to un-edit the code on the server
        
        if self.get_codelet_id() != NULL:
            
            self.socket.send( MESSAGE_RELEASE(self.get_user_id(), self.get_codelet_id()) )
        
        self.set_codelet_id(NULL)

        self.workspace.commands.default_all()
        
        return

    def send_monitored_code(self, string):
        """ Sends code to server to be forwarded to users monitoring this local user """
        self.socket.send(MESSAGE_MONITOR_EVAL(self.get_user_id(), string))
        return

    # Server communications

    def get_codelet(self, codelet_id):
        return self.sharedspace.codelets[codelet_id].get_codelet()

    def get_codelet_id(self):
        """ Returns the ID of the currently edited codelet"""
        return self.current_codelet

    def get_user_id(self):
        """ Returns the local user's id """
        return self.socket.user_id

    def get_client_name(self):
        """ Returns the user name for this client"""
        return self.socket.user_name

    def get_cursor_icon(self):
        """ Returns the Tkinter string name for the icon that the cursor should be displaying"""
        return "exchange" if self.selecting_codelet_to_hide else ""

    def get_active_cursor_icon(self):
        """ Returns the Tkinter string name for the icon that the cursor should be displayed when hovering on a codebox"""
        return "exchange" if self.selecting_codelet_to_hide else "hand2"

    def set_codelet_id(self, c_id):
        self.current_codelet = c_id
        return

    def set_user_typing(self, user_id, flag):
        """ Update typing ellipses when users are typing """
        if not self.my_id(user_id):
            BasicApp.set_user_typing(self, user_id, flag)
        return

    def request_codelet(self, codelet_id):
        """ Triggered by clicking on a codebox. Sends a message to the server to request edit
            permissions for that codelet """
        if self.get_codelet_id() == NULL:

            # Hide the codelet if we are doing that

            if self.selecting_codelet_to_hide:

                self.send_hide_codelet(codelet_id)

            # If not, request to edit

            else:

                self.socket.send(MESSAGE_REQUEST(self.get_user_id(), codelet_id))

        return

    def release_codelet(self, user_id, codelet_id):
        """ Un-locks a codelet to be re-edited with no changes """
        self.sharedspace.codelets[codelet_id].unassign_editor()
        self.sharedspace.redraw()
        return

    def is_editing_codelet(self):
        """ Returns True if there is a codelet that is flagged to "editing" """
        return self.current_codelet != NULL

    # Button actions

    def push_code_to_remote(self, event=None):
        """ Triggered by PUSH button - pushes code to the remote (and also pulls from) and resets the text box """

        if self._is_enabled:
        
            # Get code contents and package together with information which, if any, codelet is being sent

            if self.solo_on:

                self.solo_local_code()

            code = self.workspace.text.get_text()

            if len(code.strip()) > 0:

                data = MESSAGE_PUSH(self.get_user_id(), self.get_codelet_id(), code)

                if self.socket.is_connected():

                    self.socket.send(data)

                # Clear text and reset

                self.clear()

        return 

    def solo_local_code(self, event=None):
        """ Will mute other players currently being run using FoxDot Player.solo method.
            Triggered by the SOLO button. """
        if self._is_enabled:
            players = get_players(self.workspace.text.get_text())
            if len(players):
                self.solo_on = not self.solo_on
                if len(players) > 1:
                    cmd = "Group({}).solo({})".format(", ".join(players), int(self.solo_on))
                elif len(players) == 1:
                    cmd = "{}.solo({})".format(players[0], int(self.solo_on))
                self.evaluate(cmd)
        return

    def check_valid_command(self, string):
        """ Returns a list of code chunks that are not allowed to be run on a local version """
        banned = []
        for line in string.split("\n"):
            for phrase in self.banned_commands:
                match = phrase.match(line)
                if match is not None:
                    banned.append(match.group(1))
        return banned

    def reset_program_state(self, event=None):
        """ Resets the program state to before the last push, triggered by the RESET button """

        if self._is_enabled:

            if self.solo_on:

                self.solo_local_code()

            code = self.workspace.text.get_text()

            players = get_players(code)

            for player in players:

                self.evaluate("{}.reset()".format(player))

            # e.g. r1.reset() then eval the history of the codelet?

            codelet_id = self.get_codelet_id()

            if codelet_id != NULL:

                codelet = self.sharedspace.codelets[codelet_id].get_codelet()

                self.evaluate_codelet_history(codelet)

            self.clear() # sends data to server

        return

    def trigger_rollback(self, event=None):
        """ Resets the players and deletes the last commit to the current codelet. """
        if self._is_enabled:
    
            codelet_id = self.get_codelet_id()

            if codelet_id != NULL:

                data = MESSAGE_UNDO(self.get_user_id(), self.get_codelet_id())

                if self.socket.is_connected():

                    self.socket.send(data)

                # Clear text and reset

                self.clear()

        return

    def toggle_view_hidden(self, event=None):
        """ Shows any codeboxes that have been labelled as hidden """
        if self._is_enabled:

            self.sharedspace.canvas.toggle_view_hidden()

            self.workspace.commands["TOGGLE HIDDEN"].toggle() # not a great way to do it

            self.sharedspace.redraw()

        return

    def trigger_hide_codelet(self, event=None):
        """ Labels this codelet as hidden """
        if self._is_enabled:

            codelet_id = self.get_codelet_id()

            if codelet_id != NULL:

                # Use currently selected 

                self.send_hide_codelet(codelet_id)

                # Clear text and reset

                self.clear()

            # If not editing, clicking hide lets us select a codelet to hide

            else:

                self.toggle_selecting_codelet_to_hide()

        return

    def toggle_selecting_codelet_to_hide(self):
        """ Switch on/off the selecting to hide feature """
        if self.selecting_codelet_to_hide:
            self.selecting_codelet_to_hide = False
            
        else:
            self.selecting_codelet_to_hide = True
        self.workspace.commands["HIDE"].toggle()
        self.root.config(cursor=self.get_cursor_icon())
        return

    def send_hide_codelet(self, codelet_id):
        """ Sends a message to the server to hide a codelet from view """

        # Only send if the codelet is not already hidden

        if self.sharedspace.codelets[codelet_id].is_hidden() is False:
        
            data = MESSAGE_HIDE(self.get_user_id(), codelet_id)

            if self.socket.is_connected():

                self.socket.send(data)

            if self.selecting_codelet_to_hide:

                self.toggle_selecting_codelet_to_hide()

        return

    def hide_all_codelets(self, event=None):
        """ Sends messages for hiding all codelets that are not being edited """
        for codelet_id, codelet in self.sharedspace.codelets.items():

            if codelet.is_being_edited() is False:

                self.send_hide_codelet(codelet_id)

        return

    def send_clear_clock_message(self,  event=None):
        """ Sends a new message to the server to clear the scheduling clock """
        if self._is_enabled:
        
            data = MESSAGE_CLEAR(self.get_user_id())

            if self.socket.is_connected():

                self.socket.send(data)

        return

    #####

    def my_id(self, user_id):
        """ Returns True if the  user id is that of the local client """
        return user_id == self.socket.user_id

    def flag_user_typing(self, flag):
        """ Sends a message to the server flagging this user as typing a new codelet """

        if self._is_enabled:
            
            data = MESSAGE_TYPING(self.get_user_id(), flag)

            if self.socket.is_connected():

                self.socket.send(data)

        return

    def send_chat_message(self, message):
        """ Send a chat message to the server """
        if self._is_enabled:

            data = MESSAGE_CHAT(self.get_user_id(), message)

            if self.socket.is_connected():

                self.socket.send(data)

        return

    #####

    # Handler methods

    def load_codelet(self, user_id, codelet_id):
        """ Handles a codelet coming in to be edited """

        # If the user id is the local user, load it
        if self.my_id(user_id):

            self.workspace.load_from_codelet(codelet_id)
        
        # Flag it to be grey and redraw
        
        self.sharedspace.codelets[codelet_id].assign_editor(user_id)
        
        self.sharedspace.redraw()

        return

    def load_codelet_history(self, user_id, codelet_id, data, order_id, is_hidden ):
        """ Only called when connecting to a server: creates codelets and
            runs the most recent item in the code. """

        user_id, string = data[0] # editor of the code, user_id argument is likely -1

        codelet = Codelet(codelet_id, user_id, string)

        self.sharedspace.add_codelet(codelet)

        codelet.load_history(data)

        if is_hidden:

            # Hide the codelet if flagged

            codelet.hide()
            self.sharedspace.redraw()

        else:

            # Evaluate the code

            self.evaluate_codelet(codelet)

        return

    def disable_codelet(self, user_id, codelet_id):
        """ Flags a codelet to be disabled i.e. cannot be loaded """
        return

    def shutdown_from_server(self, *args, **kwargs):
        """ If the server has been shutdown, disable the interface """
        print("ConnectionError - connection to server lost")
        self.disable()
        return

    def recv_codelet(self, user_id, code_id, string, order_id):
        """ Handles a new/updated codelet """

        # Find the code_id

        codelet = self.sharedspace.codelets.get(code_id, None)

        if codelet is not None:

            codelet.update(user_id, string, order_id)

            update_text = "has updated a codelet."

        else:

            codelet = Codelet(code_id, user_id, string, order_id)

            self.sharedspace.add_codelet(codelet)

            update_text = "has added a new codelet."

        # Evaluate the code

        self.workspace.console.insert_user_update(self.socket.users[user_id], update_text)

        self.evaluate_codelet(codelet)

        return

    def start_monitoring_user(self, user):
        """ Called from public list box widget - flags a user as being monitored """
        self.workspace.console.insert_user_update(user, "is now being monitored")
        user.start_monitoring()
        self.socket.send(MESSAGE_MONITOR_START(self.get_user_id(), user.id))
        return

    def stop_monitoring_user(self, user):
        """ Called from public list box widget - flags a user as not being monitored """
        self.workspace.console.insert_user_update(user, "is no longer being monitored")
        user.stop_monitoring()
        self.socket.send(MESSAGE_MONITOR_STOP(self.get_user_id(), user.id))
        return

    def evaluate_monitored_user(self, user_id, string):
        """ If a user is being monitored, then this method is called to evaluate their code """
        self.workspace.console.insert_user_update(self.socket.users[user_id], "(monitored) has evaluated:")
        self.evaluate(string)
        return

    def hide_codelet(self, user_id, codelet_id):
        """ Labels the codelet as hidden """
        self.get_codelet(codelet_id).hide()
        self.sharedspace.redraw()
        # print("User '{}' hiding codelet id. {}".format(self.get_user_name(user_id), codelet_id))
        self.workspace.console.insert_user_update(self.socket.users[user_id], "is hiding codelet id. {}".format(codelet_id))
        return

    def rollback(self, user_id, codelet_id):
        """ Removes the last item in the history and redraws the shared-space """

        codelet = self.sharedspace.codelets[codelet_id].get_codelet()

        codelet.rollback()

        self.sharedspace.redraw()

        return

    def clear_clock(self, user_id):
        """ Silently stops clock and prints message with user ID """
        BasicApp.clear_clock(self)
        # print("{} has cleared the clock.".format(self.get_user_name(user_id)))
        self.workspace.console.insert_user_update(self.socket.users[user_id], "has cleard the clock")
        return

    def add_user(self, user_id, name): # what is the point
        """ Adds a user to the address book and updates the UI title if the local client """
        BasicApp.add_user(self, user_id, name)
        return

    def remove_user(self, user_id):
        # print("User  '{}' has disconnected.".format(self.get_user_name(user_id)))
        self.workspace.console.insert_user_update(self.socket.users[user_id], "has disconnected")
        BasicApp.remove_user(self, user_id)
        return

    def set_user_id(self, user_id):
        self.socket.user_id = user_id
        return

    def raise_error(self, user_id, err_msg):
        """ Raises a ConnectionError that displays err_msg (string) in the console.
            Triggered by HANDLE_ERROR message. """
        raise ConnectionError(err_msg)

    def print_msg(self, user_id, string):
        """ Prints string to the console. Triggered by HANDLE_INFO message. """
        return print(string)

    def unhighlight_all_codelets(self, event=None):
        """ Sets hl codelet to -1 """
        if self.highlighted_codelet != NULL:
            self.sharedspace.codelets[self.highlighted_codelet].de_highlight()
            self.highlighted_codelet = NULL
            self.sharedspace.redraw()
        return

    def highlight_codelet(self, codelet_id):
        """ Flags the interface to highlight a codelet """
        if codelet_id == NULL:
            self.unhighlight_all_codelets()
        else:
            self.get_codelet(codelet_id).highlight()
            self.highlighted_codelet = codelet_id
        return

    def highlight_codelet_up(self, event=None):
        """ Called when the user uses Alt+Up to cycle through the codelets """
        if self.current_codelet == NULL:
            codeboxes = self.sharedspace.canvas.visible_codelets()
            if self.highlighted_codelet == -1:
                # Get bottom codebox
                codebox = codeboxes[-1]
            else:
                # Find the codebox above the current one
                codebox = codeboxes[0]
                for n in range( len( codeboxes ) - 1 ):
                    this_codebox = codeboxes[n + 1]
                    if this_codebox.codelet.id == self.highlighted_codelet:
                        this_codebox.codelet.de_highlight()
                        break
                    codebox = this_codebox
                else:
                    codebox = codeboxes[0]
            
            self.highlight_codelet(codebox.codelet.id)
            
            self.sharedspace.redraw()

            # If codebox not in view, scroll up until it is

            if not codebox.in_view():

                self.sharedspace.canvas.yview_moveto(1)

                while not codebox.in_view():

                    self.sharedspace.canvas.yview_scroll(-1, "units")
                    self.sharedspace.canvas.update()

                    # If scrolled to top, break

                    if self.sharedspace.y_scroll.get()[0] == 1.0:

                        break
            
            self.set_mouse_in_codebox(False)

        else:
            
            return "break"

    def highlight_codelet_down(self, event=None):
        if self.current_codelet == NULL:
            codeboxes = self.sharedspace.canvas.visible_codelets()
            if self.highlighted_codelet == -1:
                # Get bottom codebox
                codebox = codeboxes[0]
            else:
                # Find the codebox above the current one
                codebox = codeboxes[-1]
                for n in range( len( codeboxes ), 0, -1 ):
                    this_codebox = codeboxes[n - 1]
                    if this_codebox.codelet.id == self.highlighted_codelet:
                        this_codebox.codelet.de_highlight()
                        break
                    codebox = this_codebox
            
            self.highlight_codelet(codebox.codelet.id)
            
            self.sharedspace.redraw()

            # If codebox not in view, scroll down until it is

            if not codebox.in_view():

                self.sharedspace.canvas.yview_moveto(0)

                while not codebox.in_view():

                    self.sharedspace.canvas.yview_scroll(1, "units")
                    self.sharedspace.canvas.update()

                    # If scrolled to bottom, break

                    if self.sharedspace.y_scroll.get()[1] == 1.0:

                        break

            self.set_mouse_in_codebox(False)

        else:
            
            return "break"