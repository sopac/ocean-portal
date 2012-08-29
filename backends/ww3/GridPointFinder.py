#!/usr/bin/python
import glob
import bisect
import ocean.util as util
import math
import numpy as np
from netCDF4 import Dataset

class Extractor ():
    """
    Extract point/rectangular area data.
    """

    def __init__(self):
        """
        Initialise variables.
        """
        self.serverCfg = util.get_server_config()

    def getGridPoint(self, inputLat, inputLon):
        """
        Align the input lat/lon to the grid lat/lon. Also returns the index of the grid lat/lon.
        """
        file = glob.glob(self.serverCfg["dataDir"]["ww3"] + 'monthly/' + 'ww3_outf_197901.nc')
        nc = Dataset(file[0], 'r')
        lats  = nc.variables['y'][:] 
        lons = nc.variables['x'][:]
        gridPointColIndex = 0
        inputLat = float(inputLat)
        inputLon = float(inputLon)        
        latInsertIndex = bisect.bisect_left(lats,inputLat)
        gridLatIndex = latInsertIndex 
        if latInsertIndex == 0:
            gridLat = lats[0]
        elif math.fabs(lats[latInsertIndex-1] - inputLat) - math.fabs(lats[latInsertIndex] - inputLat) > 0: 
            gridLat = lats[latInsertIndex]
        else:
            gridLatIndex = latInsertIndex - 1
            gridLat = lats[gridLatIndex]
           

        lonInsertIndex = bisect.bisect_left(lons,inputLon)
        gridLonIndex = lonInsertIndex
        if lonInsertIndex == 0:
            gridLon = lons[0]
        elif math.fabs(lons[lonInsertIndex-1] - inputLon) - math.fabs(lons[lonInsertIndex] - inputLon) > 0: 
            gridLon = lons[lonInsertIndex]
        else:
            gridLonIndex = lonInsertIndex - 1
            gridLon = lons[gridLonIndex]

        return gridLat, gridLon

    def extract(self, data, lats, lons, latTop, latBottom, lonLeft, lonRight):
        """
        Extract an area of data from the gridded data.
        """
        latmin = lats >= latBottom
        latmax = lats <= latTop
        lonmin = lons >= lonLeft
        lonmax = lons <= lonRight

        latrange = latmin & latmax
        lonrange = lonmin & lonmax 

        latSlice = sst[latrange]
        extracted = latSlice[:, lonrange]
        return extracted
