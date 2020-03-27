# -*- coding: utf-8 -*-

"""
pysocket, A replacement to the built-in socket module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Requests is an HTTP library, written in Python, for human beings. Basic GET
usage:

>>> import pysocket
>>> socket = pysocket.socket()

and treat like a normal socket.socket (with some difference).

:copyright: (c) 2015 by abmyii.
:license: MIT, see LICENSE for more details.

"""

__title__ = 'pysocket'
__version__ = '1.0.0'
__build__ = '0x64'
__author__ = 'abmyii'
__license__ = 'MIT'
__copyright__ = 'Copyright © 2015 abmyii'

import sys
from socket import *

if not sys.version_info[0] is 3:
    from pysocket import *
    del pysocket
else:
    from pysocket.pysocket import *
