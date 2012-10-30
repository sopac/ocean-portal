#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import datetime
import csv
import shutil
import datetime

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates

from ocean import util, config
from ocean.config import regionConfig
from ocean.netcdf import plotter, extractor
from ocean.util.pngcrush import pngcrush

import sealevelConfig as rc

class SeaLevelPlotter ():
    """ 
    Sea-leve plotter is specifically designed to plot the altimetry and reconstruction
    netcdf data
    """
    config = None
    serverCfg = None
    referenceDate = None
    altRefDate = datetime.date(1990, 1, 1)
    recRefDate = datetime.date(1950, 1, 1)

    def __init__(self):
        """Initialise the plotter by getting the settings ready for the plotting.""" 
        self.config = rc.SealevelConfig()
        self.serverCfg = config.get_server_config()

    def plot(self, outputFilename, **args):
        """
        Plot the thumbnail image and also the east and west map images.
        """
        cntLabel = False
        variable = args['variable']
        area = args['area']

        if variable == 'alt':
            filename = self.serverCfg["dataDir"]["sealevel"] + "grids/" + "CSIRO_SatAlt_199301_201112"
            self.referenceDate = self.altRefDate
        elif variable == 'rec':
            filename = self.serverCfg["dataDir"]["sealevel"] + "grids/" + "CSIRO_Recons_195001_200912"
            self.referenceDate = self.recRefDate
        else:
            return -1
        
        filename = filename + ".nc"
        dataset = Dataset(filename, 'r')
        time = dataset.variables["time"]
        height = dataset.variables[self.config.getVariableType(variable)][self.getDateIndex(time[:].tolist(), args["date"])]
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['lon'][:]

        delon = lons[1]-lons[0]; delat = lats[1]-lats[0]
        lons2 = (lons - 0.5*delon).tolist()
        lons2.append(lons2[-1]+delon)
        lons2 = np.array(lons2,np.float64)
        lats2 = (lats - 0.5*delat).tolist()
        lats2.append(lats2[-1]+delat)
        lats2 = np.array(lats2,np.float64)

        date = args['date']
        args['formattedDate'] = date.strftime('%B %Y')

        resolution='h'
        if not area=='pac':
           resolution='f'

        plot = plotter.Plotter()
        #plot.plot(height, lats, lons, variable, self.config, outputFilename,\
        #          regionConfig.regions[area][1]["llcrnrlat"],\
        #          regionConfig.regions[area][1]["llcrnrlon"],\
        #          regionConfig.regions[area][1]["urcrnrlat"],\
        #          regionConfig.regions[area][1]["urcrnrlon"],\
        #          res=resolution, centerLabel=cntLabel, **args)
        output_filename = self.serverCfg["outputDir"] + outputFilename + '.png'
        regionLongName = regionConfig.regions[area][2]
        title = regionLongName + '\n' + self.config.getTitle(variable) + args['formattedDate']
        units = self.config.getUnit(variable)
        cmap_name = self.config.getColorMap(variable)
        plot.plot_surface_data(lats, lons, height,
                               regionConfig.regions[area][1]["llcrnrlat"],
                               regionConfig.regions[area][1]["urcrnrlat"],
                               regionConfig.regions[area][1]["llcrnrlon"],
                               regionConfig.regions[area][1]["urcrnrlon"],
                               output_filename, title=title, units=units,
                               cmp_name=cmap_name, cm_edge_values=np.arange(-300,300.01,60.0),
                               cb_tick_fmt="%.0f")
        plot.plot_basemaps_and_colorbar(lats, lons, height,
                                        output_filename=output_filename,
                                        units=units, cm_edge_values=np.arange(-300,300.01,60.0),
                                        cb_tick_fmt="%.0f",
                                        cmp_name=cmap_name)
        plot.wait()

        dataset.close()

        return 0

    def getDateIndex(self, timeList, date):
        """
        Get the the index of the given date in the data file
        """

        timeElapsed = datetime.date(date.year, date.month, 15) - self.referenceDate
        index = timeList.index(timeElapsed.days)
        return index


    def plotTidalGauge(self, outputFilename, saveData=True, **args):
        """
        Plot tidal gauge data
        """

        tidalGaugeId = args["tidalGaugeId"]
        tidalGaugeName = args["tidalGaugeName"]
        filename = self.serverCfg["dataDir"]["sealevel"] + "tide_gauge/" + tidalGaugeId + "SLD.txt.tmp"
 
        if saveData:
            shutil.copyfile(filename, outputFilename + ".txt")

        file = open(filename, 'r')
        reader = csv.reader(file, delimiter='\t')
        reader.next()
        y_max = []
        y_mean = []
        y_min = []
        x_date = []
        for line in reader:
            date = '%4d%02d' % (int(line[1]), int(line[0]))
            date = datetime.datetime.strptime(date, '%Y%m')
            x_date.append(matplotlib.dates.date2num(date))
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
#        ax.set_aspect(5)
        maxPlot, = ax.plot_date(x_date, y_max, 'r-') 
        meanPlot, = ax.plot_date(x_date, y_mean, 'k-') 
        minPlot, = ax.plot_date(x_date, y_min, 'b-')

        #add legend
        ax.legend([maxPlot, meanPlot, minPlot], ['Max', 'Mean', 'Min'])

        plt.axhline(y=0, color='k')
        plt.figtext(0.02, 0.02, plotter.getCopyright(), fontsize=6)
        plt.figtext(0.90, 0.05, "0.0 = Tidal Gauge Zero",
                    fontsize=8, horizontalalignment='right')

        plt.savefig(outputFilename + ".png", dpi=150, bbox_inches='tight', pad_inches=.1)

        plt.close()
        file.close()

        pngcrush(outputFilename + ".png")

        return 0

    def plotTimeseries(self, outputFilename, saveData=True, **args):
        """
        Plot altimetry/reconstruction timeseries 
        """
        tidalGaugeName = args["tidalGaugeName"]
        variable = args['variable']
        lat = args["lat"]
        lon = args["lon"]
        titlePrefix = None
        aspectRatio = None
        if variable == 'alt':
            filename = self.serverCfg["dataDir"]["sealevel"] + "grids/" + "CSIRO_SatAlt_199301_201112"
            titlePrefix = "Altimetry"
            self.referenceDate = self.altRefDate
            aspectRatio = 2.5
        elif variable == 'rec':
            filename = self.serverCfg["dataDir"]["sealevel"] + "grids/" + "CSIRO_Recons_195001_200912"
            titlePrefix = "Reconstruction"
            self.referenceDate = self.recRefDate
            aspectRatio = 8
        else:
            return -1
        
        filename = filename + ".nc" 
        dataset = Dataset(filename, 'r')
        time = dataset.variables["time"]
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['lon'][:]
        var = dataset.variables[self.config.getVariableType(variable)][0]
        
        xtractor = extractor.Extractor()
        (gridLat, gridLon), (latIndex, lonIndex) = xtractor.getGridPoint(lat, lon, lats, lons, var, strategy='exhaustive')
        y_height = dataset.variables[self.config.getVariableType(variable)][:, latIndex, lonIndex]

        
        x_date = []
        date_label = []
        for date in time[:].tolist():
            date_label.append(self.referenceDate + datetime.timedelta(date))
            x_date.append(matplotlib.dates.date2num(self.referenceDate + datetime.timedelta(date))) 
 
        if saveData:
            file = open(outputFilename + ".txt", 'w')
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(('# Sea Level %s for %s' % (titlePrefix, tidalGaugeName),))
            writer.writerow(('# Datum: GSFC00.1',))
            writer.writerow(['Date (YYYY-MM)', '%s (mm)' % titlePrefix])

            for date, height in zip(date_label, y_height):
                writer.writerow([date.strftime('%Y-%m'), height])
            file.close()

        figure = plt.figure()
        plt.rc('font', size=8)
        plt.title("Sea Level %s for %s" % (titlePrefix, tidalGaugeName))
        plt.ylabel('Sea-Surface Height (mm)')
        plt.xlabel('Year')
        ax = figure.gca()
        ax.grid(True)
#        ax.set_ylim(-350, 350)
#        ax.set_aspect(aspectRatio)
        ax.plot_date(x_date, y_height, 'b-') 
        plt.axhline(y=0, color='k')

        plt.figtext(0.02, 0.02, plotter.getCopyright(), fontsize=6)
        plt.figtext(0.90, 0.05, "Height relative to GSFC00.1",
                    fontsize=8, horizontalalignment='right')

        plt.savefig(outputFilename + ".png", dpi=150, bbox_inches='tight', pad_inches=.1)

        plt.close()
        dataset.close()

        pngcrush(outputFilename + ".png")

        return 0
