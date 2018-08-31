class Codelet:
    def __init__(self, id_num, user_id, string):
        # Unique identifier
        self.id = id_num
        # A list of tuples; User & Code
        self.history = []
        # Internal flags
        self.editor = None
        self.error  = False
        self.hidden = False
        self.highlighted = False
        
        self.update(user_id, string)

    def update(self, user_id, string):
        """ Updates the contents of the codelet text - only changes the user if the string has been changed """
        self.un_hide()
        if string != self.get_text():
            self.history.append((user_id, string))
            self.error = False
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