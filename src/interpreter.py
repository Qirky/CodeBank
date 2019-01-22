from .utils import SYSTEM, WINDOWS
import re, shlex, threading, tempfile, time, sys
from subprocess import Popen
from subprocess import PIPE, STDOUT

CREATE_NO_WINDOW = 0x08000000 if SYSTEM == WINDOWS else 0

class Interpreter:
    def __init__(self, path):

        self.path = shlex.split(path)
        self.stdout = tempfile.TemporaryFile("w+", 1) # buffering = 1
        self.is_alive = True

        try:
        
            self.process = Popen(self.path, shell=False, universal_newlines=True, bufsize=1,
                              stdin=PIPE,
                              stdout=self.stdout,
                              stderr=self.stdout,
                              creationflags=CREATE_NO_WINDOW)

            self.stdout_thread = threading.Thread(target=self.read_stdout)
            self.stdout_thread.start()

        except FileNotFoundError:

            raise ExecutableNotFoundError(self.get_path_as_string())

        self._banned_commands = []
        self._colour_map = {}
        self.execute(self.setup_code(), verbose=False)

    def setup_code(self):
        """ Called from __init__ - code required at startup e.g. imports """
        return

    def start_server(self):
        """ Executes any code necessary to allow clock sync """
        return

    def stop_server(self):
        """ Executes any code necessary to stop server functionality """
        return

    def sync_to_server(self, ip_address):
        """ If there is any required synchronisation with the server from the lang, do so here """
        return

    def format_code(self, string):
        """ Formats code specifically to an interpreter if necessary """
        return string

    def execute(self, code_string, verbose=True):
        """ Pipe string into interpreter """
        if code_string is not None:
            self.print_out(code_string)
            self.pipe_to_process(code_string)
        return

    def read_stdout(self, text=""):
        """ Continually reads the stdout from the self.process """
        while self.is_alive:
            if self.process.poll():
                self.is_alive = False
                break
            try:
                # Check contents of file
                self.stdout.seek(0)
                for stdout_line in iter(self.stdout.readline, ""):
                    sys.stdout.write(stdout_line.rstrip())                
                # clear tmpfile
                self.stdout.truncate(0)
                time.sleep(0.05)
            except ValueError as e:
                print(e)
                return
        return

    def pipe_to_process(self, string):
        if self.is_alive:
            self.process.stdin.write(self.format_code(string))
            self.process.stdin.flush()
        return

    def print_out(self, string):
        lines = [line.replace("\n", "") for line in string.split("\n") if len(line.strip()) > 0]
        for line in lines:
            sys.stdout.write(">>> {}".format(string))
            sys.stdout.flush()

    def kill(self):
        """ Called to properly exit the subprocess"""
        self.is_alive = False
        if self.process.poll() is None:
            self.process.communicate()
        return

    def contains_error(self, response):
        """ Returns True if the response from the Interpreter signals an error """
        return

    def get_nudge_code(self, value):
        """ Code for adjusting clock nudge by `value` seconds """
        return
    def get_random_seed_setter(self, seed):
        """ Returns code for setting the same random seed value """
        return

    def get_streams(self, string):
        """ Returns a list of objects that correspond to each different audio stream in a codelet """
        return

    def get_stop_sound(self):
        """ Returns the code for stopping all sound / clearing a scheduling clock """
        return

    def get_solo_code(self, string, on):
        """ Returns code for solo-ing a single codelet / workspace text. Should 
            return None if no streams exist. `on` is a bool for solo-ing or desolo-ing"""
        return None
    def get_reset_code(self, local_code, codelet_code):
        """ Returns code necessary to reset program state. If codelet_code is empty,
            stop any streams. If it exists, reset streams and apply codelet_code """
        return

    def add_to_colour_map(self, regex, colour, name=None):
        ident = str(name) if name is not None else "colour_map_{}".format(len(self._colour_map))
        self._colour_map[ident] = (regex, colour)
        return

    def get_formatting(self):
        """ Returns a dict of """
        return self._colour_map

    def findstyles(self, line, *args):
        """ Finds any locations of any regex and returns the name
            of the style and the start and end point in the line """

        tags = self._colour_map.keys()

        pos = []

        for tag in tags:

            match_start = match_end = 0

            for match in re.finditer(self._colour_map[tag][0], line):

                looking = True

                i = 0

                while looking:

                    try:

                        start  = match.start(i)
                        end    = match.end(i)

                        if start == end == -1:

                            raise IndexError # this is hacky af

                        match_start = start
                        match_end   = end

                    except IndexError:

                        looking = False

                    i += 1

                pos.append((tag, match_start, match_end))

        return pos

    def add_banned_command(self, regex):
        """ Add a RegEx that will flag a code execution as disallowed when found """
        self._banned_commands.append(re.compile(regex))

    def get_banned_commands(self):
        return self._banned_commands

