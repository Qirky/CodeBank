from __future__ import absolute_import, print_function
import queue, time, threading
from .main import *

# Class for interface on the ServerSide (shown to audience)

class ServerApp(BasicApp):
    def __init__(self, *args, **kwargs):
        
        BasicApp.__init__(self, *args, **kwargs)

        self.root.title("CodeBank Server: {}".format(self.socket.hostname))

        # Data handlers to handle messages from the clients

        self.handlers = {
            HANDLE_KILL    : self.handle_kill,
            HANDLE_PUSH    : self.handle_recv_codelet,
            HANDLE_HIDE    : self.handle_hide_codelet,
            HANDLE_LOAD    : self.handle_load_codelet,
            HANDLE_DISABLE : self.handle_disable_codelet,
            HANDLE_UNDO    : self.handle_rollback,
            HANDLE_REQUEST : self.handle_request_codelet,
            HANDLE_RELEASE : self.handle_release_codelet,
            HANDLE_TYPING  : self.handle_set_user_typing,
            HANDLE_REMOVE  : self.remove_user,
        }

        self.visible = kwargs.get("visible", True)

        # Poll the parent queue

        if self.visible:

            self.poll_queue()

    def run(self):
        if self.visible:
            BasicApp.run(self)
        else:
            # Poll queue after server has started w/o runnng mainloop
            try:
                self.poll_queue()
            except KeyboardInterrupt:
                self.kill()
        return


    def poll_queue(self):
        """ Continually poll the server process queue then process each message one at a time
            in the order it was added to the server. """
        try:

            while True:
                
                data = self.socket.queue.get_nowait()
                
                self.handle_data(data)

        # Break the loop when the queue is empty
        except queue.Empty:
            pass

        # Call this function in 0.1 second
        if self.visible:    
        
            self.root.after(100, self.poll_queue)
        
        elif self.socket.running:
        
            time.sleep(0.1)
        
            self.poll_queue()
        
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

                self.users[user_id].assign_codelet( codelet_id )

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

    def handle_recv_codelet(self, user_id, codelet_id, string):
        """ Handles a new/updated codelet received from a user """

        # Find the code_id

        codelet = self.sharedspace.codelets.get(codelet_id, None)

        if codelet is not None:

            codelet.update(user_id, string, self.socket.next_order_id())

        else:

            codelet = Codelet(self.socket.next_codelet_id(), user_id, string, self.socket.next_order_id())

            self.sharedspace.add_codelet(codelet)

        # Store the fact that the user isn't currently working on a codelet

        self.users[user_id].clear_codelet()

        # Evaluate the code

        self.evaluate_codelet(codelet)

        # Send back to clients

        self.socket.send_to_all(MESSAGE_UPDATE(user_id, codelet.get_id(), string, codelet.get_order_id()))

        return

    def handle_release_codelet(self, user_id, codelet_id):
        """ Un-locks a codelet to be re-edited with no changes """
        self.get_codelet(codelet_id).unassign_editor()
        self.sharedspace.redraw()
        self.socket.send_to_all(MESSAGE_RELEASE(user_id, codelet_id))
        return

    def handle_hide_codelet(self, user_id, codelet_id):
        """ Labels the codelet as hidden and redraws the canvas, ignoring this codelet """
        self.get_codelet(codelet_id).hide()
        self.sharedspace.redraw()
        self.socket.send_to_all(MESSAGE_HIDE(user_id, codelet_id))
        return

    def handle_rollback(self, user_id, codelet_id):
        """ Removes the last item in the history and redraws the shared-space """
        self.get_codelet(codelet_id).rollback()
        self.sharedspace.redraw()
        self.socket.send_to_all(MESSAGE_UNDO(user_id, codelet_id))
        return

    def handle_set_user_typing(self, user_id, flag):
        """ Flags a user as typing then forward to all other connected users """
        BasicApp.set_user_typing(self, user_id, flag)
        self.socket.send_to_all(MESSAGE_TYPING(user_id, flag))
        return