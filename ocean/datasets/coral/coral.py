#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import os
import os.path
import glob

import numpy as np

from ocean import util, config
from ocean.config import productName
from ocean.netcdf import SurfacePlotter
from ocean.plotter import Plotter
from ocean.datasets import SST
from ocean.netcdf import Gridset

from coralAlert import filter_alert

#get the server dependant path configurations
serverCfg = config.get_server_config()

class CoralPlotterWrapper(SurfacePlotter):
    DATASET = 'coral'
    PRODUCT_NAME = "NOAA Coral Reef Watch"

    VARIABLE_MAP = {
        'daily': 'CRW_BAA_max7d',
        'outlook': 'BAA',
    }

    apply_to = util.Parameterise(SurfacePlotter)

    @apply_to(variable='daily')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'daily')

    @apply_to(variable='outlook')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'outlook')

    # --- get_prefix ---
#    @apply_to(variable='daily')
#    def get_prefix(self, params={}):
#        return 'baa_max_r07d_b05kmnn_'
#
#    @apply_to(variable='outlook')
#    def get_prefix(self, params={}):
#        return 'outlook_srt_v3_wk_among28_cfsv2_icwk'
#
    def get_prefix(self, params={}):
        prefix = ''
        if params['variable'] == 'daily':
            prefix = 'baa_max_r07d_b05kmnn_'
        else:
            prefix = 'outlook_srt_v3_wk_among28_cfsv2_icwk'
        return prefix 

    # --- get_title ---
#    @apply_to(variable='daily')
    def get_title(self, params={}):
        title = ''
        if (params['variable'] == 'daily'):
            title = 'Coral Bleaching Alert'
        else: 
            title = 'Coral Bleaching Outlook'
        return title

    @apply_to(variable='daily')
    def get_ticks(self, params={}):
        return np.arange(6) 

    @apply_to(variable='outlook')
    def get_ticks(self, params={}):
        return np.arange(6) 

    @apply_to(variable='daily')
    def get_colors(self, params={}):
        return np.array([[200, 250, 250],
                         [255, 240, 0],
                         [250, 170, 10],
                         [240, 0, 0],
                         [150, 0, 0]])
   
    @apply_to(variable='outlook')
    def get_colors(self, params={}):
        return np.array([[200, 250, 250],
                         [255, 210, 160],
                         [250, 170, 10],
                         [240, 0, 0],
                         [150, 0, 0]])

    def get_fill_color(self, params={}):
        return '0.59'

    def get_colormap_strategy(self, params={}):
        return 'levels'

    #@apply_to(variable='daily')
    def get_plotstyle(self, params={}):
        return 'pcolormesh'
  
#    @apply_to(variable='daily')
    def get_extend(self, params={}):
        return 'neither'

    @apply_to(variable='daily')
    def get_labels(self, params={}):
        return (['No Stress',
                 'Watch',
                 'Warning',
                 'Alert Level 1',
                 'Alert Level 2'],
                [0.5, 1.5, 2.5, 3.5, 4.5])

    @apply_to(variable='outlook')
    def get_labels(self, params={}):
        return (['No Stress',
                 'Watch',
                 'Warning',
                 'Alert Level 1',
                 'Alert Level 2'],
                [0.5, 1.5, 2.5, 3.5, 4.5])

    @apply_to(variable='daily')
    def get_units(self, params={}):
        return ''

    @apply_to(variable='daily')
    def get_contourlines(self, params={}):
        return False

    @apply_to(variable='outlook')
    def get_units(self, params={}):
        return ''

    @apply_to(variable='outlook')
    def get_contourlines(self, params={}):
        return False


    @apply_to(variable='outlook')
    def get_grid(self, params={}, **kwargs):
        """
        Request a Grid object for this dataset.

        Override this method to access grids in a different way.
        """

        gridvar = self.get_variable_mapping(params=params)
        kwargs.update({'depthrange':(0, 2)})
        grid =  CoralGridset(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       suffix2=self.get_suffix_prelim(params=params),
                       date=params['date'],
                       **kwargs)
        if params['period'] == '4weeks':
            grid.data = grid.data[0]
        elif params['period'] == '8weeks':
            grid.data = grid.data[1]
        elif params['period'] == '12weeks':
            grid.data = grid.data[2]
        return grid
        
class CoralGridset(Gridset):
 
    def get_filename(self, path, prefix, suffix, date, period):
        """
        Get the latest outlook
        """
        fileName = os.path.join(path, '*.nc')
        latestFilePath = max(glob.iglob(fileName), key=os.path.getctime)
        return latestFilePath

    def load_data(self, variable):
        """
        Load the subset of @variable. Assumes spatial data with layout:
        (time, (depth)), lat, lon

        Override to handle other data layouts.
        """
        try:
            ndim = len(variable.dimensions)
        except AttributeError:
            ndim = variable.ndim

        if ndim == 3:
            # data arranged time, lat, lon
            return variable
        else:
            raise GridWrongFormat()

    def get_depths(self, variables):
        """
        Implement to retrieve the depths for a dataset.
        """
        return np.arange(3) 


class coral(SST):
    DATASET = 'coral'
    PLOTTER = CoralPlotterWrapper

    __periods__ = [
        'daily',
        '4weeks',
        '8weeks',
        '12weeks',
    ]

    __subdirs__ = [
        'daily',
        'outlook',
    ]

    __plots__ = [
        'map',
    ]

    __variables__ = [
        'daily',
        'outlook'
    ]

    def process_stats(self, params):
        if params['area'] == 'pac' or params['variable'] == 'outlook':
            return {}
        else: 
            grid = self.plotter.get_grid(params=params) 
            alertLevel = filter_alert(params, grid)
            return {'dial': os.path.join('images', params['variable'] + '_' + str(alertLevel) + '.png')}
