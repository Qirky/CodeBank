#!/usr/bin/env python
import sys

if sys.version_info.major <= 2:

    sys.exit("Error: 'CodeBank' requires Python 3.5 and above to run correctly.")

from src.client import Client

myApp = Client()
myApp.run()