#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Matthew Howie
#          Danielle Madeley <d.madeley@bom.gov.au>

import os
import os.path
import sys

from ocean import config
from ocean.datasets import SST
from ocean.config import productName

import ersstPlotter

serverCfg = config.get_server_config()

class ersst(SST):

    CACHE_URL = os.path.join(serverCfg['baseURL'],
                             serverCfg['rasterURL'],
                             serverCfg['cacheDir']['ersst'])

    __form_params__ = {
        'baseYear': int,
    }
    __form_params__.update(SST.__form_params__)

    __periods__ = [
        'monthly',
        '3monthly',
        '6monthly',
        '12monthly',
    ]

    def __init__(self):
        SST.__init__(self)

        self.product = productName.products['ersst']
        self.plotter = ersstPlotter.ErsstPlotter()
