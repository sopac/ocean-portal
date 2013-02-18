#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import csv
import datetime
import shutil
import os.path

import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import matplotlib.dates

from ocean import config
from ocean.netcdf.extractor import Extractor, LandError
from ocean.netcdf.grid import Grid
from ocean.netcdf.surfaceplotter import SurfacePlotter
from ocean.plotter import getCopyright
from ocean.util.pngcrush import pngcrush

serverCfg = config.get_server_config()

# filenames for the respective gridfiles (in datadir/grids/)
GRIDS = {
    'alt': 'CSIRO_SatAlt_199301_201112.nc',
    'rec': 'CSIRO_Recons_195001_200912.nc',
}

# start date for the time index in each grid file
REFERENCE_DATE = {
    'alt': datetime.date(1990, 1, 1),
    'rec': datetime.date(1950, 1, 1),
}

class SeaLevelGrid(Grid):
    """
    Load a CMAR dataset using a spatial representation
    """

    def __init__(self, variable, date=None, **kwargs):

        self.date = date
        self.refdate = REFERENCE_DATE[variable]

        filename = os.path.join(serverCfg['dataDir']['sealevel'],
                                'grids',
                                GRIDS[variable])

        Grid.__init__(self, filename, variable, **kwargs)

    def get_days_elapsed(self, date):
        """
        Get the the index of the given date in the data file
        """

        timeElapsed = datetime.date(date.year, date.month, 15) - self.refdate

        return timeElapsed.days

    def get_variable(self, variables, variable):

        # find the index for the requested date
        elapsed = self.get_days_elapsed(self.date)
        time = variables['time'][:]
        time_index = np.where(time == elapsed)[0][0]

        var = Grid.get_variable(self, variables, 'height')

        return var[time_index]

class SeaLevelSeries(SeaLevelGrid):
    """
    Load a CMAR dataset using a temporal representation
    """

    def get_variable(self, variables, variable):

        @np.vectorize
        def timeidx2datetime(time):
            return self.refdate + datetime.timedelta(int(time))

        time = Grid.get_variable(self, variables, 'time')
        self.time = timeidx2datetime(time)

        return Grid.get_variable(self, variables, 'height')

    def get_indexes(self, variable,
                          (lats, (latmin, latmax)),
                          (lons, (lonmin, lonmax)),
                          *args):
        _, (latidx, lonidx) = Extractor.getGridPoint(latmin, lonmin, lats, lons,
                                                     variable[0],
                                                     strategy='exhaustive')

        return (latidx, latidx + 1), (lonidx, lonidx + 1), (0, 0)

    def load_data(self, variable, (lat_idx1, lat_idx2),
                                  (lon_idx1, lon_idx2),
                                  (depth_idx1, depth_idx2)):

        data = variable[:, lat_idx1, lon_idx1]

        if data[0] is ma.masked:
            raise LandError()

        return data

class SeaLevelSurfacePlotter(SurfacePlotter):
    DATASET = 'sealevel'
    PRODUCT_NAME = "CSIRO CMAR, Church and White"

    def get_grid(self, params={}, **kwargs):
        return SeaLevelGrid(params['variable'], date=params['date'])

    def get_ticks(self, params={}, **kwargs):
        return np.arange(-300,300.01,60.0)

    def get_ticks_format(self, params={}, **kwargs):
        return '%.0f'

    def get_units(self, params={}, **kwargs):
        return 'mm'

def plotTidalGauge(outputFilename, saveData=True, **args):
    """
    Plot tidal gauge data
    """

    tidalGaugeId = args["tidalGaugeId"]
    tidalGaugeName = args["tidalGaugeName"]
    filename = serverCfg["dataDir"]["sealevel"] + "tide_gauge/" + tidalGaugeId + "SLD.txt.tmp"

    if saveData:
        shutil.copyfile(filename, outputFilename + ".txt")

    with open(filename, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        reader.next() # skip one line

        y_max = []
        y_mean = []
        y_min = []
        x_date = []

        for line in reader:
            date = '%4d%02d' % (int(line[1]), int(line[0]))
            date = datetime.datetime.strptime(date, '%Y%m')
            x_date.append(date)
            try:
                y_max.append(float(line[5]))
                y_mean.append(float(line[6]))
                y_min.append(float(line[4]))
            except:
                y_max.append(None)
                y_mean.append(None)
                y_min.append(None)

    figure = plt.figure()
    plt.rc('font', size=8)
    plt.title('Monthly sea levels for ' + tidalGaugeName)
    plt.ylabel('Sea Level Height (metres)')
    plt.xlabel('Year')
    ax = figure.gca()
    ax.grid(True)
    ax.set_aspect(5)
    maxPlot, = ax.plot(x_date, y_max, 'r-')
    meanPlot, = ax.plot(x_date, y_mean, 'k-')
    minPlot, = ax.plot(x_date, y_min, 'b-')

    #add legend
    ax.legend([maxPlot, meanPlot, minPlot], ['Max', 'Mean', 'Min'])

    plt.axhline(y=0, color='k')
    plt.figtext(0.02, 0.02, getCopyright(), fontsize=6)
    plt.figtext(0.90, 0.05, "0.0 = Tidal Gauge Zero",
                fontsize=8, horizontalalignment='right')

    plt.savefig(outputFilename + ".png", dpi=150,
                bbox_inches='tight', pad_inches=.1)

    plt.close()
    pngcrush(outputFilename + ".png")

    return 0

def plotTimeseries(outputFilename, saveData=True, **args):
    """
    Plot altimetry/reconstruction timeseries 
    """
    tidalGaugeName = args["tidalGaugeName"]
    variable = args['variable']
    lat = args['lat']
    lon = args['lon']

    titlePrefix = {
        'alt': "Altimetry",
        'rec': "Reconstruction",
    }[variable]

    grid = SeaLevelSeries(variable,
                          latrange=(lat, lat),
                          lonrange=(lon, lon))

    if saveData:
        with open(outputFilename + ".txt", 'w') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(('# Sea Level %s for %s' % (
                             titlePrefix, tidalGaugeName),))
            writer.writerow(('# Datum: GSFC00.1',))
            writer.writerow(['Date (YYYY-MM)', '%s (mm)' % titlePrefix])

            for date, height in zip(grid.time, grid.data):
                writer.writerow([date.strftime('%Y-%m'), height])

    figure = plt.figure()
    plt.rc('font', size=8)
    plt.title("Sea Level %s for %s" % (titlePrefix, tidalGaugeName))
    plt.ylabel('Sea-Surface Height (mm)')
    plt.xlabel('Year')
    ax = figure.gca()
    ax.grid(True)
    ax.set_ylim(-350, 350)
    ax.plot(grid.time, grid.data, 'b-')
    plt.axhline(y=0, color='k')

    plt.figtext(0.02, 0.02, getCopyright(), fontsize=6)
    plt.figtext(0.90, 0.05, "Height relative to GSFC00.1",
                fontsize=8, horizontalalignment='right')

    plt.savefig(outputFilename + ".png", dpi=150,
                bbox_inches='tight', pad_inches=.1)

    plt.close()
    pngcrush(outputFilename + ".png")

    return 0
