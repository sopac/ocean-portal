#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import os
import os.path
import glob
import calendar
from datetime import date

import numpy as np

from ocean import util, config
from ocean.netcdf import SurfacePlotter
from ocean.datasets import SST
from ocean.netcdf import Grid, Gridset


#get the server dependant path configurations
serverCfg = config.get_server_config()

class ChlorophyllPlotterWrapper(SurfacePlotter):
    DATASET = 'chloro'
    PRODUCT_NAME = "Chlorophyll-A"

    VARIABLE_MAP = {
        'chldaily': 'l3m_data',
        'chlmonthly': 'l3m_data',
    }

    apply_to = util.Parameterise(SurfacePlotter)

    @apply_to(variable='chldaily')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'daily')

    @apply_to(variable='chlmonthly')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'monthly')

    # --- get_prefix ---
#    @apply_to(variable='chldaily')
    def get_prefix(self, params={}):
        return 'A'

#    @apply_to(variable='chlmonthly')
#    def get_prefix(self, params={}):
#        return 'A'

    @apply_to(variable='chldaily')
    def get_suffix(self, params={}):
        return '.L3m_DAY_CHL_chlor_a_4km' + self.FILE_EXTENSION

    @apply_to(variable='chlmonthly')
    def get_suffix(self, params={}):
        return '.L3m_MO_CHL_chlor_a_4km' + self.FILE_EXTENSION

    # --- get_title ---
    def get_title(self, params={}):
        title = 'Chlorophyll-A'
        return title

    def get_colormap(self, params={}):
        cm_name = 'jet'
        return cm_name

    @apply_to(variable='chldaily')
    def get_ticks(self, params={}):
        return np.array([0.0, 0.15, 0.2, 0.25, 0.3, 0.4, 0.6, 1.0, 2.0, 4.0, 8.0, 16.0, 30.0]) 

    @apply_to(variable='chlmonthly')
    def get_ticks(self, params={}):
        return np.array([0.0, 0.15, 0.2, 0.25, 0.3, 0.4, 0.6, 1.0, 2.0, 4.0, 8.0, 16.0, 30.0]) 

    def get_ticks_format(self, params={}):
        return '%.2f'

    def get_colormap_strategy(self, params={}):
        return 'nonlinear'

#    def get_colormap(self, params={}):
#        return 'coolwarm'

#    @apply_to(variable='daily', period='daily')
#    def get_formatted_date(self, params={}):
#        date = params['date'].timetuple()
#        return '%4d%03d' % (date.tm_year, date.tm_yday)

    def get_plotstyle(self, params={}):
        return 'pcolormesh'
  
    def get_extend(self, params={}):
        return 'neither'

    def get_fill_color(self, params={}):
        return '0.0'

    @apply_to(variable='chldaily')
    def get_units(self, params={}):
        return 'mg/m' + ur'\u00B3'

    @apply_to(variable='chlmonthly')
    def get_units(self, params={}):
        return 'mg/m' + ur'\u00B3' 

    @apply_to(variable='chldaily')
    def get_contourlines(self, params={}):
        return False

    @apply_to(variable='chlmonthly')
    def get_contourlines(self, params={}):
        return False

    @apply_to(variable='chldaily', period='daily')
    def get_grid(self, params={}, **kwargs):
        """
        Request a Grid object for this dataset.

        Override this method to access grids in a different way.
        """

        gridvar = self.get_variable_mapping(params=params)
        grid =  ChlorophyllGridset(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       suffix2=self.get_suffix_prelim(params=params),
                       date=params['date'],
                       **kwargs)
        return grid

    @apply_to(variable='chlmonthly', period='monthly')
    def get_grid(self, params={}, **kwargs):
        """
        Request a Grid object for this dataset.

        Override this method to access grids in a different way.
        """

        gridvar = self.get_variable_mapping(params=params)
        grid =  ChlorophyllMonthlyGridset(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       suffix2=self.get_suffix_prelim(params=params),
                       date=params['date'],
                       **kwargs)
        return grid


class ChlorophyllGridset(Gridset):
 
    # a list of possible variables for latitudes
    LATS_VARIABLE = ['Number_of_Lines']

    # a list of possible variables for longitude
    LONS_VARIABLE = ['Number_of_Columns']

    def get_filename_date(self, date, **kwargs):
        date = date.timetuple()
        return '%4d%03d' % (date.tm_year, date.tm_yday)

class ChlorophyllMonthlyGridset(ChlorophyllGridset):
 
    def get_filename_date(self, date, **kwargs):
        first_day_month = date.replace(day=1)
        last_day_month = date.replace(day=calendar.monthrange(date.year, date.month)[1])

        first_date = first_day_month.timetuple()
        last_date = last_day_month.timetuple()
        return '%4d%03d%4d%03d' % (first_date.tm_year, first_date.tm_yday, last_date.tm_year, last_date.tm_yday)

class chlorophyll(SST):
    DATASET = 'chloro'
    PLOTTER = ChlorophyllPlotterWrapper

    __periods__ = [
        'daily',
        'monthly',
    ]

    __subdirs__ = [
        'daily',
        'monthly',
    ]

    __plots__ = [
        'map',
    ]

    __variables__ = [
        'chldaily',
        'chlmonthly'
    ]
