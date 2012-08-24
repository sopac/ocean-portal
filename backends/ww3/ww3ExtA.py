#!/usr/bin/python


import glob
import bisect
import math
from netCDF4 import Dataset
import numpy as np

import ocean.util as util
import extractor

class WaveWatch3Extraction ():
    """
    Extract wave watch 3 point/rectangular area data.
    """

    serverCfg = None

    _DELTA = 0

    def __init__(self):
        """
        Initialise variables.
        """
        self.serverCfg = util.get_server_config()


    def extract(self, inputLat, inputLon, variableName, delta=_DELTA):
        k1 = 31
        k2 = 62
        files = glob.glob(self.serverCfg["dataDir"]["ww3"] + '/monthly/' +  '*.nc')
        #sort the files back in time.
        files = sorted(files, key=lambda filename: filename[-5:-3])
        filez =  files[k1:k2]
        filez = sorted(filez, key=lambda filename: filename[-9:-3]) 
        #align the input lat/lon to grid lat/lon
        xtractor = extractor.Extractor()
        nc = Dataset(filez[0], 'r')
        lats = nc.variables['y'][:]
        lons = nc.variables['x'][:]
        (gridLat, gridLon), (gridLatIndex, gridLonIndex) = xtractor.getGridPoint(inputLat, inputLon, lats, lons)
        gridValues = []
        latLonValues = []
        timeseries = []
        latsLons = str(gridLat) + ' ' + str(gridLon) 
        nc.close()
            
        for file in filez:
            nc = Dataset(file, 'r') 		 
            #print values  
            var = nc.variables[variableName]
            point = var[1::4,gridLatIndex,gridLonIndex]
            tvar = nc.variables['time1']
            time = tvar[1::4]   
            timeseries = np.append(timeseries,time)
            latLonValues = np.append(latLonValues,point)
            nc.close()                  
        return timeseries, latsLons, latLonValues, gridValues, (gridLat, gridLon)

    def writeOutput(self, fileName, latsLons, timeseries, gridValues):
    
        output = open(fileName, 'w')
        #write lats and lons table header
        output.write('\t')
        #for latlon in latsLons:
        output.write(latsLons + '\t')
        output.write('\n')
        for timestamp, row in zip(timeseries, gridValues):
            output.write(timestamp + '\t')
            for col in row:
                output.write(str(col))
                output.write('\t')
            output.write('\n')

        output.close()