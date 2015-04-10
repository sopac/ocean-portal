#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
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

import numpy as np
from ocean import util, config
from ocean.config import productName
#from ocean.netcdf.extractor import Extractor
from ocean.datasets import Dataset
from currentforecastPlotter import CurrentForecastPlotter, COMMON_FILES
from ocean.netcdf import Grid

svnDayForecast = '%s_%s.json'

#get the server dependant path configurations
serverCfg = config.get_server_config()

#get dataset dependant production information
currentProduct = productName.products['currentfc']

#number of forecast steps
FORECAST_STEPS = 57 

class currentforecast(Dataset):

    __form_params__ = {
        'mode': str
    }
    __form_params__.update(Dataset.__form_params__)

    __required_params__ = Dataset.__required_params__ + [
    ]

    __periods__ = [
        '7days',
    ]

    __variables__ = [
        'currents'
    ]

    __plots__ = [
        'map'
    ]

    __subdirs__ = [
    ]

    def process(self, params):
        response = {}

        varStr = params['variable']
        periodStr = params['period']
        regionStr = params['area']

        '''
            Check whether the data file matches the generated config file.
            If the files match, then just return the config file; otherwise
            process the data file and then return the config file.
        '''
        filename = svnDayForecast % (currentProduct['7d'], '7days')
        configFileName = serverCfg['outputDir'] + filename

        latestFilePath = serverCfg['dataDir']['currents'] + 'data/latest_HYCOM_currents.nc'

        #The grid where u and v have been converted to magnitude
#        self.grid = currentforecastGrid(latestFilePath, latestFilePath, ('u', 'v'), (-90, 90), (105, 295))
 
        #For the overlay grid, u and v are used.
##        self.overlayGrid = currentforecastGrid(latestFilePath, latestFilePath, ('u', 'v'), (-90, 90), (105, 295))

        if not os.path.exists(configFileName):
            #The grid where u and v have been converted to magnitude
            self.grid = currentforecastGrid(latestFilePath, latestFilePath, ('u', 'v'), (-90, 90), (105, 295), (0, FORECAST_STEPS))
            #Generate the config file
#            config = self.generateConfig()
            config = self.generateConfig(latestFilePath, self.grid.time)
            with open(configFileName, 'w') as f:
                json.dump(config, f)
           # and associated images.
        else:
            with open(configFileName, 'r') as f:
                config = json.load(f)
#        config = self.generateConfig(latestFilePath, self.grid.time)
        configStr = json.dumps(config) 

        response['forecast'] = configStr 
