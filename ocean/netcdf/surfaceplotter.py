#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import bisect
import os.path

import numpy as np

from ocean import util, config
from ocean.config import regionConfig
from ocean.netcdf import Gridset
from ocean.plotter import Plotter

serverCfg = config.get_server_config()

class SurfacePlotter(object):
    """
    Plot surface data from a netCDF grid.

    Override class hooks to specify the location for data.

    Use the decorator @SurfacePlotter.apply_to to tag methods to bind to
    specific parameters. Most tightly binding function wins.
    """

    BASE_YEAR = '1950'
    FILE_EXTENSION = '.nc'

    _pp = util.Parameterise()
    apply_to = _pp.apply_to

    # --- get_path ---
    @apply_to()
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'averages', params['period'])

    @apply_to(variable='dec')
    def get_path(self, params={}):
        return os.path.join(serverCfg['dataDir'][self.DATASET],
                            'decile', self.BASE_YEAR, params['period'])

    # --- get_suffix ---
    @apply_to(variable='dec')
    def get_suffix(self, params={}):
        return '_dec' + self.FILE_EXTENSION

    @apply_to()
    def get_suffix(self, params={}):
        return self.FILE_EXTENSION

    # --- get_formatted_date ---
    @apply_to(period='daily')
    def get_formatted_date(self, params={}):
        return params['date'].strftime('%d %B %Y')

    @apply_to(period='monthly')
    def get_formatted_date(self, params={}):
        return params['date'].strftime('%B %Y')

    @apply_to(period='3monthly')
    def get_formatted_date(self, params={}):
        return self._get_formatted_date(params, 3)

    @apply_to(period='6monthly')
    def get_formatted_date(self, params={}):
        return self._get_formatted_date(params, 6)

    @apply_to(period='12monthly')
    def get_formatted_date(self, params={}):
        return self._get_formatted_date(params, 12)

    def _get_formatted_date(self, params, range):
        months = util.getMonths(params['date'], range)
        return "%s to %s" % (months[0].strftime('%B %Y'),
                             months[-1].strftime('%B %Y'))

    # --- get_ticks_format ---
    @apply_to()
    def get_ticks_format(self, params={}):
        return '%.1f'

    @apply_to(variable='mean')
    def get_ticks_format(self, params={}):
        return '%.0f'

    # --- get_labels ---
    @apply_to()
    def get_labels(self, params={}):
        return (None, None)

    @apply_to(variable='dec')
    def get_labels(self, params={}):
        return (['Lowest on \nrecord',
                 'Very much \nbelow average \n[1]',
                 'Below average \n[2-3]',
                 'Average \n[4-7]',
                 'Above average \n[8-9]',
                 'Very much \nabove average \n[10]',
                 'Highest on \nrecord'],
                [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])

    # --- get_ticks ---
    @apply_to(variable='mean')
    def get_ticks(self, params={}):
        try:
            if regionConfig.regions[params['area']][0] == 'pi':
                return np.arange(20.0, 32.1, 1.0)
            else:
                pass
        except KeyError:
            pass

        return np.arange(0.0, 32.1, 2.0)

    @apply_to(variable='anom')
    def get_ticks(self, params={}):
        return np.arange(-2.0, 2.01, 0.5)

    @apply_to(variable='dec')
    def get_ticks(self, params={}):
        return np.arange(0.5, 7.51, 1)

    # --- get_extend ---
    @apply_to()
    def get_extend(self, params={}):
        return 'both'

    @apply_to(variable='dec')
    def get_extend(self, params={}):
        return 'neither'

    # --- get_contour_labels ---
    @apply_to()
    def get_contour_labels(self, params={}):
        return True

    @apply_to(variable='dec')
    def get_contour_labels(self, params={}):
        return False

    # ---
    def __init__(self):
        self.config = self.CONFIG()

    def get_grid(self, params={}, **kwargs):
        """
        Request a Grid object for this dataset.

        Override this method to access grids in a different way.
        """

        gridvar = self.config.getVariableType(params['variable'])

        return Gridset(self.get_path(params=params), gridvar, params['period'],
                       prefix=self.get_prefix(params=params),
                       suffix=self.get_suffix(params=params),
                       date=params['date'],
                       **kwargs)

    def plot(self, outputFilename, **args):
        """
        Plot the thumbnail image and also the east and west map images.
        """

        area = args['area']
        variable = args['variable']

        args['formattedDate'] = self.get_formatted_date(params=args)
        output_filename = serverCfg['outputDir'] + outputFilename + '.png'

        regionLongName = regionConfig.regions[area][2]
        title = regionLongName + '\n'

        if hasattr(self.config, 'getPeriodPrefix') and 'period' in args:
            title += self.config.getPeriodPrefix(args['period'])
            title += self.config.getTitle(variable) + args['formattedDate']

        cmap_name = self.config.getColorMap(variable)
        units = self.config.getUnit(variable)

        cb_ticks = self.get_ticks(params=args)
        cb_tick_fmt = self.get_ticks_format(params=args)
        cb_labels, cb_label_pos = self.get_labels(params=args)
        extend = self.get_extend(params=args)
        contourLabels = self.get_contour_labels(params=args)

        plot = Plotter()

        lat_min = regionConfig.regions[area][1]['llcrnrlat']
        lat_max = regionConfig.regions[area][1]['urcrnrlat']
        lon_min = regionConfig.regions[area][1]['llcrnrlon']
        lon_max = regionConfig.regions[area][1]['urcrnrlon']

        grid = self.get_grid(params=args,
                             lonrange=(lon_min, lon_max),
                             latrange=(lat_min, lat_max))

        plot.plot_surface_data(grid.lats, grid.lons, grid.data,
                               lat_min, lat_max, lon_min, lon_max,
                               output_filename=output_filename,
                               title=title,
                               units=units,
                               cm_edge_values=cb_ticks,
                               cb_tick_fmt=cb_tick_fmt,
                               cb_labels=cb_labels,
                               cb_label_pos=cb_label_pos,
                               cmp_name=cmap_name,
                               extend=extend,
                               contourLabels=contourLabels,
                               product_label_str=self.PRODUCT_NAME,
                               area=area)

        grid = self.get_grid(params=args)

        if variable == 'dec':
            # Mask out polar region to avoid problem of calculating deciles
            # over sea ice
            grid.data.mask[0:bisect.bisect_left(grid.lats,-60),:] = True
            grid.data.mask[bisect.bisect_left(grid.lats,60):-1,:] = True

        plot.plot_basemaps_and_colorbar(grid.lats, grid.lons, grid.data,
                                        output_filename=output_filename,
                                        units=units,
                                        cm_edge_values=cb_ticks,
                                        cb_tick_fmt=cb_tick_fmt,
                                        cb_labels=cb_labels,
                                        cb_label_pos=cb_label_pos,
                                        cmp_name=cmap_name, extend=extend)

        plot.wait()
