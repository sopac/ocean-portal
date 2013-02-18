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
from ocean.netcdf import SurfacePlotter

serverCfg = config.get_server_config()

class ReynoldsPlotter(SurfacePlotter):
    DATASET = 'reynolds'
    PRODUCT_NAME = "Reynolds SST"

    VARIABLE_MAP = {
        'mean': 'sst',
        'dec': 'sst_dec_cats',
    }

    apply_to = util.Parameterise(SurfacePlotter)

    @apply_to(period='daily')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'daily-new-uncompressed')

    # --- get_prefix ---
    @apply_to(period='daily')
    def get_prefix(self, params={}):
        return 'avhrr-only-v2.'

    @apply_to()
    def get_prefix(self, params={}):
        return 'reynolds_sst_avhrr-only-v2_'

class reynolds(SST):
    DATASET = 'reynolds'
    PLOTTER = ReynoldsPlotter

    __periods__ = [
        'daily',
        'monthly',
        '3monthly',
        '6monthly',
        '12monthly',
    ]

    __subdirs__ = [
        'daily-new-uncompressed',
        'averages',
        'decile',
    ]