class FoxDot(Interpreter):
    path = "python -u -m FoxDot --pipe"
    def __init__(self):
        Interpreter.__init__(self, FoxDot.path)
        # Ban local changes to tempo / clock stopping
        self.add_banned_command(r".*(Clock\s*\.\s*bpm\s*[\+\-\*\/]*\s*=\s*.+)")
        self.add_banned_command(r".*(Clock\s*\.\s*clear\(\s*\))")

        # Set up syntax colouring

        self.add_to_colour_map(r"(?<=def )(\w+)", '#29abe2', name="user_defn")
        self.add_to_colour_map(r"(?<=>>)(\s*\w+)", '#ec4e20', name="players")
        self.add_to_colour_map(r"^\s*#.*|[^\"']*(#[^\"']*$)", '#666666', name="comments")
        self.add_to_colour_map(r"\W+(\d+)", '#e89c18', name="numbers")
        self.add_to_colour_map(r"\".*?\"|\".*" + "|\'.*?\'|\'.*", "Green", name="strings")
        self.add_to_colour_map(r"\s>>\s?", "#e89c18", name="arrow", )

    def kill(self):
        self.execute("Clock.stop()")
        return Interpreter.kill(self)

    def format_code(self, string):
        return "{}\n\n".format(string)

    def start_server(self):
        return self.execute("allow_connections()")

    def stop_server(self):
        return self.execute("allow_connections(False)")

    def sync_to_server(self, ip_address):
        return self.execute("Clock.connect('{}')".format(ip_address), verbose=True)

    def contains_error(self, response):
        return response.startswith("Traceback") if type(response) == str else False

    def get_nudge_code(self, value):
        return "Clock.nudge = {}".format(value)

    def get_streams(self, string):
        """ Uses RegEx to return the FoxDot players in a block of text """
        return re.findall(r"(\w+)\s*>>", string)

    def get_random_seed_setter(self, seed):
        """ Returns code for setting the same random seed value """
        return "RandomGenerator.set_override_seed({})".format(seed)

    def get_stop_sound(self):
        """ Returns the code for stopping all sound / clearing a scheduling clock """
        return "Clock.clear()"

    def get_solo_code(self, string, on):
        players = self.get_streams(string)
        if len(players):
            if len(players) > 1:
                cmd = "Group({}).solo({})".format(", ".join(players), int(on))
            else:
                cmd = "{}.solo({})".format(players[0], int(on))
        else:
            return None

    def get_reset_code(self, local_code, codelet_code):
        reset_code = []
        
        # Stop players if there isn't a codelet to reset to
        if codelet_code == "":
            func = "stop"
        else:
            func = "reset"

        # Add reset/stop code
        players = self.get_streams(local_code)
        for player in players:
            reset_code.append("{}.{}()".format(player, func))

        # Re-apply codelet text if it exists
        if codelet_code != "":
            reset_code.append(codelet_code)

        return "\n".join(reset_code)

LANGUAGE_NAMES = { "FoxDot": 0, "TidalCycles": 1 }
LANGUAGE_CLASS = { 0 : FoxDot}