#        response['mapimg'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['mapimg']
#        response['scale'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['scale']
##        response['mapimg'] = self.getPlotFileName(varStr, 0, 'pac')[1] + COMMON_FILES['mapimg']
##        response['scale'] = self.getPlotFileName(varStr, 0, 'pac')[1] + COMMON_FILES['scale']
        response['mapimg'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['mapimg']
        response['scale'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['scale']
#        os.utime(os.path.join(serverCfg['outputDir'], filename), None)

        if ('mode' in params) and (params['mode'] == 'preprocess'):
            if not hasattr(self, 'grid'):
                self.grid = currentforecastGrid(latestFilePath, latestFilePath, ('u', 'v'), (-90, 90), (105, 295), (0, FORECAST_STEPS))
            response['preproc'] = 'inside'
            self.preprocess(varStr, regionStr)

        return response

    def preprocess(self, varName, region):
        '''
            Allows the map images to be produced via the URL.
        '''
#        for step in range(FORECAST_STEPS):
#            self.plotSurfaceData(varName, step, region) 
        self.plotSurfaceData(varName, 0, region) 

    def generateConfig(self, latestFilePath, gridTime):
        '''
            Generate the configuration file
        '''
        baseDateTime = datetime(2000, 1, 1, 0, 0, 0)

        timeArray = gridTime
        timeObjArray = map(lambda(x): timedelta(hours=+x), timeArray.astype(float))

        dateTimeObjArray = [baseDateTime + x for x in timeObjArray]
        dateTimeStrArray = [{"datetime": x.strftime('%d-%m-%Y %H:%M')} for x in dateTimeObjArray]
        return dateTimeStrArray
   
    def getPlotFileName(self, varName, timeIndex, regionName):
        '''
            A helper method to put together the plot file name.
        '''
        plot_filename = '%s_%s_%s_%02d' % (currentProduct['7d'], 'current', regionName, timeIndex)
        plot_filename_fullpath = os.path.join(serverCfg['outputDir'],
                                                  plot_filename)
        raster_filename_fullpath = os.path.join(serverCfg['baseURL'],
                                                 serverCfg['rasterURL'],
                                                 plot_filename)
        return plot_filename_fullpath, raster_filename_fullpath
        

    def plotSurfaceData(self, varName, timeIndex, regionName):
        '''
            Plot wind and wave forecasts dataset, including the following three variables:
            sig_wav_ht, together with the pk_wave_dir vector overlay;
            pk_wav_per, with pk_wav_dir vector overlay;
            and
            wnd_spd, with wnd_dir vector overlay.
        ''' 
        cm = 'jet'
        cb_ticks = np.array([0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.6, 1.0, 1.5, 2.5])
        unitStr = 'm/s'
        cb_tick_fmt = '%.2f'
        plot_filename_fullpath = self.getPlotFileName(varName, timeIndex, regionName)[0]
        clabel = False
        vector = True

        plot = CurrentForecastPlotter()
        plot.plot_basemaps_and_colorbar(self.grid.lats, self.grid.lons, self.grid.data, timeIndex, 
        #                                overlay_grid = self.overlayGrid.data[timeIndex],
                                        output_filename=plot_filename_fullpath,
                                        units=unitStr, cm_edge_values=cb_ticks,
                                        cb_tick_fmt=cb_tick_fmt,
                                        cb_labels=None, cb_label_pos=None,
                                        cmp_name=cm, extend='neither', clabel=clabel, vector=vector, regionName = regionName)


        plot.wait()

    def get_overlay_variable(self, variable):
        if variable in ['sig_wav_ht', 'sig_ht_wnd_sea', 'sig_ht_sw1',  'pk_wav_per']:
            return 'mn_wav_dir'
        elif variable in ['wnd_spd']:
            return 'wnd_dir'
        return ''

class currentforecastGrid(Grid):
    """
        Inherites class Grid to implement the  method.
    """ 
    TIME_VARIABLE = ['time']

    def get_variable(self, variables, variable):
        """
        Retrieve @variable
        variable is a tuple consisting of u and v.
        """

        try:
            return variables[variable[0]], variables[variable[1]]
        except KeyError as e:
            raise GridWrongFormat(e)
 
    def load_data(self, variable):
        """
        Load the subset of @variable. Assumes spatial data with layout:
        (time, (depth)), lat, lon

        variable is a tuple consisting of u and v.

        Override to handle other data layouts.
        """

        try:
            ndim = len(variable[0].dimensions)
        except AttributeError:
            ndim = variable.ndim

        if ndim == 4:
            # data arranged time, depth, lat, lon
            return variable[0]
        elif ndim == 3:
            # data arranged time, lat, lon
            return variable[0][:], variable[1][:]
        elif ndim == 2:
            # data arranged lat, lon
            return variable
        else:
            raise GridWrongFormat()
 
    def clip_data(self, data, (lat_idx1, lat_idx2),
                                  (lon_idx1, lon_idx2),
                                  (depth_idx1, depth_idx2)):
        ndim = len(data[0].shape)
        if ndim == 3:
            return data[0][depth_idx1:depth_idx2,
                            lat_idx1:lat_idx2:self.GRID_SPACING,
                            lon_idx1:lon_idx2:self.GRID_SPACING], \
                   data[1][depth_idx1:depth_idx2,
                            lat_idx1:lat_idx2:self.GRID_SPACING,
                            lon_idx1:lon_idx2:self.GRID_SPACING] 
        elif ndim == 2:
            return data[lat_idx1:lat_idx2:self.GRID_SPACING,
                        lon_idx1:lon_idx2:self.GRID_SPACING]
        else:
            raise GridWrongFormat()

    def get_depths(self, variables):
#        return np.arange(FORECAST_STEPS)
        return [0]
