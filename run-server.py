#!/usr/bin/env python

import sys

if sys.version_info.major <= 2:

    sys.exit("Error: 'CodeBank' requires Python 3.5 and above to run correctly.")

import argparse

parser = argparse.ArgumentParser( prog="CodeBank Server Application" )

parser.add_argument('-n', '--no-gui', action='store_false', help="Don't activate the GUI for the server")

args = parser.parse_args()

from src.server import Server

myServer = Server(visible=args.no_gui)
myServer.start()

    
    
