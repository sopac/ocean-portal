#!/user/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Nicholas Summons <n.summons@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>
"""
Plotter is the base class for plotting.
"""

import os
import bisect
import math
import shutil
import datetime
import sys
import multiprocessing

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import mpl
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea
from matplotlib.transforms import offset_copy
from mpl_toolkits.basemap import Basemap
try:
    from mpl_toolkits.axes_grid1 import make_axes_locatable
except ImportError:
    # support older matplotlib
    from mpl_toolkits.axes_grid import make_axes_locatable

from ocean import util, logger
from ocean.util.pngcrush import pngcrush
from ocean.config import get_server_config
from ocean.config.regionConfig import regions

COMMON_FILES = {
    'img': '.png',
    'mapeast': '_east.png',
    'mapeastw': '_east.pgw',
    'mapwest': '_west.png',
    'mapwestw': '_west.pgw',
    'scale': '_scale.png',
}

def guess_resolution(latmin, latmax, lonmin, lonmax):
    if min(abs(lonmax - lonmin), latmax - latmin) < 15:
        return 'h' # high
    else:
        return 'c' # crude

def getCopyright():
    return ur'\u00A9' + "Commonwealth of Australia "\
           + datetime.date.today().strftime('%Y')\
           + "\nAustralian Bureau of Meteorology, COSPPac COMP"

