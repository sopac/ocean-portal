#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os.path

import numpy as np
import bisect

from ocean import util, config
from ocean.config import regionConfig
from ocean.util import dateRange, Parameterise
from ocean.netcdf import plotter
from ocean.netcdf.grid import Gridset

import reynoldsConfig as rc
import reynoldsSpatialMean as spatialMean

class ReynoldsPlotter ():
    """ 
    Reynolds plotter is specifically designed to plot the reynolds
    netcdf data
    """

    pp = Parameterise()

    def __init__(self):
       self.config = rc.ReynoldsConfig()
       self.serverCfg = config.get_server_config()

    # --- get_path ---
    @pp.apply_to()
    def get_path(self, params={}):
        return os.path.join(self.serverCfg['dataDir']['reynolds'],
                            'averages', params['period'])

    @pp.apply_to(period='daily')
    def get_path(self, params={}):
        return os.path.join(self.serverCfg['dataDir']['reynolds'],
                            'daily-new-uncompressed' )

    @pp.apply_to(variable='dec')
    def get_path(self, params={}):
        return os.path.join(self.serverCfg['dataDir']['reynolds'],
                            'decile', '1950', params['period'])

    # --- get_prefix ---
    @pp.apply_to(period='daily')
    def get_prefix(self, params={}):
        return 'avhrr-only-v2.'

    @pp.apply_to()
    def get_prefix(self, params={}):
        return 'reynolds_sst_avhrr-only-v2_'

    # --- get_suffix ---
    @pp.apply_to(variable='dec')
    def get_suffix(self, params={}):
        return '_dec.nc'

    @pp.apply_to()
    def get_suffix(self, params={}):
        return '.nc'

    # --- get_formatted_date ---
    @pp.apply_to(period='daily')
    def get_formatted_date(self, params={}):
        return params['date'].strftime('%d %B %Y')

    @pp.apply_to(period='monthly')
    def get_formatted_date(self, params={}):
        return params['date'].strftime('%B %Y')

    @pp.apply_to(period='3monthly')
    def get_formatted_date(self, params={}):
        return self._get_formatted_date(params, 3)

    @pp.apply_to(period='6monthly')
    def get_formatted_date(self, params={}):
        return self._get_formatted_date(params, 6)

    @pp.apply_to(period='12monthly')
    def get_formatted_date(self, params={}):
        return self._get_formatted_date(params, 12)

    def _get_formatted_date(self, params, range):
        months = dateRange.getMonths(params['date'], range)
        return "%s to %s" % (months[0].strftime('%B %Y'),
                             months[-1].strftime('%B %Y'))

    def plot(self, outputFilename, **args):
        """
        Plot the thumbnail image and also the east and west map images.
        """

        variable = args['variable']
        area = args['area']
        period = args['period']
        date = args['date']

        formattedDate = self.get_formatted_date(params=args)

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

        elif variable == 'anom':
            extend = 'both'
            cb_tick_fmt="%.1f"
            cb_ticks = np.arange(-2.0,2.01,0.5)

        elif variable == 'dec':
            extend = 'neither'
            cb_tick_fmt="%.1f"
            cb_ticks = np.arange(0.5,7.51,1)
            cb_labels=['Lowest on \nrecord',
                       'Very much \nbelow average \n[1]',
                       'Below average \n[2-3]',
                       'Average \n[4-7]',
                       'Above average \n[8-9]',
                       'Very much \nabove average \n[10]',
                       'Highest on \nrecord']
            cb_label_pos=[1.0,2.0,3.0,4.0,5.0,6.0,7.0]

        args['formattedDate'] = formattedDate
        output_filename = self.serverCfg['outputDir'] + outputFilename + '.png'

        regionLongName = regionConfig.regions[area][2]
        title = regionLongName + '\n'

        if hasattr(self.config, 'getPeriodPrefix') and 'period' in args:
            title += self.config.getPeriodPrefix(args['period'])
            title += self.config.getTitle(variable) + args['formattedDate']

        cmap_name = self.config.getColorMap(variable)
        units = self.config.getUnit(variable)

        plot = plotter.Plotter()

        if variable == 'dec':
            contourLabels = False
        else:
            contourLabels = True

        lat_min = regionConfig.regions[area][1]['llcrnrlat']
        lat_max = regionConfig.regions[area][1]['urcrnrlat']
        lon_min = regionConfig.regions[area][1]['llcrnrlon']
        lon_max = regionConfig.regions[area][1]['urcrnrlon']

        gridvar = self.config.getVariableType(variable)

        grid = Gridset(self.get_path(params=args), gridvar, period,
                       prefix=self.get_prefix(params=args),
                       suffix=self.get_suffix(params=args),
                       date=date,
                       lonrange=(lon_min, lon_max),
                       latrange=(lat_min, lat_max))

        plot.plot_surface_data(grid.lats, grid.lons, grid.data,
                               lat_min, lat_max, lon_min, lon_max,
                               output_filename=output_filename,
                               title=title, units=units,
                               cm_edge_values=cb_ticks, cb_tick_fmt=cb_tick_fmt,
                               cb_labels=cb_labels, cb_label_pos=cb_label_pos,
                               cmp_name=cmap_name, extend=extend,
                               contourLabels=contourLabels,
                               product_label_str='Reynolds SST',
                               area=area)

        grid = Gridset(self.get_path(params=args), gridvar, period,
                       prefix=self.get_prefix(params=args),
                       suffix=self.get_suffix(params=args),
                       date=date)

        if variable == 'dec':
            # Mask out polar region to avoid problem of calculating deciles
            # over sea ice
            grid.data.mask[0:bisect.bisect_left(grid.lats,-60),:] = True
            grid.data.mask[bisect.bisect_left(grid.lats,60):-1,:] = True

        plot.plot_basemaps_and_colorbar(grid.lats, grid.lons, grid.data,
                                        output_filename=output_filename,
                                        units=units, cm_edge_values=cb_ticks,
                                        cb_tick_fmt=cb_tick_fmt,
                                        cb_labels=cb_labels,
                                        cb_label_pos=cb_label_pos,
                                        cmp_name=cmap_name, extend=extend)

        plot.wait()

        return 0
