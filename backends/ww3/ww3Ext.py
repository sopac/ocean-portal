#!/usr/bin/python


import glob
import bisect
import math
from netCDF4 import Dataset
import numpy as np

from ..util import serverConfig
from ..netcdf import extractor

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
        self.serverCfg = serverConfig.servers[serverConfig.currentServer]


    def extract(self, inputLat, inputLon, variableName, delta=_DELTA):

        files = glob.glob(self.serverCfg["dataDir"]["ww3"] + '/monthly/' +  '*.nc')
        #sort the files back in time.
        files = sorted(files, key=lambda filename: filename[-9:-3])
 
        #align the input lat/lon to grid lat/lon 
        xtractor = extractor.Extractor()
        nc = Dataset(files[0], 'r')
        lats = nc.variables['y'][:]
        lons = nc.variables['x'][:]
        var = nc.variables[variableName][0]
        (gridLat, gridLon), (gridLatIndex, gridLonIndex) = xtractor.getGridPoint(inputLat, inputLon, lats, lons, var)

        nc.close()
            
        if (delta == 0):
            latTopIndex = gridLatIndex
            latBottomIndex = gridLatIndex
            lonLeftIndex = gridLonIndex
            lonRightIndex = gridLonIndex
        else:
            latBottomIndex = gridLatIndex - delta
            if latBottomIndex < 0:
                latBottomIndex = 0
            latTopIndex = gridLatIndex + delta
            if latTopIndex > len(lats):
                latTopIndex = len(lats)

            lonLeftIndex = gridLonIndex - delta
            if lonLeftIndex < 0:
                lonLeftIndex = 0
            lonRightIndex = gridLonIndex + delta
            if lonRightIndex > len(lons):
                lonRightIndex = len(lons)
 
        latBottom = lats[latBottomIndex]
        latTop = lats[latTopIndex]
        lonLeft = lons[lonLeftIndex]
        lonRight = lons[lonRightIndex] #this doesn't consider the IDL wrap

        latmin = lats >= latBottom
        latmax = lats <= latTop
        lonmin = lons >= lonLeft
        lonmax = lons <= lonRight

        latrange = latmin & latmax
        lonrange = lonmin & lonmax
        
        latsLons = []
        for lat in lats[latrange]:
            for lon in lons[lonrange]:
                latsLons.append(str(lat) + ', ' + str(lon))

        timeseries = []
        latLonValues = []
        gridValues = []
        for file in files:
            nc = Dataset(file, 'r')
   

            #print values
            var = nc.variables[variableName][0]

            xrange = var[latrange]
            grid = xrange[:, lonrange] 
            timeseries.append(file[-9:-3])
            gridValues.append(grid.flatten())
            latLonValues.append(var[gridLatIndex, gridLonIndex])
            nc.close()

        return timeseries, latsLons, latLonValues, gridValues, (gridLat, gridLon)

    def writeOutput(self, fileName, latsLons, timeseries, gridValues):
    
        output = open(fileName, 'w')
        #write lats and lons table header
        output.write('\t')
        for latlon in latsLons:
            output.write(latlon + '\t')
        output.write('\n')
        for timestamp, row in zip(timeseries, gridValues):
            output.write(timestamp + '\t')
            for col in row:
                output.write(str(col))
                output.write('\t')
            output.write('\n')

        output.close()
