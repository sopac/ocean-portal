#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

import socket

import serverConfig as rc

def get_server_config(hostname=None):
    if not hostname:
        hostname = socket.gethostname().split('.', 2)[0]

    return rc.servers[hostname]
