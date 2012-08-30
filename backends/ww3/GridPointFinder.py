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
        return lats, lons

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
