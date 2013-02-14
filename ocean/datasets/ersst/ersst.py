#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Matthew Howie
#          Danielle Madeley <d.madeley@bom.gov.au>

import os.path

from ocean import config
from ocean.datasets import SST
from ocean.netcdf import SurfacePlotter
from ocean.util import Parameterise

serverCfg = config.get_server_config()

class ERSSTPlotter(SurfacePlotter):

    DATASET = 'ersst'
    PRODUCT_NAME = "Extended Reconstructed SST"

    VARIABLE_MAP = {
        'mean': 'sst',
        'dec': 'sst_dec_cats',
    }

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

class ersst(SST):
    DATASET = 'ersst'
    PLOTTER = ERSSTPlotter

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

    __subdirs__ = [
        'monthly',
        'averages',
        'deciles',
    ]
