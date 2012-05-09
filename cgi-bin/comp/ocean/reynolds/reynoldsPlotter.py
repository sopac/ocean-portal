#!/usr/bin/python


from ..netcdf import plotter

from netCDF4 import Dataset
import numpy as np
import reynoldsConfig as rc
from ..util import serverConfig
from ..util import regionConfig


class ReynoldsPlotter ():
    """ 
    Reynolds plotter is specifically designed to plot the reynolds
    netcdf data
    """
    config = None
    serverCfg = None

    def __init__(self):
       """Does nothing""" 
       self.config = rc.ReynoldsConfig()
       self.serverCfg = serverConfig.servers[serverConfig.currentServer]

    def plot(self, outputFilename, variable, date, area, period):
        """
        Plot the thumbnail image and also the east and west map images.
        """
        if period=='daily':
            filename = self.serverCfg["dataDir"] + period + "/" + date[:4] + "/" + "avhrr-only-v2." + date
        elif period=='predaily':
            filename = self.serverCfg["dataDir"] + period + "/" + date[:4] + "/" + "avhrr-only-v2." + date + "_preliminary"
        elif period=='weekly':
            filename = self.serverCfg["dataDir"] + period + "/" + "avhrr-only-v2." + date + "ave"
            startDate, endDate = daterange.generateWeekly(date)
        elif period=='monthly':
            filename = self.serverCfg["dataDir"] + period + "/" + date[:4] + "/" + "avhrr-only-v2." + date[:6] + "ave"
        elif period=='3monthly':
            filename = self.serverCfg["dataDir"] + period + "/" + date[:4] + "/" + "avhrr-only-v2." + date[:6] + "ave"
            startDate = daterange.generate3Month(date)
        elif period=='6monthly':
            filename = self.serverCfg["dataDir"] + period + "/" + date[:4] + "/" + "avhrr-only-v2." + date[:6] + "ave"
            startDate = daterange.generate6Month(date)
        elif period=='yearly':
            filename = self.serverCfg["dataDir"] + period + "/" + date[:4] + "/" + "avhrr-only-v2." + date[:4] + "ave"
        else:
            return -1
        
        filename = filename + ".nc" 
        dataset = Dataset(filename, 'r')
        sst = dataset.variables[self.config.getVariableType(variable)][0][0]
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['lon'][:]
        
        delon = lons[1]-lons[0]; delat = lats[1]-lats[0]
        lons = (lons - 0.5*delon).tolist()
        lons.append(lons[-1]+delon)
        lons = np.array(lons,np.float64)
        lats = (lats - 0.5*delat).tolist()
        lats.append(lats[-1]+delat)
        lats = np.array(lats,np.float64)

        plot = plotter.Plotter()
        plot.plot(sst, lats, lons, variable, self.config, outputFilename,\
                  regionConfig.regions[area][1]["llcrnrlat"],\
                  regionConfig.regions[area][1]["llcrnrlon"],\
                  regionConfig.regions[area][1]["urcrnrlat"],\
                  regionConfig.regions[area][1]["urcrnrlon"])
        plot.plotBasemapEast(sst, lats, lons, variable, self.config, outputFilename)
        plot.plotBasemapWest(sst, lats, lons, variable, self.config, outputFilename)

        dataset.close()
        
        return 0

