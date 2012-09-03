#!/usr/bin/python

import bisect
import math
import numpy as np

class Extractor ():
    """
    Extract point/rectangular area data.
    """

    def __init__(self):
        """
        Initialise variables.
        """

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
