#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

from netCDF4 import Dataset
import numpy as np
import datetime

import reynoldsConfig as rc
import reynoldsSpatialMean as spatialMean
import ocean.util as util
from ..util import regionConfig
from ..util import dateRange
from ..netcdf import plotter


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
       self.serverCfg = util.get_server_config()

    def plot(self, outputFilename, **args):
        """
        Plot the thumbnail image and also the east and west map images.
        """
        variable = args['map']
        date = args['date']
        area = args['area']
        period = args['period']
        
        dateObj = datetime.date(int(date[:4]), int(date[4:6]), int(date[6:]))
        formattedDate = ''
        cntLabel = False
        if variable == 'dec':
            formattedDate = dateObj.strftime('%B %Y')
            filename = self.serverCfg["dataDir"]["reynolds"] + "decile/" + period + "/" + date[:4] + "/" + "avhrr-only-v2." + date[:6]  + "dec"
            cntLabel = True
        else:
            if period=='daily':
                formattedDate = dateObj.strftime('%d %B %Y')
                filename = self.serverCfg["dataDir"]["reynolds"] + period + "/" + date[:4] + "/" + "avhrr-only-v2." + date
            elif period=='predaily':
                formattedDate = dateObj.strftime('%d %B %Y')
                filename = self.serverCfg["dataDir"]["reynolds"] + period + "/" + date[:4] + "/" + "avhrr-only-v2." + date + "_preliminary"
            elif period=='weekly':
                weekdays = dateRange.getWeekDays(date)
                formattedDate = weekdays[0].strftime('%d %B %Y') + ' to ' + weekdays[-1].strftime('%d %B %Y') 
                spatialMean.generateWeekly(weekdays)
                filename = self.serverCfg["dataDir"]["reynolds"] + period + "/" + "avhrr-only-v2." + weekdays[0].strftime('%Y%m%d') + "ave"
            elif period=='monthly':
                formattedDate = dateObj.strftime('%B %Y')
                filename = self.serverCfg["dataDir"]["reynolds"] + period + "/" + date[:4] + "/" + "avhrr-only-v2." + date[:6] + "ave"
            elif period=='3monthly':
                months = dateRange.getMonths(date, 3)
                formattedDate = months[0].strftime('%B %Y') + ' to ' + months[-1].strftime('%B %Y') 
                spatialMean.generate3Monthly(months)
                filename = self.serverCfg["dataDir"]["reynolds"] + period + "/avhrr-only-v2." + date[:6] + "ave"
            elif period=='6monthly':
                months = dateRange.getMonths(date, 6)
                formattedDate = months[0].strftime('%B %Y') + ' to ' + months[-1].strftime('%B %Y') 
                spatialMean.generate6Monthly(months)
                filename = self.serverCfg["dataDir"]["reynolds"] + period + "/avhrr-only-v2." + date[:6] + "ave"
            elif period=='yearly':
                formattedDate = date[:4]
                filename = self.serverCfg["dataDir"]["reynolds"] + period + "/avhrr-only-v2." + date[:4] + "ave"
            else:
                return -1
        
        args['formattedDate'] = formattedDate
        filename = filename + ".nc" 
        dataset = Dataset(filename, 'r')
        sst = dataset.variables[self.config.getVariableType(variable)][0][0]
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['lon'][:]
        
        delon = lons[1]-lons[0]; delat = lats[1]-lats[0]
        lons = (lons - 0.5*delon).tolist()
        lons.append(lons[-1]+delon)
        lons = np.array(lons,np.float64) #TODO check necessariness 
        lats = (lats - 0.5*delat).tolist()
        lats.append(lats[-1]+delat)
        lats = np.array(lats,np.float64)
         
        resolution='h'
        if not area=='pac':
           resolution='f'

        plot = plotter.Plotter()
        plot.plot(sst, lats, lons, variable, self.config, outputFilename,\
                  regionConfig.regions[area][1]["llcrnrlat"],\
                  regionConfig.regions[area][1]["llcrnrlon"],\
                  regionConfig.regions[area][1]["urcrnrlat"],\
                  regionConfig.regions[area][1]["urcrnrlon"],\
                  res=resolution, centerLabel = cntLabel, **args)
        plot.plotBasemapEast(sst, lats, lons, variable, self.config, outputFilename)
        plot.plotBasemapWest(sst, lats, lons, variable, self.config, outputFilename)
        plot.plotScale(sst, variable, self.config, outputFilename)

        dataset.close()

        return 0
