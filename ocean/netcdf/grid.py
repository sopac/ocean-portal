#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Nick Summons <n.summons@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import bisect

import numpy as np
from netCDF4 import Dataset

from ocean.core import ReportableException

class GridWrongFormat(ReportableException):
    pass

def get_subset_idxs(x, x_min, x_max):

    if x_min == x_max:
        closest_idx = np.abs(np.array(x) - x_min).argmin()
        return closest_idx, closest_idx + 1

    # assuming that x is sorted, find indexes to the left of x_min and the
    # right of x_max
    start_idx = bisect.bisect_left(x, x_min)
    end_idx = bisect.bisect_right(x, x_max)

    return start_idx, end_idx

class Grid(object):
    """
    Generic accessor for NetCDF grids. Able to handle data referenced in
    multiple dimensions given the specified subset.

    Subclass this class to handle specific grid layouts.
    """

    def __init__(self, filename, variable, latrange=(-90, 90),
                                           lonrange=(-180, 180),
                                           depthrange=(0, 0)):
        with Dataset(filename) as nc:

            lats = self.get_lats(nc.variables)
            lons = self.get_lons(nc.variables)
            depths = self.get_depths(nc.variables)

            # calculate the data subset indexes
            lat_min, lat_max = latrange
            lon_min, lon_max = lonrange
            depth_min, depth_max = depthrange

            lat_idx1, lat_idx2 = get_subset_idxs(lats, lat_min, lat_max)
            lon_idx1, lon_idx2 = get_subset_idxs(lons, lon_min, lon_max)
            depth_idx1, depth_idx2 = get_subset_idxs(depths,
                                                     abs(depth_min),
                                                     abs(depth_max))

            # subset the dimension arrays
            self.lats = lats[lat_idx1:lat_idx2]
            self.lons = lons[lon_idx1:lon_idx2]
            self.depths = depths[depth_idx1:depth_idx2]

            var = self.get_variable(nc.variables, variable)
            data = self.load_data(var, (lat_idx1, lat_idx2),
                                       (lon_idx1, lon_idx2),
                                       (depth_idx1, depth_idx2))
            self.data = np.squeeze(data)

    def get_lats(self, variables):
        try:
            return variables['lat'][:]
        except KeyError as e:
            raise GridWrongFormat(e)

    def get_lons(self, variables):
        try:
            return variables['lon'][:]
        except KeyError as e:
            raise GridWrongFormat(e)

    def get_depths(self, variables):
        return [0.]

    def get_variable(self, variables, variable):
        try:
            return variables[variable]
        except KeyError as e:
            raise GridWrongFormat(e)

    def load_data(self, variable, (lat_idx1, lat_idx2),
                                  (lon_idx1, lon_idx2),
                                  (depth_idx1, depth_idx2)):
        ndim = len(variable.dimensions)

        if ndim == 4:
            # data arranged time, depth, lat, lon
            return variable[0,
                            depth_idx1:depth_idx2,
                            lat_idx1:lat_idx2,
                            lon_idx1:lon_idx2]

        elif ndim == 3:
            # data arranged time, lat, lon
            return variable[0,
                            lat_idx1:lat_idx2,
                            lon_idx1:lon_idx2]
        elif ndim == 2:
            # data arranged lat, lon
            return variable[lat_idx1:lat_idx2,
                            lon_idx1:lon_idx2]
        else:
            raise GridWrongFormat()
