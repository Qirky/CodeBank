from .utils import GET_USER_COLOUR, NULL

class Codelet:
    def __init__(self, id_num, user_id, string, order_id=0):
        # Unique identifier
        self.id = id_num
        # A list of tuples; User & Code
        self.history = []
        # Internal flags
        self.editor = None
        self.error  = False
        self.hidden = False
        self.highlighted = False
        
        self.update(user_id, string, order_id)

    def update(self, user_id, string, order_id):
        """ Updates the contents of the codelet text - only changes the user if the string has been changed """
        if self.is_hidden():
            self.order_id = order_id
            self.un_hide()

        if string != self.get_text():
            self.history.append((user_id, string))
            self.error = False
            self.order_id = order_id # might already be done if was hidden?
        return

    def rollback(self, n=1):
        assert type(n) == int
        if len(self.history) > 1:
            self.history = self.history[:-n]
        return

    def load_history(self, data):
        self.history = data
        return

    def get_id(self):
        return self.id

    def get_text(self):
        """ Returns the *current* text of the codelet (empty string if no updates) """
        return self.history[-1][1] if len(self.history) else ""

    def get_user_id(self):
        return self.history[-1][0]

    def get_order_id(self):
        return self.order_id

    def get_editor(self):
        return self.editor

    def is_being_edited(self):
        return self.editor is not None

    def is_hidden(self):
        return self.hidden

    def hide(self):
        self.hidden = True

    def un_hide(self):
        self.hidden = False

    def highlight(self):
        self.highlighted = True

    def de_highlight(self):
        self.highlighted = False

    def is_highlighted(self):
        return self.highlighted

    def assign_editor(self, user_id):
        self.editor = user_id
        return

    def unassign_editor(self):
        self.editor = None
        return

    def get_history(self):
        return self.history

    def flag_error(self):
        """ Turns the internal error (i.e. code contained error) flag to True """
        self.error = True
        return

    def has_error(self):
        return self.error



class User:
    """ Class for representing each user;
        - name: str
        - codelet_id they are editing (None if not editing): int / None (maybe use -1 in place of None?)
        - is_typing, flag if user is adding a new codelet: bool
        - colour: string of hex colour
        - text_tag: string of tkinter tag
        - is_monitored: bool for if user is monitoring private code pushes
        - monitoring: list of user_id's this user is monitoring
    """
    def __init__(self, id_num, name):
        self.id = int(id_num)
        self.name = name
        self.codelet_id = NULL
        self.is_typing = False
        self.colour = GET_USER_COLOUR(self.id)
        self.text_tag = "text_tag_{}".format(self.id)

        self.last_monitored_code = None
        self.is_monitored = False
        self.monitoring = []

    def __repr__(self):
        return self.name

    def get_name(self):
        return self.name

    def get_colour(self):
        return self.colour

    def tag(self):
        return self.text_tag

    def get_is_typing(self):
        return self.is_typing

    # Unnecessary?
    def get_codelet_id(self):
        return self.codelet_id

    def get_is_monitored(self):
        return self.is_monitored

    def get_monitored_users(self):
        return self.monitoring

    def add_monitoring(self, user_id):
        if user_id not in self.monitoring:
            self.monitoring.append(user_id)

    def remove_monitoring(self, user_id):
        if user_id in self.monitoring:
            self.monitoring.remove(user_id)

    def monitor_evaluate(self, text):
        self.last_monitored_code = text

    def get_last_monitored_code(self):
        return self.last_monitored_code

    def start_monitoring(self):
        self.is_monitored = True

    def stop_monitoring(self):
        self.is_monitored = False
        self.last_monitored_code = None

    def set_is_typing(self, flag):
        self.is_typing = bool(flag)

    def assign_codelet(self, i):
        self.codelet_id = i

    def clear_codelet(self):
        self.codelet_id = NULL
