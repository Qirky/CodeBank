class User:
    def __init__(self, id_num, name):
        self.id = id_num
        self.name = name
    def __repr__(self):
        return self.name

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
        
        self.update(user_id, string)

    def update(self, user_id, string):
        self.un_hide()
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
        return self.history[-1][1]

    def get_user_id(self):
        return self.history[-1][0]

    def is_being_edited(self):
        return self.editor is not None

    def is_hidden(self):
        return self.hidden

    def hide(self):
        self.hidden = True

    def un_hide(self):
        self.hidden = False

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