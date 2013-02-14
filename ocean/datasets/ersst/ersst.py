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
from ocean.netcdf import SurfacePlotter
from ocean.util import Parameterise

from ersstConfig import ErsstConfig

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
        self.plotter = ERSSTPlotter()

class ERSSTPlotter(SurfacePlotter):

    DATASET = 'ersst'
    PRODUCT_NAME = "Extended Reconstructed SST"
    CONFIG = ErsstConfig

    apply_to = Parameterise(SurfacePlotter)

    @apply_to()
    def get_prefix(self, params={}):
        return 'ersst_v3b_'

    @apply_to(period='monthly')
    def get_prefix(self, params={}):
        return 'ersst.'

    @apply_to(period='monthly')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET], 'monthly')

    @apply_to(period='monthly', variable='dec')
    def get_path(self, params={}):
        return self.get_path(params=params, _ignore=['period'])
