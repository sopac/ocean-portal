#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import datetime

from netCDF4 import Dataset
import numpy as np
import bisect

from ocean import util, config
from ocean.config import regionConfig
from ocean.util import dateRange
from ocean.netcdf import plotter
from ocean.datasets.bran import branPlotterNew

import reynoldsConfig as rc
import reynoldsSpatialMean as spatialMean

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
       self.serverCfg = config.get_server_config()

    def plot(self, outputFilename, **args):
        """
        Plot the thumbnail image and also the east and west map images.
        """
        variable = args['variable']
        area = args['area']
        period = args['period']
        
        dateObj = args['date']
        date = dateObj.strftime('%Y%m%d')

        formattedDate = ''
        if variable == 'dec':
            if period=='monthly':
                formattedDate = dateObj.strftime('%B %Y')
                filename = self.serverCfg["dataDir"]["reynolds"] + "decile/1950/" + period + "/" + "reynolds_sst_avhrr-only-v2_" + date[:6]  + "_dec"
            else:
                monthInt = ''.join(i for i in period if i.isdigit())
                months = dateRange.getMonths(date, monthInt)
                formattedDate = months[0].strftime('%B %Y') + ' to ' + months[-1].strftime('%B %Y')
                filename = self.serverCfg["dataDir"]["reynolds"] + "decile/1950/" + period + "/" + \
                           "reynolds_sst_avhrr-only-v2_" + monthInt + "mthavg_" + \
                           months[0].strftime('%Y%m') + "_" + months[-1].strftime('%Y%m') + "_dec"
        else:
            if period=='daily':
                formattedDate = dateObj.strftime('%d %B %Y')
                filename = self.serverCfg["dataDir"]["reynolds"] + 'daily-new-uncompressed' + "/" + "avhrr-only-v2." + date
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
                filename = self.serverCfg["dataDir"]["reynolds"] + "/averages/monthly/reynolds_sst_avhrr-only-v2_" + date[:6]
            elif period=='3monthly':
                months = dateRange.getMonths(date, 3)
                formattedDate = months[0].strftime('%B %Y') + ' to ' + months[-1].strftime('%B %Y')
                filename = self.serverCfg["dataDir"]["reynolds"] + \
                           "/averages/3monthly/reynolds_sst_avhrr-only-v2_3mthavg_" + \
                           months[0].strftime('%Y%m') + '_' + months[-1].strftime('%Y%m')
            elif period=='6monthly':
                months = dateRange.getMonths(date, 6)
                formattedDate = months[0].strftime('%B %Y') + ' to ' + months[-1].strftime('%B %Y') 
                filename = self.serverCfg["dataDir"]["reynolds"] + \
                           "/averages/6monthly/reynolds_sst_avhrr-only-v2_6mthavg_" + \
                           months[0].strftime('%Y%m') + '_' + months[-1].strftime('%Y%m')
            elif period=='12monthly':
                months = dateRange.getMonths(date, 12)
                formattedDate = months[0].strftime('%B %Y') + ' to ' + months[-1].strftime('%B %Y')
                filename = self.serverCfg["dataDir"]["reynolds"] + \
                           "/averages/12monthly/reynolds_sst_avhrr-only-v2_12mthavg_" + \
                           months[0].strftime('%Y%m') + '_' + months[-1].strftime('%Y%m')
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
            cb_ticks = np.arange(0.5,7.51,1)
            cb_labels=['Lowest on \nrecord','Very much \nbelow average \n[1]','Below average \n[2-3]','Average \n[4-7]','Above average \n[8-9]','Very much \nabove average \n[10]','Highest on \nrecord']
            #cb_labels=['Very much \nbelow average \n[1]','Below average \n[2-3]','Average \n[4-7]','Above average \n[8-9]','Very much \nabove average \n[10]']
            cb_label_pos=[1.0,2.0,3.0,4.0,5.0,6.0,7.0]

        args['formattedDate'] = formattedDate
        filename = filename + ".nc" 
        dataset = Dataset(filename, 'r')

        lats = dataset.variables['lat'][:]
        lons = dataset.variables['lon'][:]

        #if variable == 'dec':
        #    sst = dataset.variables[self.config.getVariableType(variable)][:]
        #    # Mask out polar region to avoid problem of calculating deciles over sea ice
        #    sst.mask[0:bisect.bisect_left(lats,-60),:] = True
        #    sst.mask[bisect.bisect_left(lats,60):-1,:] = True
        #else:
        #    sst = dataset.variables[self.config.getVariableType(variable)][0][0]
        #lats = dataset.variables['lat'][:]
        #lons = dataset.variables['lon'][:]

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
        #plot.plotBasemapEast(sst, lats, lons, variable, self.config, outputFilename)
        #plot.plotBasemapWest(sst, lats, lons, variable, self.config, outputFilename)
        #plot.plotScale(sst, variable, self.config, outputFilename)

        if variable == 'dec':
            contourLabels = False
        else:
            contourLabels = True

        lat_min = regionConfig.regions[area][1]['llcrnrlat']
        lat_max = regionConfig.regions[area][1]['urcrnrlat']
        lon_min = regionConfig.regions[area][1]['llcrnrlon']
        lon_max = regionConfig.regions[area][1]['urcrnrlon']

        lats, lons, skip, sst = \
            branPlotterNew.load_BRAN_data(filename, self.config.getVariableType(variable),
                                          lat_min - 1.0, lat_max + 1.0,
                                          lon_min - 1.0, lon_max + 1.0)

        plot.plot_surface_data(lats, lons, sst,
                               lat_min, lat_max, lon_min, lon_max,
                               output_filename=output_filename,
                               title=title, units=units,
                               cm_edge_values=cb_ticks, cb_tick_fmt=cb_tick_fmt,
                               cb_labels=cb_labels, cb_label_pos=cb_label_pos,
                               cmp_name=cmap_name, extend=extend,
                               contourLabels=contourLabels,
                               product_label_str='Reynolds SST',
                               area=area)

        lats, lons, skip, sst = \
            branPlotterNew.load_BRAN_data(filename, self.config.getVariableType(variable), -999.0, 999.0, -999.0, 999.0)

        if variable == 'dec':
            # Mask out polar region to avoid problem of calculating deciles over sea ice
            sst.mask[0:bisect.bisect_left(lats,-60),:] = True
            sst.mask[bisect.bisect_left(lats,60):-1,:] = True

        plot.plot_basemaps_and_colorbar(lats, lons, sst,
                                        output_filename=output_filename,
                                        units=units, cm_edge_values=cb_ticks, cb_tick_fmt=cb_tick_fmt,
                                        cb_labels=cb_labels, cb_label_pos=cb_label_pos,
                                        cmp_name=cmap_name, extend=extend)

        plot.wait()
        dataset.close()

        return 0