class Plotter(object):
    """The base class for plotting netCDF files."""

    _DEFAULT_PROJ = "cyl" #Equidistant Cylindrical Projection
    serverConfig = None

    def __init__(self):
        """The simple constructor of Plotter"""
        self.serverConfig = get_server_config()
        self._processes = []

    @logger.time_and_log('waiting-for-plotter-subprocesses')
    def wait(self):
        """Wait for the completion of all plotting threads"""

        for p in self._processes:
            p.join()
            # FIXME: return any Exceptions back to the main process

    def queue_plot(self, func, *args, **kwargs):
        """Queue a plot to be drawn"""

        def _target(*args, **kwargs):
            if self.serverConfig.get('profile', False):
                import cProfile

                cProfile.runctx('func(*args, **kwargs)', globals(), locals(),
                             '/tmp/portal.profile.%s.%s' % (func.__name__,
                                                            os.getpid()))
            else:
                func(*args, **kwargs)

        p = multiprocessing.Process(target=_target, name=func.__name__,
                                    args=args, kwargs=kwargs)
        self._processes.append(p)
        p.start()

    @logger.time_and_log
    def plot_surface_data(self, *args, **kwargs):

        @logger.time_and_log('subprocess-plot-surface-data')
        def _plot_surface_data(lats, lons, data,
                               lat_min, lat_max, lon_min, lon_max,
                               output_filename='noname.png', title='', units='',
                               cm_edge_values=None, cb_tick_fmt="%.0f",
                               cb_labels=None, cb_label_pos=None,
                               cmp_name='jet', extend='both',
                               plotStyle='contourf', contourLines=True,
                               contourLabels=True,
                               proj=self._DEFAULT_PROJ, product_label_str=None,
                               vlat=None, vlon=None, u=None, v=None,
                               draw_every=1, arrow_scale=10,
                               resolution=None, area=None):

            if resolution is None and area is not None:
                # try and get a resolution from the area default
                resolution = regions[area][3].get('resolution', None)

            if resolution is None:
                # still no resolution? try and guess
                resolution = guess_resolution(lat_min, lat_max,
                                              lon_min, lon_max)

            m = Basemap(projection=proj,
                        llcrnrlat=lat_min, llcrnrlon=lon_min,
                        urcrnrlat=lat_max, urcrnrlon=lon_max,
                        resolution=resolution)

            # Create colormap
            if cm_edge_values is None:
                cm_edge_values = get_tick_values(data.min(), data.max(), 10)[0]
            n_colours = cm_edge_values.size - 1
            d_cmap = discrete_cmap(cmp_name, n_colours, extend=extend)

            # Plot data
            x, y = None, None
            if plotStyle == 'contourf':
                x, y = m(*np.meshgrid(lons, lats))
                img = plt.contourf(x, y, data, levels=cm_edge_values,
                                  shading='flat', cmap=d_cmap, extend=extend)
            elif plotStyle == 'pcolormesh':
                # Convert centre lat/lons to corner values required for
                # pcolormesh
                lons2 = get_grid_edges(lons)
                lats2 = get_grid_edges(lats)
                x2, y2 = m(*np.meshgrid(lons2, lats2))
                img = m.pcolormesh(x2, y2, data, shading='flat', cmap=d_cmap)

            # Draw contours
            if contourLines:
                if x is None:
                    x, y = m(*np.meshgrid(lons, lats))
                cnt = plt.contour(x, y, data, levels=cm_edge_values,
                                 colors = 'k', linewidths = 0.4, hold='on')
                if contourLabels:
                    plt.clabel(cnt, inline=True, fmt=cb_tick_fmt, fontsize=8)

            img.set_clim(cm_edge_values.min(), cm_edge_values.max())

            # Plot vector data if provided
            if (u is not None) and (v is not None) and \
               (vlat is not None) and (vlon is not None):
                # Draw vectors
                if draw_every is not None:
                    draw_vector_plot(m, vlon, vlat, u, v,
                                     draw_every=draw_every,
                                     arrow_scale=arrow_scale)

            # Draw land, coastlines, parallels, meridians and add title
            m.drawcoastlines(linewidth=0.5, color='#505050', zorder=8)
            m.fillcontinents(color='#F1EBB7', zorder=7)

            parallels, p_dec_places = get_tick_values(lat_min, lat_max)
            meridians, m_dec_places = get_tick_values(lon_min, lon_max)
            m.drawparallels(parallels, labels=[True, False, False, False],
                            fmt='%.' + str(p_dec_places) + 'f',
                            fontsize=6, dashes=[3, 3], color='gray')
            m.drawmeridians(meridians, labels=[False, False, False, True],
                            fmt='%.' + str(m_dec_places) + 'f',
                            fontsize=6, dashes=[3, 3], color='gray')
            plt.title(title, fontsize=9)

            # Draw colorbar
            ax = plt.gca()
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size=0.2, pad=0.3)
            if cb_label_pos is None:
                tick_pos = cm_edge_values
            else:
                tick_pos = cb_label_pos
            cb = plt.colorbar(img, cax=cax,
                             spacing='proportional',
                             drawedges='True',
                             orientation='vertical',
                             extend=extend,
                             ticks=tick_pos)
            if cb_labels is None:
                cb.set_ticklabels([cb_tick_fmt % k for k in cm_edge_values])
            else:
                cb.set_ticklabels(cb_labels)
            for tick in cb.ax.get_yticklabels():
                tick.set_fontsize(7)
            cb.set_label(units, fontsize=8)

            # Patch for graphics bug that affects label positions for
            # long/narrow plots
            lat_extent = np.float(lat_max) - np.float(lat_min)
            lon_extent = np.float(lon_max) - np.float(lon_min)
            aspect_ratio = abs(lon_extent / lat_extent)
            if aspect_ratio > 1.7:
                copyright_label_yadj = -0.25
            else:
                copyright_label_yadj = -0.15
            if aspect_ratio < 0.7:
                copyright_label_xadj = -0.2
                product_label_xadj = 1.4
            else:
                copyright_label_xadj = -0.1
                product_label_xadj = 1.04

            # Draw copyright and product labels
            box = TextArea(getCopyright(),
                           textprops=dict(color='k', fontsize=6))
            copyrightBox = AnchoredOffsetbox(loc=3, child=box,
                                             borderpad=0.1,
                                             bbox_to_anchor=(copyright_label_xadj, copyright_label_yadj),
                                             frameon=False,
                                             bbox_transform=ax.transAxes)
            ax.add_artist(copyrightBox)

            if product_label_str is not None:
                box = TextArea(product_label_str,
                               textprops=dict(color='k', fontsize=6))
                copyrightBox = AnchoredOffsetbox(loc=4, child=box,
                                                 borderpad=0.1,
                                                 bbox_to_anchor=(product_label_xadj, copyright_label_yadj),
                                                 frameon=False,
                                                 bbox_transform=ax.transAxes)
                ax.add_artist(copyrightBox)

            # Save figure
            plt.savefig(output_filename, dpi=150,
                        bbox_inches='tight',
                        pad_inches=0.6)
            plt.close()

            pngcrush(output_filename)

        self.queue_plot(_plot_surface_data, *args, **kwargs)

    @logger.time_and_log
    def plot_basemaps_and_colorbar(self, *args, **kwargs):

        output_filename = kwargs.get('output_filename', 'noname.png')
        fileName, fileExtension = os.path.splitext(output_filename)
        colorbar_filename = fileName + '_scale.png'
        outputfile_east = fileName + '_east.png'
        outputfile_west = fileName + '_west.png'
        worldfile_east = util.get_resource('east.pgw')
        worldfile_west = util.get_resource('west.pgw')
        shutil.copyfile(worldfile_east, fileName + '_east.pgw')
        shutil.copyfile(worldfile_west, fileName + '_west.pgw')

        regions = [{'lat_min':-90,
                    'lat_max':90,
                    'lon_min':0,
                    'lon_max':180.5,
                    'output_filename':outputfile_east},
                   {'lat_min':-90,
                    'lat_max':90,
                    'lon_min':180,
                    'lon_max':360,
                    'output_filename':outputfile_west}
                ]

        # Create colormap
        cm_edge_values = kwargs.get('cm_edge_values', None)
        cmp_name = kwargs.get('cmp_name', 'jet')
        extend = kwargs.get('extend', 'both')
        cb_label_pos = kwargs.get('cb_label_pos', None)

        if cm_edge_values is None:
            cm_edge_values = get_tick_values(data.min(), data.max(), 10)[0]

        n_colours = cm_edge_values.size - 1
        d_cmap = discrete_cmap(cmp_name, n_colours, extend=extend)

        if cb_label_pos is None:
            tick_pos = cm_edge_values
        else:
            tick_pos = cb_label_pos

        @logger.time_and_log('subprocess-plot-basemap')
        def _plot_basemap(region, lats, lons, data,
                          units='', cb_tick_fmt="%.0f", cb_labels=None,
                          proj=self._DEFAULT_PROJ, **kwargs):

            m = Basemap(projection=proj,
                        llcrnrlat=region['lat_min'],
                        llcrnrlon=region['lon_min'],
                        urcrnrlat=region['lat_max'],
                        urcrnrlon=region['lon_max'],
                        resolution=None)

            # Convert centre lat/lons to corner values required for pcolormesh
            lons2 = get_grid_edges(lons)
            lats2 = get_grid_edges(lats)

            # Plot data
            x2, y2 = m(*np.meshgrid(lons2, lats2))
            img = m.pcolormesh(x2, y2, data, shading='flat', cmap=d_cmap)
            img.set_clim(cm_edge_values.min(), cm_edge_values.max())

            m.drawmapboundary(linewidth=0.0)

            # Save figure
            plt.savefig(region['output_filename'], dpi=150,
                        bbox_inches='tight', pad_inches=0.0)
            plt.close()

        @logger.time_and_log('subprocess-plot-colorbar')
        def _plot_colorbar(lats, lons, data,
                           units='', cb_tick_fmt="%.0f",
                           cb_labels=None, extend='both',
                           proj=self._DEFAULT_PROJ, **kwargs):
            # Draw colorbar
            fig = plt.figure(figsize=(1.5,2))
            ax1 = fig.add_axes([0.05, 0.01, 0.125, 0.98])

            norm = mpl.colors.Normalize(*[cm_edge_values[0],
                                        cm_edge_values[-1]])
            cb = mpl.colorbar.ColorbarBase(
                    ax1,
                    cmap=d_cmap,
                    norm=norm,
                    orientation='vertical',
                    drawedges='True',
                    extend=extend,
                    ticks=tick_pos)
            if cb_labels is None:
                cb.set_ticklabels([cb_tick_fmt % k for k in cm_edge_values])
            else:
                cb.set_ticklabels(cb_labels)
            cb.set_label(units,
                    rotation='horizontal',
                    fontsize=6,
                    fontweight='bold')

            for tick in cb.ax.get_yticklabels():
                tick.set_fontsize(6)
                tick.set_fontweight('bold')

            plt.savefig(colorbar_filename,
                    dpi=120,
                    transparent=True)
            plt.close()
            pngcrush(colorbar_filename)

        for region in regions:
            self.queue_plot(_plot_basemap, region, *args, **kwargs)

        self.queue_plot(_plot_colorbar, *args, **kwargs)


