import os.path
import socket

import ocean
import serverConfig as rc

def get_resource(*args):
    """
    Return the path to a resource.
    """

    return os.path.join(ocean.__path__[0], 'resource', *args)

def check_files_exist(basename, subnames):
    """
    Returns: True if the list of files basename+subnames[0, 1, 2, etc..] exist.
    """

    return reduce(lambda a, p: a and os.path.exists(basename + p),
        subnames, True)

def get_server_config(hostname=None):
    if not hostname:
        hostname = socket.gethostname().split('.', 2)[0]

    return rc.servers[hostname]
