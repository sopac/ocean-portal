#!/usr/bin/python



import datetime
from netCDF4 import Dataset
import numpy as np
import glob

import ersstConfig as ec
import smooth as sm

import ocean.util as util
from ..netcdf import plotter
from ..util import regionConfig
from ..util import dateRange


class ErsstPlotter ():
    """ 
    Ersst plotter is specifically designed to plot the ersst
    netcdf data
    """
    config = None
    serverCfg = None

    def __init__(self):
       """Initialise the configurations""" 
       self.config = ec.ErsstConfig()
       self.serverCfg = util.get_server_config()

    def plot(self, outputFilename, **args):
        """
        Plot the thumbnail image and also the east and west map images.
        """
        variable = args["variable"]
        date = args["date"] 
        area = args["area"]
        period = args["period"]
 
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])

        inputDate = datetime.date(year, month, day)
 
	centerLabel = False

	if variable == 'mean' or variable == 'anom':
            if period=='monthly':
                filename = self.serverCfg["dataDir"]["ersst"] + period + "/" + "ersst." + date[:6]
		title = self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(inputDate)
            elif period=='3monthly' or period == '6monthly': 
            	filename = self.serverCfg["dataDir"]["ersst"] + "/" + period + "/ersst." + date[:6] + "ave"
		title = self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(dateRange.getMonths(date, period[:1])[0]) \
                      + " to "\
                      + util.format_old_date(inputDate)
            elif period == '12monthly': 
            	filename = self.serverCfg["dataDir"]["ersst"] + "/" + period + "/ersst." + date[:6] + "ave"
		title = self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(dateRange.getMonths(date, period[:2])[0])\
                      + " to "\
                      + util.format_old_date(inputDate)
	elif variable=='dec':
	    centerLabel = True
            baseYear = args["baseYear"]
            if period=='monthly':
                filename = self.serverCfg["dataDir"]["ersst"] + "decile/" + baseYear + "/" + period + "/" + "ersst." + date[:6] + "dec"
		title = self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(inputDate)
            elif period=='3monthly' or period == '6monthly': 
                filename = self.serverCfg["dataDir"]["ersst"] + "decile/" + baseYear + "/" + period + "/" + "ersst." + date[:6] + "dec"
		title = self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(dateRange.getMonths(date, period[:1])[0]) \
                      + " to "\
                      + util.format_old_date(inputDate)
            elif period == '12monthly': 
                filename = self.serverCfg["dataDir"]["ersst"] + "decile/" + baseYear + "/" + period + "/" + "ersst." + date[:6] + "dec"
		title = self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(dateRange.getMonths(date, period[:2])[0]) \
                      + " to "\
                      + util.format_old_date(inputDate)

	elif variable=='trend':
            baseYear = args["baseYear"]
            if period=='monthly':
                filename = self.serverCfg["dataDir"]["ersst"] + "trend/" + period\
                         + "/" + baseYear + "/"  + "ersst." + period\
                         + "_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]lin" + date[4:6]
		title = self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + inputDate.strftime('%B')\
                      + " (" + baseYear + " - " + inputDate.strftime('%Y') + ")"
            elif period=='3monthly' or period == '6monthly': 
                filename = self.serverCfg["dataDir"]["ersst"] + "trend/" + period\
                         + "/" + baseYear + "/"  + "ersst." + period\
                         + "_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]lin" + date[4:6]
		title = self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + dateRange.getMonths(date, period[:1])[0].strftime('%B')\
                      + " to "\
                      + inputDate.strftime('%B')\
                      + " (" + baseYear + " - " + inputDate.strftime('%Y') + ")"
            elif period == '12monthly': 
                filename = self.serverCfg["dataDir"]["ersst"] + "trend/" + period\
                         + "/" + baseYear + "/"  + "ersst." + period\
                         + "_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]lin" + date[4:6]
		title = self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + dateRange.getMonths(date, period[:2])[0].strftime('%B')\
                      + " to "\
                      + inputDate.strftime('%B')\
                      + " (" + baseYear + " - " + inputDate.strftime('%Y') + ")"
        else:
            return -1
	
        filename = filename + ".nc" 
        filename = glob.glob(filename)[0]
        dataset = Dataset(filename, 'r')

        sst = dataset.variables[self.config.getVariableType(variable)][0][0]
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['lon'][:]
        
        lons = np.array(lons,np.float64)
        lats = np.array(lats,np.float64)

	sst = sm.smooth(sst, 5)

	contourLines = True

        resolution='h'
        if not area=='pac':
           resolution='f'

        plot = plotter.Plotter()
        plot.contour(sst, lats, lons, variable, self.config, outputFilename, title,\
                  regionConfig.regions[area][1]["llcrnrlat"],\
                  regionConfig.regions[area][1]["llcrnrlon"],\
                  regionConfig.regions[area][1]["urcrnrlat"],\
                  regionConfig.regions[area][1]["urcrnrlon"],\
		  "cyl", contourLines, centerLabel)
        plot.contourBasemapEast(sst, lats, lons, variable, self.config, outputFilename)
        plot.contourBasemapWest(sst, lats, lons, variable, self.config, outputFilename)
        plot.plotScale(sst, variable, self.config, outputFilename)

        dataset.close()
        
        return 0