def get_tick_values(x_min, x_max, min_ticks=4):
    """
    Automatically determine best latitude / longitude tick values for plotting.

    Input arguments:
        x_min       Minimum lat/lon value
        x_max       Maximum lat/lon value
        min_ticks   Minimum number of ticks

    Example usage:
        get_tick_values(-30,30) -> [-30., -20., -10., 0., 10., 20., 30.]
    """
    eps = 0.0001

    # Calculate base 10 exponent of the value range
    dif_exp = np.floor(np.log10(x_max - x_min))

    for k in [1.0,0.5,0.2]:
        test_interval = math.pow(10, dif_exp) * k
        start_value = np.ceil(x_min/test_interval)*test_interval
        ticks = np.arange(start_value, x_max + eps, test_interval)
        if (ticks.size >= min_ticks):
            break

    # Determine number of decimal places required for labels
    if dif_exp <= 0:
        if k >= 1.0:
            dec_places = abs(dif_exp)
        else:
            dec_places = abs(dif_exp) + 1
    else:
        dec_places = 0

    return ticks, int(dec_places)

def discrete_cmap(cmap_name, intervals, extend='both'):
    """
    Generate a discrete colour map by subsetting from a continuous matplotlib colour map.

    Input arguments
    ---------------
    cmap_name   -> Name of colour map (e.g. 'jet')
    intervals   -> Number of colour intervals (excluding out of range colour flags)
    extend      -> Specify whether to add extra colours for values that are out of range.
                   Options are 'both', 'min', 'max' or 'neither'.
    """
    if extend == 'both':
        n_colours = intervals + 2
    elif extend == 'min' or extend == 'max':
        n_colours = intervals + 1
    else:
        n_colours = intervals

    cmap = mpl.cm.get_cmap(cmap_name, n_colours)
    clrs = cmap(range(n_colours))

    if extend == 'both':
        min_colour = clrs[0,:]
        max_colour = clrs[-1,:]
        intv_colours = clrs[1:-1,:]
    elif extend == 'min':
        min_colour = clrs[0,:]
        max_colour = None
        intv_colours = clrs[1:,:]
    elif extend == 'max':
        min_colour = None
        max_colour = clrs[-1,:]
        intv_colours = clrs[:-1,:]
    else:
        min_colour = None
        max_colour = None
        intv_colours = clrs

    cmap = mpl.colors.ListedColormap(intv_colours)
    if min_colour is not None:
        cmap.set_under(min_colour)
    if max_colour is not None:
        cmap.set_over(max_colour)
    return cmap

