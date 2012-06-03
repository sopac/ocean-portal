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

    def getGridPoint(self, inputLat, inputLon, lats, lons):
        gridPointColIndex = 0
        inputLat = float(inputLat)
        inputLon = float(inputLon)        
        latInsertIndex = bisect.bisect_left(lats, inputLat)
        gridLatIndex = latInsertIndex 
        if latInsertIndex == 0:
            gridLat = lats[0]
        elif math.fabs(lats[latInsertIndex-1] - inputLat) - math.fabs(lats[latInsertIndex] - inputLat) > 0: 
            gridLat = lats[latInsertIndex]
        else:
            gridLatIndex = latInsertIndex - 1
            gridLat = lats[gridLatIndex]
           

        lonInsertIndex = bisect.bisect_left(lons, inputLon)
        gridLonIndex = lonInsertIndex
        if lonInsertIndex == 0:
            gridLon = lons[0]
        elif math.fabs(lons[lonInsertIndex-1] - inputLon) - math.fabs(lons[lonInsertIndex] - inputLon) > 0: 
            gridLon = lons[lonInsertIndex]
        else:
            gridLonIndex = lonInsertIndex - 1
            gridLon = lons[gridLonIndex]

        return  (gridLat, gridLon), (gridLatIndex, gridLonIndex)

