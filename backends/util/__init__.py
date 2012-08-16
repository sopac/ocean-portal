import os.path

import ocean

def get_resource(*args):
    """
    Return the path to a resource.
    """

    return os.path.join(ocean.__path__[0], 'resource', *args)
