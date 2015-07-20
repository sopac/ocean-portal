#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os
import os.path
import glob
import numpy as np
import numpy.ma as ma
from datetime import datetime, timedelta

from ocean import config, logger, util
from ocean.netcdf.surfaceplotter import SurfacePlotter
from ocean.netcdf import Gridset
from ocean.netcdf.extractor import LandError

serverCfg = config.get_server_config()
    
DATASET = 'msla'
FILE_PREFIX = 'nrt_global_allsat_msla_h_'

class MslaPlotter(SurfacePlotter):
    DATASET = DATASET
    
    VARIABLE_MAP = {
        'sla': 'sla'
    }
    
    apply_to = util.Parameterise()
    
    PRODUCT_NAME = ""
    
    def __init__(self, variable):
        super(MslaPlotter, self).__init__()
            
    def get_colormap_strategy(self, params={}):
        return 'nonlinear'
    
    def get_grid(self, params, **kwargs):
        gridvar = params['variable'] 
        grid =  MslaGrid(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       suffix2=self.get_suffix_prelim(params=params),
                       date=params['date'],
                       **kwargs)
        return grid
    
    def get_ticks(self, params={}):
        return np.arange(-0.3,0.31,0.06)

    def get_ticks_format(self, params={}, **kwargs):
        return '%.0f'
    
    def get_units(self, params={}, **kwargs):
        return 'mm'
    
    @apply_to(variable='sla')
    def get_labels(self, params={}):
        return ((self.get_ticks(params=params) * 1000).astype(int), None)
    
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET], 'grids', 'daily')

    def get_prefix(self, params={}):
        return FILE_PREFIX
    

class MslaGrid(Gridset):

    def get_filename(self, path, prefix, suffix, date, period):
        """
        Get the file based on the given date
        """
        return getFileForTheDate(path, prefix, date)        

"""
Get the file based on the given date
"""
def getFileForTheDate(path, prefix, date):
    formatted_date = date.strftime('%Y%m%d')
    file_name = prefix + formatted_date + '_'+ formatted_date + '.nc'
    file_name_with_path = os.path.join(path, file_name)
    return file_name_with_path   