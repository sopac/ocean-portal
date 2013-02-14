#
# (c) 2013 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Nick Summons <n.summons@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os.path
import bisect

import numpy as np
from netCDF4 import Dataset

from ocean import util
from ocean.util.dateRange import getMonths
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

    # a list of possible variables for latitudes
    LATS_VARIABLE = ['lat']

    # a list of possible variables for longitude
    LONS_VARIABLE = ['lon']

    def __init__(self, filename, variable,
                 latrange=(-90, 90),
                 lonrange=(-360, 360),
                 depthrange=(0, 0),
                 **kwargs):
        with Dataset(filename) as nc:

            lats = self.get_lats(nc.variables)
            lons = self.get_lons(nc.variables)
            depths = self.get_depths(nc.variables)

            indexes = self.get_indexes((lats, latrange),
                                       (lons, lonrange),
                                       (depths, depthrange))
            (lat_idx1, lat_idx2), (lon_idx1, lon_idx2), \
                                  (depth_idx1, depth_idx2) = indexes

            # subset the dimension arrays
            self.lats = lats[lat_idx1:lat_idx2]
            self.lons = lons[lon_idx1:lon_idx2]
            self.depths = depths[depth_idx1:depth_idx2]

            var = self.get_variable(nc.variables, variable)
            data = self.load_data(var, *indexes)
            self.data = np.squeeze(data)

    def _get_variable(self, variables, options):
        """
        Generic routine to try and load a variable from a list of @options
        """

        for v in options:
            try:
                return variables[v][:]
            except KeyError:
                pass

        raise GridWrongFormat("No variable in choices: %s" % options)

    def get_lats(self, variables):
        """
        Retrieve the latitudes for a dataset.
        """

        return self._get_variable(variables, self.LATS_VARIABLE)

    def get_lons(self, variables):
        """
        Retrieve the longitudes for a dataset.
        """

        return self._get_variable(variables, self.LONS_VARIABLE)

    def get_depths(self, variables):
        """
        Implement to retrieve the depths for a dataset.
        """

        return [0.]

    def get_indexes(self, *args):
        """
        Get the subsetting indexes for any number of datasets, passed as an
        iterable of elements (dataset, (min, max)).

        e.g. (lat_idx1, lat_idx2), (lon_idx1, lon_idx2) = \
            get_indexes([(lats, (latmin, latmax)), (lons, (lonmin, lonmax))])
        """

        return [get_subset_idxs(data, min, max)
                for data, (min, max) in args]

    def get_variable(self, variables, variable):
        """
        Retrieve @variable
        """

        try:
            return variables[variable]
        except KeyError as e:
            raise GridWrongFormat(e)

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

class Gridset(Grid):
    """
    Generic accessor for sets of grids where grids are separated
    temporally in different files.
    """

    SUFFIX = '.nc'

    apply_to = util.Parameterise(Grid)

    def __init__(self, path, variable, period,
                       prefix=None, suffix=SUFFIX, date=None, **kwargs):

        assert prefix is not None
        assert suffix is not None
        assert date is not None

        filename = self.get_filename(path, prefix, suffix, date, period)

        Grid.__init__(self, filename, variable, **kwargs)

    def get_filename(self, path, prefix, suffix, date, period):
        """
        Returns the filename for a grid file given the specified @path,
        @prefix, @date and @period of the file.
        """

        return os.path.join(path,
                            '%s%s%s' % (
                            prefix,
                            self.get_filename_date(date,
                                                   params=dict(period=period)),
                            suffix))

    @apply_to(period='daily')
    def get_filename_date(self, date, **kwargs):
        return date.strftime('%Y%m%d')

    @apply_to(period='monthly')
    def get_filename_date(self, date, **kwargs):
        return date.strftime('%Y%m')

    def _get_filename_date(self, date, nmonths):
        months = getMonths(date, nmonths)
        return '%imthavg_%s_%s' % (nmonths,
                                   months[0].strftime('%Y%m'),
                                   months[-1].strftime('%Y%m'))

    @apply_to(period='3monthly')
    def get_filename_date(self, date, **kwargs):
        return self._get_filename_date(date, 3)

    @apply_to(period='6monthly')
    def get_filename_date(self, date, **kwargs):
        return self._get_filename_date(date, 6)

    @apply_to(period='12monthly')
    def get_filename_date(self, date, **kwargs):
        return self._get_filename_date(date, 12)
