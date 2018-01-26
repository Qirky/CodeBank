from .main import *

# Class for interface on the ServerSide (shown to audience)

class ServerApp(BasicApp):
    def __init__(self, *args, **kwargs):
        
        BasicApp.__init__(self, *args, **kwargs)

        self.root.title("CodeBank Server")

        # Data handlers to handle messages from the clients

        self.handlers = {
            HANDLE_KILL    : self.handle_kill,
            HANDLE_PUSH    : self.handle_recv_codelet,
            HANDLE_DELETE  : self.handle_delete_codelet,
            HANDLE_LOAD    : self.handle_load_codelet,
            HANDLE_DISABLE : self.handle_disable_codelet,
            HANDLE_UNDO    : self.handle_rollback,
            HANDLE_REQUEST : self.handle_request_codelet,
            HANDLE_RELEASE : self.handle_release_codelet,
            HANDLE_REMOVE  : self.remove_user,
        }

        # user_id to codelet_id / None
        self.users = {}

    def evaluate(self, code):
        """ Passes a string to FoxDot to exectute """
        
        if self.lang is not None:

            self.lang.execute(code)

        return

    # Handler methods

    def handle_kill(self, user_id):
        return

    def handle_request_codelet(self, user_id, codelet_id):
        """ Flag a codelet as being edited if not already edited """

        # Get the codelet

        codelet = self.sharedspace.codelets.get(codelet_id, None)

        if codelet is not None:

            # Don't do anything if the codelet is already editing

            if codelet.is_being_edited():

                return

            else:

                # Assign editor

                codelet.assign_editor(user_id)

                self.users[user_id] = codelet_id

                # Send data to clients, if the user_id's match then they are allowed to use it

                self.socket.send_to_all(MESSAGE_LOAD(user_id, codelet_id))

                self.sharedspace.redraw()

        return

    def handle_load_codelet(self, user_id, codelet_id):
        """ Handles a codelet coming in to be edited """
        return

    def handle_disable_codelet(self, user_id, codelet_id):
        """ Flags a codelet to be disabled i.e. cannot be loaded """
        return

    def handle_recv_codelet(self, user_id, code_id, string):
        """ Handles a new/updated codelet received from a user """

        # Find the code_id

        codelet = self.sharedspace.codelets.get(code_id, None)

        if codelet is not None:

            codelet.update(user_id, string, self.sharedspace.next_order_id())

        else:

            codelet = Codelet(self.socket.next_codelet_id(), user_id, string)

            self.sharedspace.add_codelet(codelet)

        # Store the fact that the user isn't currently working on a codelet

        self.users[user_id] = None

        # Evaluate the code

        self.evaluate(codelet.get_text())

        # Send back to clients

        self.socket.send_to_all(MESSAGE_UPDATE(user_id, codelet.get_id(), string, self.sharedspace.get_order_id()))

        return

    def handle_release_codelet(self, user_id, codelet_id):
        """ Un-locks a codelet to be re-edited with no changes """
        self.sharedspace.codelets[codelet_id].unassign_editor()
        self.sharedspace.redraw()
        self.socket.send_to_all(MESSAGE_RELEASE(user_id, codelet_id))
        return

    def handle_delete_codelet(self, user_id, data):
        return

    def handle_rollback(self, user_id, data):
        return