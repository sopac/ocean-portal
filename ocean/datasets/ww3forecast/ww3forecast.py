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

from netCDF4 import Dataset as DS

svnDayForecast = '%s_%s.json'

#get the server dependant path configurations
serverCfg = config.get_server_config()

#get dataset dependant production information
ww3Product = productName.products['ww3forecast']

#get the plotter
#extractor = ww3ExtA.WaveWatch3Extraction()
#getGrid = GPF.Extractor()

class ww3forecast(Dataset):

    __form_params__ = {
#        'lllat': float,
#        'lllon': float,
#        'urlat': float,
#        'urlon': float,
    }
    __form_params__.update(Dataset.__form_params__)

    __required_params__ = Dataset.__required_params__ + [
#        'date',
#        'lllat',
#        'lllon',
    ]

    __periods__ = [
        '7days',
    ]

    __variables__ = [
        'sig_wav_ht',
        'pk_wav_dir',
        'wnd_spd',
    ]

    __plots__ = [
        'map'
    ]

    __subdirs__ = [
#        'monthly'
    ]

    def process(self, params):
        response = {}

        varStr = params['variable']
        periodStr = params['period']

        '''
            Check whether the data file matches the generated config file.
            If the files match, then just return the config file; otherwise
            process the data file and then return the config file.
        '''

        filename = svnDayForecast % (ww3Product['7d'], '7days')
        configFileName = serverCfg['outputDir'] + filename

#        if not os.path.exists(configFileName):
            #Generate the config file
#            config = self.generateConfig()
#            with open(configFileName, 'w') as f:
#                json.dump(config, f)
            # and associated images. 
#        else:
#            with open(configFileName, 'r') as f:
#                config = json.load(f)
        config = self.generateConfig()
        configStr = json.dumps(config) 

        if not os.path.exists(configFileName):
            response['error'] = "Error occured during the wave forecast data processing."
        else:
            response['forecast'] = configStr 
            os.utime(os.path.join(serverCfg['outputDir'], filename),
                     None)

        return response

    def generateConfig(self):
        self.serverCfg = config.get_server_config()
   
        fileName = self.serverCfg['dataDir']['ww3forecast'] + 'ww3_????????_??.nc'
        latestFilePath = max(glob.iglob(fileName), key=os.path.getctime)
        baseFileName = os.path.basename(latestFilePath)
        dateTimeValue = baseFileName[4:15]
        baseDateTime = datetime.strptime(dateTimeValue, '%Y%m%d_%H')  
     
        nc = DS(latestFilePath, 'r')

        timeArray = nc.variables['time'][:]
        timeObjArray = map(timedelta, timeArray)

        dateTimeObjArray = [baseDateTime + x for x in timeObjArray]
        dateTimeStrArray = [{"datetime": x.strftime('%d-%m-%Y %H:%M')} for x in dateTimeObjArray]
        return dateTimeStrArray

 
