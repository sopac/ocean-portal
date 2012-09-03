#!/usr/bin/python

import bisect
import math
import numpy as np
import numpy.ma as ma

class Extractor ():
    """
    Extract point/rectangular area data.
    """

    _NEAREST_STRATEGY = 'nearest'

    _EXHAUSTIVE_STRATEGY = 'exhaustive'

    _AVERAGE_STRATEGY = 'average'
 
    _RADIUS = 2

    def __init__(self):
        """
        Initialise variables.
        """

    def getGridPoint(self, inputLat, inputLon, lats, lons, var, strategy=_NEAREST_STRATEGY):
        """
        Align the input lat/lon to the grid lat/lon. Also returns the index of the grid lat/lon.
        """
        gridPointColIndex = 0
        inputLat = float(inputLat)
        inputLon = float(inputLon)        

        latInsertIndex = bisect.bisect_left(lats, inputLat)
        #For lon, first we need to check the lon range in the dataset. if the lon range is from 0 to a number larger
        #than 180, than we should convert the input lon. Otherwise the input lon is fine.
        dataLon = inputLon
        if lons[-1] > 180:
            if inputLon < 0:
                dataLon = inputLon + 360

        nearestPoints = []
        lonInsertIndex = bisect.bisect_left(lons, dataLon)
        for latIndex in range(-self._RADIUS, self._RADIUS + 1):
            #There is no need to wrap the lat, therefore skip till the index becomes 0 
            if latInsertIndex + latIndex < 0:
                pass
            else:
                for lonIndex in range(-self._RADIUS, self._RADIUS + 1):
                    if lonInsertIndex + lonIndex < 0:
                        lonsCheck = lons[0] + lons[-1]
                        if math.fabs(lonsCheck) <= 5 or math.fabs(lonsCheck - 360) <= 5:
                        #wrap around the globe
                            nearestPoints.append((lonInsertIndex + lonIndex, latInsertIndex + latIndex))
                        else:
                            pass
                    else:
                        nearestPoints.append((lonInsertIndex + lonIndex, latInsertIndex + latIndex))



        input = (inputLon, inputLat)
        nearestPoints.sort(key=lambda coord: (input[0] - lons[coord[0]]) ** 2 + (input[1] - lats[coord[1]]) ** 2)

        if strategy == self._NEAREST_STRATEGY:
            return self._nearest_strategy(nearestPoints, lats, lons, var)
        elif strategy == self._EXHAUSTIVE_STRATEGY:
            return self._exhaustive_strategy(nearestPoints, lats, lons, var)

    def _nearest_strategy(self, sortedNearestPoints, lats, lons, var):
        return ((lats[sortedNearestPoints[0][1]], lons[sortedNearestPoints[0][0]]), sortedNearestPoints[0][::-1])

    def _exhaustive_strategy(self, sortedNearestPoints, lats, lons, var):
        result = self._nearest_strategy(sortedNearestPoints, lats, lons, var) 
        for point in sortedNearestPoints:
            if var[point[1], point[0]] is not ma.masked:
                result = ((lats[point[1]], lons[point[0]]), (point[1], point[0]))
                break
        return result

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
