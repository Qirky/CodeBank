#!/usr/bin/env python

import sys

if sys.version_info.major <= 2:

    sys.exit("Error: 'CodeBank' requires Python 3.5 and above to run correctly.")

import argparse

parser = argparse.ArgumentParser( prog="CodeBank Server Application" )

parser.add_argument('-n', '--no-gui', action='store_false', help="Don't activate the GUI for the server")
parser.add_argument('-m', '--mode', action='store', default="foxdot", help="Name of interpreter e.g. FoxDot")

args = parser.parse_args()

from src.interpreter import get_interpreter_id

lang_id = get_interpreter_id(args.mode)

if lang_id is None:

    sys.exit("FatalError: '{}' is not a valid interpreter.".format(args.mode))

from src.server import Server

myServer = Server(lang_id=lang_id, visible=args.no_gui)
myServer.start()

    
    
