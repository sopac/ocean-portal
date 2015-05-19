#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac 
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import os
import os.path
import sys
import copy
import glob
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import numpy as np

from ocean import util, config
from ocean.config import productName
from ocean.datasets.poama import POAMA
from ocean.netcdf import SurfacePlotter, Gridset

#get the server dependant path configurations
serverCfg = config.get_server_config()

#get dataset dependant production information
poamaProduct = productName.products['poama']

#number of forecast steps
FORECAST_STEPS = 9

class PoamaPlotterWrapper(SurfacePlotter):
    DATASET = 'poamassta'
    PRODUCT_NAME = "Seasonal Sea Surface Temperature Forecast"

    VARIABLE_MAP = {
        'ssta': 'SSTA_emn',
        'sst': 'SST_emn'
    }

    apply_to = util.Parameterise(SurfacePlotter)

    @apply_to(variable='ssta')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'ssta')

    @apply_to(variable='sst')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'ssta')

    def get_colormap(self, params={}):
        cm_name = 'RdBu_r'
        if params['variable'] == 'sst':
            cm_name = 'jet'
        return cm_name

#    @apply_to(variable='ssta')
#    def get_prefix(self, params={}):
#        return 'asdf'

    @apply_to(variable='ssta')
    def get_ticks(self, params={}):
        return np.arange(-3, 4)

    @apply_to(variable='sst')
    def get_ticks(self, params={}):
        return np.arange(0, 33, 2)

    @apply_to(variable='ssta', period='seasonal')
    def get_formatted_date(self, params={}):
        return ''

    @apply_to(variable='sst', period='seasonal')
    def get_formatted_date(self, params={}):
        return ''

    def get_ticks_format(self, params={}):
        return '%.1f'

    def get_colormap_strategy(self, params={}):
        return 'nonlinear'

    def get_plotstyle(self, params={}):
        return 'pcolormesh'

    def get_extend(self, params={}):
        return 'neither'

    def get_fill_color(self, params={}):
        return '0.0'

#    @apply_to(variable='ssta')
#    def get_units(self, params={}):
#        return 'cm'

    @apply_to(variable='ssta')
    def get_contourlines(self, params={}):
        return False

    @apply_to(variable='sst')
    def get_contourlines(self, params={}):
        return False

    @apply_to(variable='ssta')
    def get_grid(self, params={}, **kwargs):
        """
        Request a Grid object for this dataset.

        Override this method to access grids in a different way.
        """

        gridvar = self.get_variable_mapping(params=params)
        kwargs.update({'depthrange':(0, FORECAST_STEPS)})
        grid =  PoamaGridset(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       suffix2=self.get_suffix_prelim(params=params),
                       date=params['date'],
                       **kwargs)
        return grid

    @apply_to(variable='sst')
    def get_grid(self, params={}, **kwargs):
        """
        Request a Grid object for this dataset.

        Override this method to access grids in a different way.
        """

        gridvar = self.get_variable_mapping(params=params)
        kwargs.update({'depthrange':(0, FORECAST_STEPS)})
        grid =  PoamaGridset(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       suffix2=self.get_suffix_prelim(params=params),
                       date=params['date'],
                       **kwargs)
        return grid

    def plot_basemaps_and_colorbar(self, output, step, args):
        area = args['area']
        variable = args['variable']

        args['formattedDate'] = self.get_formatted_date(params=args)
        output_filename = serverCfg['outputDir'] + output + '.png'

        title = ''

        units = self.get_units(params=args)
        cmap_name = self.get_colormap(params=args)
        cb_ticks = self.get_ticks(params=args)
        cb_tick_fmt = self.get_ticks_format(params=args)
        cb_labels, cb_label_pos = self.get_labels(params=args)
        extend = self.get_extend(params=args)
        contourLabels = self.get_contour_labels(params=args)
        plotStyle = self.get_plotstyle(params=args)#GAS
        contourLines = self.get_contourlines(params=args)#GAS
        smoothFactor = self.get_smooth_fac(params=args)#GAS
        colors = self.get_colors(params=args)
        fill_color = self.get_fill_color(params=args)
        colormap_strategy = self.get_colormap_strategy(params=args)

        plot = self.getPlotter()
        grid = self.get_grid(params=args)
 
        plot.plot_basemaps_and_colorbar(grid.lats, grid.lons, grid.data[step],
                                        output_filename=output_filename,
                                        units=units,
                                        cm_edge_values=cb_ticks,
                                        cb_tick_fmt=cb_tick_fmt,
                                        cb_labels=cb_labels,
                                        cb_label_pos=cb_label_pos,
                                        cmp_name=cmap_name, extend=extend,
                                        colormap_strategy = colormap_strategy,
                                        colors = colors,
                                        fill_color = fill_color)

        plot.wait()

class PoamaGridset(Gridset):
    TIME_VARIABLE = ['time']

    def get_filename(self, path, prefix, suffix, date, period):
        """
        Get the latest outlook
        """
        fileName = os.path.join(path, 'PACCSAP_oa_latest.nc')
        return  fileName

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
            return variable
        else:
            raise GridWrongFormat()

    def get_depths(self, variables):
        """
        Implement to retrieve the depths for a dataset.
        """
        return np.arange(FORECAST_STEPS)

class poamassta(POAMA):
        
    DATASET = 'poamassta'
    PLOTTER = PoamaPlotterWrapper

    def preprocess(self, var, region, args):
        '''
            Allows the map images to be produced via the URL.
        '''
        for step in range(FORECAST_STEPS):
   #         self.plotter.plot_basemaps_and_colorbar(self.getPlotFileName(var, step, region)[1], step,  args)
            plot_filename = '%s_%s_%s_%02d' % (poamaProduct[var], var, region, step)
            self.plotter.plot_basemaps_and_colorbar(plot_filename, step,  args)

    def generateConfig(self, params):
        '''
            Generate the configuration file
        '''
        baseDateTime = datetime(1800, 1, 1, 0, 0, 0)  
        
        timeArray = self.plotter.get_grid(params=params).time
        timeObjArray = map(timedelta, timeArray.astype(float))

        dateTimeObjArray = [baseDateTime + x for x in timeObjArray]
        dateTimeStrArray = [{"datetime": x.strftime('%b') + ' ' + str(x.year)} for x in dateTimeObjArray]
        return dateTimeStrArray
   
    def getPlotFileName(self, varName, timeIndex, regionName):
        '''
            A helper method to put together the plot file name.
        '''
        plot_filename = '%s_%s_%s_%02d' % (poamaProduct[varName], varName, regionName, timeIndex)
        plot_filename_fullpath = os.path.join(serverCfg['outputDir'],
                                                  plot_filename)
        raster_filename_fullpath = os.path.join(serverCfg['baseURL'],
                                                 serverCfg['rasterURL'],
                                                 plot_filename)
        return plot_filename_fullpath, raster_filename_fullpath
