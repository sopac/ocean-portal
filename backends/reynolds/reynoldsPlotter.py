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

        cb_labels = None
        cb_label_pos = None

        if variable == 'mean':
            extend = 'both'
            cb_tick_fmt="%.0f"
            if regionConfig.regions.has_key(area):
                if regionConfig.regions[area][0] == 'pi':
                    cb_ticks = np.arange(20.0,32.1,1.0)
                else:
                    cb_ticks = np.arange(0.0,32.1,2.0)
            else:
                cb_ticks = np.arange(0.0,32.1,2.0)

        if variable == 'anom':
            extend = 'both'
            cb_tick_fmt="%.1f"
            cb_ticks = np.arange(-2.0,2.01,0.5)

        if variable == 'dec':
            extend = 'neither'
            cb_tick_fmt="%.1f"
            cb_ticks = np.arange(0.5,5.51,1)
            #cb_labels=['Lowest on \nrecord','Very much \nbelow average \n[1]','Below average \n[2-3]','Average \n[4-7]','Above average \n[8-9]','Very much \nabove average \n[10]','Highest on \nrecord']
            cb_labels=['Very much \nbelow average \n[1]','Below average \n[2-3]','Average \n[4-7]','Above average \n[8-9]','Very much \nabove average \n[10]']
            cb_label_pos=[1.0,2.0,3.0,4.0,5.0]

        args['formattedDate'] = formattedDate
        filename = filename + ".nc" 
        dataset = Dataset(filename, 'r')
        sst = dataset.variables[self.config.getVariableType(variable)][0][0]
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['lon'][:]

        resolution='h'
        if not area=='pac':
           resolution='f'

        output_filename = self.serverCfg["outputDir"] + outputFilename + '.png'

        regionLongName = regionConfig.regions[area][2]
        title = regionLongName + '\n'

        if hasattr(self.config, 'getPeriodPrefix') and 'period' in args:
            title += self.config.getPeriodPrefix(args['period'])
            title += self.config.getTitle(variable) + args['formattedDate']

        cmap_name = self.config.getColorMap(variable)
        units = self.config.getUnit(variable)

        plot = plotter.Plotter()
        plot.plotBasemapEast(sst, lats, lons, variable, self.config, outputFilename)
        plot.plotBasemapWest(sst, lats, lons, variable, self.config, outputFilename)
        plot.plotScale(sst, variable, self.config, outputFilename)

        if variable == 'dec':
            # Temporary patch until decile calculation code is fixed
            sst = np.where((sst < 1.5), 1, sst)
            sst = np.where((sst >= 1.5) & (sst < 3.5), 2, sst)
            sst = np.where((sst >= 3.5) & (sst < 7.5), 3, sst)
            sst = np.where((sst >= 7.5) & (sst < 9.5), 4, sst)
            sst = np.where((sst >= 9.5), 5, sst)
        plot.plot_surface_data(lats, lons, sst,
                               regionConfig.regions[area][1]["llcrnrlat"],
                               regionConfig.regions[area][1]["urcrnrlat"],
                               regionConfig.regions[area][1]["llcrnrlon"],
                               regionConfig.regions[area][1]["urcrnrlon"],
                               output_filename, title=title, units=units,
                               cm_edge_values=cb_ticks, cb_tick_fmt=cb_tick_fmt,
                               cb_labels=cb_labels, cb_label_pos=cb_label_pos,
                               cmp_name=cmap_name, extend=extend,
                               contourLines=False, product_label_str='Reynolds SST')

        dataset.close()

        return 0
