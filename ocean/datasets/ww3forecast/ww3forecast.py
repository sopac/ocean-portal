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

from ocean import util, config
from ocean.config import productName
#from ocean.netcdf.extractor import Extractor
from ocean.datasets import Dataset
from ww3forecastPlotter import Ww3ForecastPlotter, COMMON_FILES
from ocean.netcdf import Grid



svnDayForecast = '%s_%s.json'

#get the server dependant path configurations
serverCfg = config.get_server_config()

#get dataset dependant production information
ww3Product = productName.products['ww3forecast']

#number of forecast steps
FORECAST_STEPS = 25

class ww3forecast(Dataset):

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
        'sig_wav_ht',
        'sig_ht_wnd_sea',
        'sig_ht_sw1',
        'pk_wav_per',
        'wnd_spd',
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

        filename = svnDayForecast % (ww3Product['7d'], '7days')
        configFileName = serverCfg['outputDir'] + filename

        fileName = serverCfg['dataDir']['ww3forecast'] + 'ww3_????????_??.nc'
        latestFilePath = max(glob.iglob(fileName), key=os.path.getctime)

        self.grid = ww3forecastGrid(latestFilePath, latestFilePath, varStr, (-90, 90), (0, 360))
 
        self.overlayGrid = ww3forecastGrid(latestFilePath, latestFilePath, self.get_overlay_variable(varStr), (-90, 90), (0, 360))

        config = self.generateConfig(latestFilePath, self.grid.time)
        configStr = json.dumps(config) 

        response['forecast'] = configStr 
#        response['mapimg'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['mapimg']
#        response['scale'] = self.getPlotFileName(varStr, 0, regionStr)[1] + COMMON_FILES['scale']
        response['mapimg'] = self.getPlotFileName(varStr, 0, 'pac')[1] + COMMON_FILES['mapimg']
        response['scale'] = self.getPlotFileName(varStr, 0, 'pac')[1] + COMMON_FILES['scale']
#        os.utime(os.path.join(serverCfg['outputDir'], filename), None)

        if ('mode' in params) and (params['mode'] == 'preprocess'):
            response['preproc'] = 'inside'
            self.preprocess(varStr, regionStr)

        return response

    def preprocess(self, varName, region):
        '''
            Allows the map images to be produced via the URL.
        '''
        for step in range(FORECAST_STEPS):
            self.plotSurfaceData(varName, step, region) 

    def generateConfig(self, latestFilePath, gridTime):
        '''
            Generate the configuration file
        '''
        baseFileName = os.path.basename(latestFilePath)
        dateTimeValue = baseFileName[4:15]
        baseDateTime = datetime.strptime(dateTimeValue, '%Y%m%d_%H')  
        
        timeArray = gridTime
        timeObjArray = map(timedelta, timeArray)

        dateTimeObjArray = [baseDateTime + x for x in timeObjArray]
        dateTimeStrArray = [{"datetime": x.strftime('%d-%m-%Y %H:%M')} for x in dateTimeObjArray]
        return dateTimeStrArray
   
    def getPlotFileName(self, varName, timeIndex, regionName):
        '''
            A helper method to put together the plot file name.
        '''
        plot_filename = '%s_%s_%s_%02d' % (ww3Product['7d'], varName, regionName, timeIndex)
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
        if varName == 'sig_ht_sw1':
            cm = 'wav_cm'
            cb_ticks = 'sig'
            unitStr = 'Metres'
            cb_tick_fmt = '%.1f'
            plot_filename_fullpath = self.getPlotFileName(varName, timeIndex, regionName)[0]
            clabel = False
            vector = True
        elif varName == 'pk_wav_per':
            cm = 'wav_cm'
            cb_ticks = 'pk'
            unitStr = 'Seconds'
            cb_tick_fmt = '%2d'
            plot_filename_fullpath = self.getPlotFileName(varName, timeIndex, regionName)[0]
            clabel = True 
            vector = False
        elif varName == 'wnd_spd':
            cm = 'wnd_cm'
            cb_ticks = 'wnd'
            unitStr = 'Speed(kts)'
            cb_tick_fmt = '%3d'
            plot_filename_fullpath = self.getPlotFileName(varName, timeIndex, regionName)[0]
            clabel = False 
            vector = True
            self.grid.data = self.grid.data[timeIndex] * 1.94384449
        elif varName == 'sig_wav_ht':
            cm = 'wav_cm'
            cb_ticks = 'sig'
            unitStr = 'Metres'
            cb_tick_fmt = '%.1f'
            plot_filename_fullpath = self.getPlotFileName(varName, timeIndex, regionName)[0]
            clabel = False
            vector = True
        elif varName == 'sig_ht_wnd_sea':
            cm = 'wav_cm'
            cb_ticks = 'sig'
            unitStr = 'Metres'
            cb_tick_fmt = '%.1f'
            plot_filename_fullpath = self.getPlotFileName(varName, timeIndex, regionName)[0]
            clabel = False
            vector = True

        print plot_filename_fullpath
        plot = Ww3ForecastPlotter()
        plot.plot_basemaps_and_colorbar(self.grid.lats, self.grid.lons, self.grid.data[timeIndex],
                                        overlay_grid = self.overlayGrid.data[timeIndex],
                                        output_filename=plot_filename_fullpath,
                                        units=unitStr, cm_edge_values=cb_ticks,
                                        cb_tick_fmt=cb_tick_fmt,
                                        cb_labels=None, cb_label_pos=None,
                                        cmp_name=cm, extend='neither', clabel=clabel, vector=vector)


        plot.wait()

    def get_overlay_variable(self, variable):
        if variable in ['sig_wav_ht', 'sig_ht_wnd_sea', 'sig_ht_sw1',  'pk_wav_per']:
            return 'mn_wav_dir'
        elif variable in ['wnd_spd']:
            return 'wnd_dir'
        return ''

class ww3forecastGrid(Grid):
    """
        Inherites class Grid to implement the get_variable method.
    """ 
    TIME_VARIABLE = ['time']
 
    def load_data(self, variable, (lat_idx1, lat_idx2),
                                  (lon_idx1, lon_idx2),
                                  (depth_idx1, depth_idx2)):
        """
        Load the subset of @variable. Assumes spatial data with layout:
        (time, (depth)), lat, lon

        Override to handle other data layouts.
        """

        try:
            ndim = len(variable.dimensions)
        except AttributeError:
            ndim = variable.ndim

        if ndim == 4:
            # data arranged time, depth, lat, lon
            return variable[0,
                            depth_idx1:depth_idx2,
                            lat_idx1:lat_idx2:self.GRID_SPACING,
                            lon_idx1:lon_idx2:self.GRID_SPACING,]
        elif ndim == 3:
            # data arranged time, lat, lon
            return variable[:,
                            lat_idx1:lat_idx2:self.GRID_SPACING,
                            lon_idx1:lon_idx2:self.GRID_SPACING,]
        elif ndim == 2:
            # data arranged lat, lon
            return variable[lat_idx1:lat_idx2:self.GRID_SPACING,
                            lon_idx1:lon_idx2:self.GRID_SPACING,]
        else:
            raise GridWrongFormat()
 
        
