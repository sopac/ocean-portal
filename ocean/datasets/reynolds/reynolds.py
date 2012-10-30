#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os
import os.path
import sys

from ocean import config
from ocean.datasets import SST
from ocean.config import productName

import reynoldsPlotter

serverCfg = config.get_server_config()

class reynolds(SST):
    CACHE_URL = os.path.join(serverCfg['baseURL'],
                             serverCfg['rasterURL'],
                             serverCfg['cacheDir']['reynolds'])

    __periods__ = [
        'daily',
        'monthly',
        'yearly',
    ]

    def __init__(self):
        SST.__init__(self)

        self.product = productName.products['reynolds']
        self.plotter = reynoldsPlotter.ReynoldsPlotter()
