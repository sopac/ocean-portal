#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os.path

from ocean import config, util
from ocean.datasets import SST
from ocean.config import productName
from ocean.netcdf import SurfacePlotter

from reynoldsConfig import ReynoldsConfig

serverCfg = config.get_server_config()

class reynolds(SST):
    CACHE_URL = os.path.join(serverCfg['baseURL'],
                             serverCfg['rasterURL'],
                             serverCfg['cacheDir']['reynolds'])

    __periods__ = [
        'daily',
        'monthly',
        '3monthly',
        '6monthly',
        '12monthly',
    ]

    def __init__(self):
        SST.__init__(self)

        self.product = productName.products['reynolds']
        self.plotter = ReynoldsPlotter()

class ReynoldsPlotter(SurfacePlotter):
    DATASET = 'reynolds'
    PRODUCT_NAME = "Reynolds SST"
    CONFIG = ReynoldsConfig

    apply_to = util.Parameterise(SurfacePlotter)

    @apply_to(period='daily')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'daily-new-uncompressed' )

    # --- get_prefix ---
    @apply_to(period='daily')
    def get_prefix(self, params={}):
        return 'avhrr-only-v2.'

    @apply_to()
    def get_prefix(self, params={}):
        return 'reynolds_sst_avhrr-only-v2_'
