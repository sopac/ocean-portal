#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Matthew Howie

import os.path
import datetime
import glob

import numpy as np
from netCDF4 import Dataset

import ersstConfig as ec
import smooth as sm

from ocean import util, config
from ocean.util import dateRange
from ocean.config import regionConfig
from ocean.netcdf import plotter

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
       self.serverCfg = config.get_server_config()

    def plot(self, outputFilename, **args):
        """
        Plot the thumbnail image and also the east and west map images.
        """
        variable = args["variable"]
        inputDate = args["date"] 
        date = inputDate.strftime('%Y%m%d')
        area = args["area"]
        period = args["period"]
 
        centerLabel = False

        regionLongName = regionConfig.regions[area][2]
        
        if variable == 'mean' or variable == 'anom':
            if period=='monthly':
                filename = self.serverCfg["dataDir"]["ersst"] + period + "/" + "ersst." + date[:6]
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period) \
                      + self.config.getTitle(variable) \
                      + util.format_old_date(inputDate)
            elif period=='3monthly' or period == '6monthly': 
                if period=='3monthly':
                    filename = self.serverCfg["dataDir"]["ersst"] + "seasonalclim/ersst_v3b_" + date[:6] + "_3mthavg"
                elif period=='6monthly':
                    filename = self.serverCfg["dataDir"]["ersst"] + "seasonalclim/ersst_v3b_" + date[:6] + "_6mthavg"
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(dateRange.getMonths(date, period[:1])[0]) \
                      + " to "\
                      + util.format_old_date(inputDate)
            elif period == '12monthly': 
                filename = self.serverCfg["dataDir"]["ersst"] + "seasonalclim/ersst_v3b_" + date[:6] + "_12mthavg"
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(dateRange.getMonths(date, period[:2])[0])\
                      + " to "\
                      + util.format_old_date(inputDate)

        elif variable == 'dec':
            centerLabel = True
            baseYear = str(args['baseYear'])
            filename = os.path.join(self.serverCfg['dataDir']['ersst'],
                                    'decile', baseYear, period,
                                    'ersst.' + date[:6] + 'dec')

            if period=='monthly':
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(inputDate)

            elif period == '3monthly' or period == '6monthly': 
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(dateRange.getMonths(date, period[:1])[0]) \
                      + " to "\
                      + util.format_old_date(inputDate)

            elif period == '12monthly':
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(dateRange.getMonths(date, period[:2])[0]) \
                      + " to "\
                      + util.format_old_date(inputDate)

        elif variable == 'trend':
            baseYear = str(args["baseYear"])
            if period=='monthly':
                filename = self.serverCfg["dataDir"]["ersst"] + "trend/" + period\
                         + "/" + baseYear + "/"  + "ersst." + period\
                         + "_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]lin" + date[4:6]
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + inputDate.strftime('%B')\
                      + " (" + baseYear + " - " + inputDate.strftime('%Y') + ")"
            elif period=='3monthly' or period == '6monthly': 
                filename = self.serverCfg["dataDir"]["ersst"] + "trend/" + period\
                         + "/" + baseYear + "/"  + "ersst." + period\
                         + "_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]lin" + date[4:6]
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + dateRange.getMonths(date, period[:1])[0].strftime('%B')\
                      + " to "\
                      + inputDate.strftime('%B')\
                      + " (" + baseYear + " - " + inputDate.strftime('%Y') + ")"
            elif period == '12monthly': 
                filename = self.serverCfg["dataDir"]["ersst"] + "trend/" + period\
                         + "/" + baseYear + "/"  + "ersst." + period\
                         + "_[0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9]lin" + date[4:6]
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + dateRange.getMonths(date, period[:2])[0].strftime('%B')\
                      + " to "\
                      + inputDate.strftime('%B')\
                      + " (" + baseYear + " - " + inputDate.strftime('%Y') + ")"
        else:
            return -1

        cb_labels = None
        cb_label_pos = None
        extend = 'both'

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
            cb_ticks = np.arange(0.5,7.51,1)
            cb_labels=['Lowest on \nrecord','Very much \nbelow average \n[1]','Below average \n[2-3]','Average \n[4-7]','Above average \n[8-9]','Very much \nabove average \n[10]','Highest on \nrecord']
            #cb_labels=['Very much \nbelow average \n[1]','Below average \n[2-3]','Average \n[4-7]','Above average \n[8-9]','Very much \nabove average \n[10]']
            cb_label_pos=[1.0,2.0,3.0,4.0,5.0,6.0,7.0]
            
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
        output_filename = self.serverCfg["outputDir"] + outputFilename + '.png'
        units = self.config.getUnit(variable)
        cmap_name = self.config.getColorMap(variable)

        if variable == 'dec':
            # Temporary patch until decile calculation code is fixed
            sst = np.where((sst < 0.5), 0, sst)
            sst = np.where((sst >= 0.5) & (sst < 1.5), 1, sst)
            sst = np.where((sst >= 1.5) & (sst < 3.5), 2, sst)
            sst = np.where((sst >= 3.5) & (sst < 7.5), 3, sst)
            sst = np.where((sst >= 7.5) & (sst < 9.5), 4, sst)
            sst = np.where((sst >= 9.5) & (sst < 10.5), 5, sst)
            sst = np.where((sst >= 10.5), 6, sst)
            contourLines = False
        else:
            contourLines = True

        plot.plot_surface_data(lats, lons, sst,
                               regionConfig.regions[area][1]["llcrnrlat"],
                               regionConfig.regions[area][1]["urcrnrlat"],
                               regionConfig.regions[area][1]["llcrnrlon"],
                               regionConfig.regions[area][1]["urcrnrlon"],
                               output_filename, title=title, units=units,
                               product_label_str='Extended Reconstructed SST',
                               cm_edge_values=cb_ticks, cb_tick_fmt=cb_tick_fmt,
                               cb_labels=cb_labels, cb_label_pos=cb_label_pos,
                               cmp_name=cmap_name, extend=extend, contourLines=contourLines)

        plot.plot_basemaps_and_colorbar(lats, lons, sst,
                                        output_filename=output_filename,
                                        units=units,
                                        cm_edge_values=cb_ticks,
                                        cb_tick_fmt=cb_tick_fmt,
                                        cb_labels=cb_labels,
                                        cb_label_pos=cb_label_pos,
                                        cmp_name=cmap_name,
                                        extend=extend)

        plot.wait()
        dataset.close()

        return 0
