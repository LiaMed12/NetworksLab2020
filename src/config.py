from math import factorial, sqrt

from .core import *


class ServerConfig:
    IP = "127.0.0.1"
    PORT = 7777
    CODE = 'utf-8'
    BLOCK_LENGTH = 512


class ClientType:
    QUICK = 0
    LONG = 1


class ServerType:
    ANSWER = 0


OPERATION = {0: plus,
             1: minus,
             2: multi,
             3: divide,
             4: factorial,
             5: sqrt}
