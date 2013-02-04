#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Matthew Howie

import os.path
import glob

import numpy as np
import bisect

import ersstConfig as ec

from ocean import util, config
from ocean.util import dateRange
from ocean.config import regionConfig
from ocean.netcdf import plotter
from ocean.datasets.bran import branPlotterNew

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
                    months = dateRange.getMonths(date, 3)
                    filename = self.serverCfg["dataDir"]["ersst"] + "averages/3monthly/ersst_v3b_3mthavg_" + months[0].strftime('%Y%m') + '_' + months[-1].strftime('%Y%m')
                elif period=='6monthly':
                    months = dateRange.getMonths(date, 6)
                    filename = self.serverCfg["dataDir"]["ersst"] + "averages/6monthly/ersst_v3b_6mthavg_" + months[0].strftime('%Y%m') + '_' + months[-1].strftime('%Y%m')
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(dateRange.getMonths(date, period[:1])[0]) \
                      + " to "\
                      + util.format_old_date(inputDate)
            elif period == '12monthly':
                months = dateRange.getMonths(date, 12)
                filename = self.serverCfg["dataDir"]["ersst"] + "averages/12monthly/ersst_v3b_12mthavg_" + months[0].strftime('%Y%m') + '_' + months[-1].strftime('%Y%m')
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(dateRange.getMonths(date, period[:2])[0])\
                      + " to "\
                      + util.format_old_date(inputDate)

        elif variable == 'dec':
            centerLabel = True
            baseYear = '1950' #str(args['baseYear'])

            if period=='monthly':
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + util.format_old_date(inputDate)
                filename = os.path.join(self.serverCfg['dataDir']['ersst'],
                                        'decile', baseYear, period,
                                        'ersst.' + date[:6] + '_dec')
            elif (period == '3monthly') or (period == '6monthly') or (period == '12monthly'):
                monthInt = ''.join(i for i in period if i.isdigit())
                months = dateRange.getMonths(date, monthInt)
                formattedDate = months[0].strftime('%B %Y') + ' to ' + months[-1].strftime('%B %Y')
                filename = os.path.join(self.serverCfg['dataDir']['ersst'],
                                        'decile', baseYear, period,
                                        'ersst_v3b_' + monthInt + 'mthavg_' + \
                                        months[0].strftime('%Y%m') + "_" + months[-1].strftime('%Y%m') + "_dec")
                title = regionLongName + '\n' \
                      + self.config.getPeriodPrefix(period)\
                      + self.config.getTitle(variable)\
                      + months[0].strftime('%B %Y') \
                      + " to "\
                      + months[-1].strftime('%B %Y')
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
            cb_label_pos=[1.0,2.0,3.0,4.0,5.0,6.0,7.0]
            
        filename = filename + ".nc" 
        filename = glob.glob(filename)[0]

        plot = plotter.Plotter()
        output_filename = self.serverCfg["outputDir"] + outputFilename + '.png'
        units = self.config.getUnit(variable)
        cmap_name = self.config.getColorMap(variable)

        if variable == 'dec':
            contourLabels = False
        else:
            contourLabels = True

        lat_min = regionConfig.regions[area][1]['llcrnrlat']
        lat_max = regionConfig.regions[area][1]['urcrnrlat']
        lon_min = regionConfig.regions[area][1]['llcrnrlon']
        lon_max = regionConfig.regions[area][1]['urcrnrlon']

        lats, lons, _, sst = \
            branPlotterNew.load_BRAN_data(filename, self.config.getVariableType(variable),
                                          lat_min - 1.0, lat_max + 1.0,
                                          lon_min - 1.0, lon_max + 1.0)

        plot.plot_surface_data(lats, lons, sst,
                               lat_min, lat_max, lon_min, lon_max,
                               output_filename, title=title, units=units,
                               product_label_str='Extended Reconstructed SST',
                               cm_edge_values=cb_ticks, cb_tick_fmt=cb_tick_fmt,
                               cb_labels=cb_labels, cb_label_pos=cb_label_pos,
                               cmp_name=cmap_name, extend=extend,
                               contourLabels=contourLabels, area=area)

        lats, lons, _, sst = \
            branPlotterNew.load_BRAN_data(filename, self.config.getVariableType(variable), -999.0, 999.0, -999.0, 999.0)

        if variable == 'dec':
            # Mask out polar region to avoid problem of calculating deciles over sea ice
            sst.mask[0:bisect.bisect_left(lats,-60),:] = True
            sst.mask[bisect.bisect_left(lats,60):-1,:] = True

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

        return 0