def get_grid_edges(x):
    x = np.array(x)
    cntrs = (x[1:] + x[0:-1]) / 2.0
    edges_strt = 2*x[0] - cntrs[0]
    edges_end = 2*x[-1] - cntrs[-1]
    edges = np.append(edges_strt, cntrs)
    edges = np.append(edges, edges_end)
    return edges

@logger.time_and_log
def draw_vector_plot(m, x, y, u, v, draw_every=1, arrow_scale=10, quiverkey_value=0.5, units='ms^{-1}',
                     quiverkey_xpos=0.25, quiverkey_ypos=0.28):
    # Draw vector plot
    #
    # Input arguments:
    # ----------------
    #   x, y            -> x, y (or lon, lat) values
    #   u, v            -> vector components (i.e. Vx, Vy)
    #   draw_every      -> draw every nth arrow
    #   arrow_scale     -> scale arrow size
    #   quiverkey_value -> Quiver key value
    #   units           -> Units for quiver key label
    #   quiverkey_xpos  -> x position of quiver key
    #   quiverkey_ypos  -> y position of quiver key
    x = x[::draw_every]
    y = y[::draw_every]
    u = u[::draw_every,::draw_every]
    v = v[::draw_every,::draw_every]
    x, y = m(*np.meshgrid(x, y))
    q = m.quiver(x, y, u, v, pivot='mid', scale=arrow_scale,
                  minshaft=1, minlength=0.85, headlength=2.5, headaxislength=2.5)
    quiverkey_label = '$' + str(quiverkey_value) + units + '$'
    plt.quiverkey(q, 1.08, -0.07, quiverkey_value, quiverkey_label, coordinates='axes',
                 labelpos='N', labelsep=0.01, fontproperties={'size':'xx-small', 'weight':'1000'})
