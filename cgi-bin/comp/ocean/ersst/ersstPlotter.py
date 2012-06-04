#!/usr/bin/python


from ..netcdf import plotter

from netCDF4 import Dataset
import numpy as np
import ersstConfig as ec
from ..util import serverConfig
from ..util import regionConfig
import smooth as sm
import datetime
from dateutil.relativedelta import *


class ErsstPlotter ():
    """ 
    Ersst plotter is specifically designed to plot the ersst
    netcdf data
    """
    config = None
    serverCfg = None

    def __init__(self):
       """Does nothing""" 
       self.config = ec.ErsstConfig()
       self.serverCfg = serverConfig.servers[serverConfig.currentServer]

    def plot(self, outputFilename, variable, date, area, period, baseYear=None):
        """
        Plot the thumbnail image and also the east and west map images.
        """
	titlehead = []

	#**args = (variable, date, area, period)

	year = int(date[0:4])
    	month = int(date[4:6])
    	day = int(date[6:8])

    	initDate = datetime.date(year, month, day)
	

	if period=='monthly':
	    titlehead = "Monthly Average "
	elif period=='3monthly':
	    titlehead = "Three Month Average "
	    startDate = initDate + relativedelta(months=-2)
	elif period=='6monthly':
	    titlehead = "Six Month Average "
	    startDate = initDate + relativedelta(months=-5)
	elif period=='12monthly':
	    titlehead = "Twelve Month Average "
	    dateTwelve = initDate + relativedelta(months=-11)
	
	firstmonth = "%02d" % (startDate.month)
	monthmap = {'01':'January', '02':'February', \
            '03': 'March', '04': 'April', \
            '05': 'May', '06': 'June', \
            '07': 'July', '08': 'August', \
            '09': 'September', '10': 'October', \
            '11': 'November', '12': 'December'}
	cmonth = monthmap[date[4:6]]
	smonth = monthmap[firstmonth]

	if variable=='mean':
	    centerLabel = False
            if period=='monthly':
                filename = self.serverCfg["dataDir"] + period + "/" + "ersst." + date[:6]
		title = titlehead + self.config.getTitle(variable) + cmonth + ' ' + date[0:4]
            elif period=='3monthly': 
            	filename = self.serverCfg["dataDir"] + period + "/" + "ersst." + date[:6] + "ave"
		title = titlehead + self.config.getTitle(variable) + smonth + " %s" % (startDate.year) + ' to ' + cmonth + ' ' + date[0:4]
            elif period=='6monthly':
             	filename = self.serverCfg["dataDir"] + period + "/" + "ersst." + date[:6] + "ave"
		title = titlehead + self.config.getTitle(variable) + smonth + " %s" % (startDate.year) + ' to ' + cmonth + ' ' + date[0:4]
            elif period=='12monthly':
            	filename = self.serverCfg["dataDir"] + period + "/" + "ersst." + date[:6] + "ave"
	    	title = titlehead + self.config.getTitle(variable) + smonth + " %s" % (startDate.year) + ' to ' + cmonth + ' ' + date[0:4]
	elif variable=='anom':
	    centerLabel = False
	    if period=='monthly':
                filename = self.serverCfg["dataDir"] + period + "/" + "ersst." + date[:6]
		title = titlehead + self.config.getTitle(variable) + cmonth + ' ' + date[0:4]
            elif period=='3monthly':
                filename = self.serverCfg["dataDir"] + period + "/" + "ersst." + date[:6] + "ave"
		title = titlehead + self.config.getTitle(variable) + smonth + " %s" % (startDate.year) + ' to ' + cmonth + ' ' + date[0:4]
            elif period=='6monthly':
                filename = self.serverCfg["dataDir"] + period + "/" + "ersst." + date[:6] + "ave"
		title = titlehead + self.config.getTitle(variable) + smonth + " %s" % (startDate.year) + ' to ' + cmonth + ' ' + date[0:4]
            elif period=='12monthly':
                filename = self.serverCfg["dataDir"] + period + "/" + "ersst." + date[:6] + "ave"
	    	title = titlehead + self.config.getTitle(variable) + smonth + " %s" % (startDate.year) + ' to ' + cmonth + ' ' + date[0:4]	
	elif variable=='dec':
	    centerLabel = True
	    if period=='monthly':
                filename = self.serverCfg["dataDir"] + "decile" + "/" + baseYear + "/" + period + "/" + "ersst." + date[:6] + "dec"
		title = titlehead + self.config.getTitle(variable) + cmonth + ' ' + date[0:4]
	    elif period=='3monthly':
		filename = self.serverCfg["dataDir"] + "decile" + "/" + baseYear + "/" + period + "/" + "ersst." + date[:6] + "dec"
		title = titlehead + self.config.getTitle(variable) + smonth + " %s" % (startDate.year) + ' to ' + cmonth + ' ' + date[0:4]
	    elif period=='6monthly':
                filename = self.serverCfg["dataDir"] + "decile" + "/" + baseYear + "/" + period + "/" + "ersst." + date[:6] + "dec"
		title = titlehead + self.config.getTitle(variable) + smonth + " %s" % (startDate.year) + ' to ' + cmonth + ' ' + date[0:4]
	    elif period=='12monthly':
                filename = self.serverCfg["dataDir"] + "decile" + "/" + baseYear + "/" + period + "/" + "ersst." + date[:6] + "dec"
	    	title = titlehead + self.config.getTitle(variable) + smonth + " %s" % (startDate.year) + ' to ' + cmonth + ' ' + date[0:4]
	elif variable=='trend':
	    centerLabel = False
	    if period=='monthly':
		filename = self.serverCfg["dataDir"] + "trend" + "/" + period + "/" + baseYear + "/" + "ersst." + period\
		+ "_" + baseYear + "_2011lin" + date[4:6]
		title = titlehead + self.config.getTitle(variable) + cmonth + ' (' + baseYear + '-' + date[0:4] + ')'
	    if period=='3monthly':
                filename = self.serverCfg["dataDir"] + "trend" + "/" + period + "/" + baseYear + "/" + "ersst." + period\
                + "_" + baseYear + "_2011lin" + date[4:6]
		title = titlehead + self.config.getTitle(variable) + smonth + ' to ' + cmonth + ' (' + baseYear + '-' + date[0:4] + ')'
	    if period=='6monthly':
                filename = self.serverCfg["dataDir"] + "trend" + "/" + period + "/" + baseYear + "/" + "ersst." + period\
                + "_" + baseYear + "_2011lin" + date[4:6]
		title = titlehead + self.config.getTitle(variable) + smonth + ' to ' + cmonth + ' (' + baseYear + '-' + date[0:4] + ')'
	    if period=='12monthly':
                filename = self.serverCfg["dataDir"] + "trend" + "/" + period + "/" + baseYear + "/" + "ersst." + period\
                + "_" + baseYear + "_2011lin" + date[4:6]	
	    	title = titlehead + self.config.getTitle(variable) + smonth + ' to ' + cmonth + ' (' + baseYear + '-' + date[0:4] + ')'
        else:
            return -1
	
        filename = filename + ".nc" 
        dataset = Dataset(filename, 'r')

	#formatted_title = 
	#title = titlehead + self.config.getTitle(variable) + "%s %04d%02d" % (area, date


        sst = dataset.variables[self.config.getVariableType(variable)][0][0]
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['lon'][:]
        
        lons = np.array(lons,np.float64)
        lats = np.array(lats,np.float64)

	sst = sm.smooth(sst, 5)

	contourLines = True

        plot = plotter.Plotter()
        plot.contour(sst, lats, lons, variable, self.config, outputFilename, title,\
                  regionConfig.regions[area][1]["llcrnrlat"],\
                  regionConfig.regions[area][1]["llcrnrlon"],\
                  regionConfig.regions[area][1]["urcrnrlat"],\
                  regionConfig.regions[area][1]["urcrnrlon"],\
		  "cyl", contourLines, centerLabel)
        #plot.plotBasemapEast(sst, lats, lons, variable, self.config, outputFilename)
        #plot.plotBasemapWest(sst, lats, lons, variable, self.config, outputFilename)

        dataset.close()
        
        return 0


