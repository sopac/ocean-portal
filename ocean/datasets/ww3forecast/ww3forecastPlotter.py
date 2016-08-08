#
# (c) 2015 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea
import math
from datetime import datetime, timedelta

try:
    from mpl_toolkits.axes_grid1 import make_axes_locatable
except ImportError:
    # support older matplotlib
    from mpl_toolkits.axes_grid import make_axes_locatable

from ocean import logger
from ocean.netcdf.grid import Grid, GridWrongFormat
from ocean.plotter import Plotter, COMMON_FILES, getCopyright, get_tick_values, discrete_cmap
from ocean.util.pngcrush import pngcrush
from ocean.util.gdalprocess import gdal_process
 
customColorMap = {"wav_cm": [[187, 214, 232],
                             [107, 174, 214],
                             [49, 130, 189],
                             [8, 81, 156],
                             [186, 228, 179],
                             [116, 196, 118],
                             [49, 163, 84],
                             [0, 109, 44],
                             [255, 255, 178],
                             [254, 204, 92],
                             [253, 141, 60],
                             [240, 59, 32],
                             [255, 0, 0],
                             [204, 51, 204]],
                 "wnd_cm": [[239, 248, 253],
                            [204, 240, 254],
                            [156, 219, 252],
                            [172, 255, 167],
                            [126, 222, 120],
                            [229, 229, 117],
                            [255, 125, 75],
                            [229, 39, 13],
                            [153, 0, 0]]}

basemapColorMap = {"wav_cm": [[255, 255, 255],
                              [235, 235, 235],
                              [216, 216, 216],
                              [196, 196, 196],
                              [177, 177, 177],
                              [157, 157, 157],
                              [137, 137, 137],
                              [118, 118, 118],
                              [98, 98, 98],
                              [78, 78, 78],
                              [59, 59, 59],
                              [39, 39, 39],
                              [20, 20, 20],
                              [0, 0, 0]],
                 "wnd_cm": [[255, 255, 255],
                            [223, 223, 223],
                            [191, 191, 191],
                            [159, 159, 159],
                            [128, 128, 128],
                            [96, 96, 96],
                            [64, 64, 64],
                            [32, 32, 32],
                            [0, 0, 0]]}

customTicks = {"sig": [0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 10, 20],
               "pk": [0, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 30],
               "wnd": [0, 5, 10, 15, 20, 25, 30, 35, 45, 100]}

variableConfig = {"sig_wav_ht": ("Combined Sea and Swell Wave Height",
                                        {"cm" : 'wav_cm',
                                        "cb_ticks" : 'sig',
                                        "unitStr" : 'Metres',
                                        "cb_tick_fmt" : '%.1f',
                                        "clabel" : False,
                                        "vector" : True}),
                         "sig_ht_wnd_sea": ("Sea Wave Height",
                                        {"cm" : 'wav_cm',
                                        "cb_ticks" : 'sig',
                                        "unitStr" : 'Metres',
                                        "cb_tick_fmt" : '%.1f',
                                        "clabel" : False,
                                        "vector" : True}),
                        "sig_ht_sw1": ("Swell Wave Height",
                                        {"cm" : 'wav_cm',
                                        "cb_ticks" : 'sig',
                                        "unitStr" : 'Metres',
                                        "cb_tick_fmt" : '%.1f',
                                        "clabel" : False,
                                        "vector" : True}),
                        "pk_wav_per": ("Peak Wave Period",
                                        {"cm" : 'wav_cm',
                                        "cb_ticks" : 'pk',
                                        "unitStr" : 'Seconds',
                                        "cb_tick_fmt" : '%2d',
                                        "clabel" : True,
                                        "vector" : False}),
                        "wnd_spd": ("Wind Speed",
                                        {"cm" : 'wnd_cm',
                                        "cb_ticks" : 'wnd',
                                        "unitStr" : 'Speed(kts)',
                                        "cb_tick_fmt" : '%3d',
                                        "clabel" : False,
                                        "vector" : True})
    }

class Ww3ForecastPlotter(Plotter):

    def get_formatted_date(self, params={}):
        if 'step' in params:
            return datetime.strptime(params['forecast'][params['step']]['datetime'], '%d-%m-%Y %H:%M').strftime('%d %B %Y %H:%M') + " UTC"
        else:
            return ''

    def get_title(self, params={}):
        return variableConfig[params['variable']][0]

    def get_colormap(self, params={}):
        return variableConfig[params['variable']][1]['cm']

    def get_ticks(self, params={}):
        return variableConfig[params['variable']][1]['cb_ticks']

    def get_units(self, params={}):
        return variableConfig[params['variable']][1]['unitStr']

    def get_ticks_format(self, params={}):
        return variableConfig[params['variable']][1]['cb_tick_fmt']

    def get_labels(self, params={}):
        return variableConfig[params['variable']][1]['clabel']

    def get_vector(self, params={}):
        return variableConfig[params['variable']][1]['vector']

    def get_extend(self, params={}):
        return 'neither'

    def get_fill_color(self, params={}):
        #return '1.0'
        return '0.02'

    def get_smooth_fac(self, params={}):
        return 1

    def get_contourlines(self, params={}):
        return False

    def get_contour_labels(self, params={}):
        return False

    def get_colors(self, params={}):
        return None

    def get_plotstyle(self, params={}):
        return 'contourf'

    def get_colormap_strategy(self, params={}):
        return 'levels'

    """
        Plot mapis and color bars for WW3 forecast data. 
    """
    def plot_basemaps_and_colorbar(self, *args, **kwargs):
        #Plots the image for the map overlay.

        output_filename = kwargs.get('output_filename', 'noname.png')
        fileName, fileExtension = os.path.splitext(output_filename)
        colorbar_filename = fileName + COMMON_FILES['scale']
        outputfile_map = fileName + COMMON_FILES['mapimg']

        # Create colormap
        cm_edge_values = kwargs.get('cm_edge_values', None)
        cmp_name = kwargs.get('cmp_name', 'jet')
        extend = kwargs.get('extend', 'both')
        cb_label_pos = kwargs.get('cb_label_pos', None)
        clabel = kwargs.get('clabel', False)
        vector = kwargs.get('vector', False)
        fill_color = kwargs.get('fill_color', '1.0')

        overlay_grid = kwargs.get('overlay_grid', None)

        cmArray = customColorMap[cmp_name]
        basemapArray = basemapColorMap[cmp_name]
#        d_cmap = mpl.colors.ListedColormap(np.array(cmArray) / 255.0)
        d_cmap, norm = from_levels_and_colors(customTicks[cm_edge_values], np.array(cmArray) / 255.0)
        basemap_cmap, basemap_norm = from_levels_and_colors(customTicks[cm_edge_values], np.array(basemapArray) / 255.0)
        cm_edge_values = np.array(customTicks[cm_edge_values])

        if cb_label_pos is None:
            tick_pos = cm_edge_values
        else:
            tick_pos = cb_label_pos

        regions = [{'lat_min':-90,
                    'lat_max':90,
                    'lon_min':110,
                    'lon_max':290,
                    'output_filename':outputfile_map}
                ]

        @logger.time_and_log('subprocess-plot-basemap')
        def _plot_basemap(region, lats, lons, data, 
                          units='', cb_tick_fmt="%.0f", cb_labels=None,
                          proj=self._DEFAULT_PROJ, **kwargs):
            m = Basemap(projection=proj,
                        llcrnrlat=region['lat_min'],
                        llcrnrlon=region['lon_min'],
                        urcrnrlat=region['lat_max'],
                        urcrnrlon=region['lon_max'],
                        resolution='i')

            m.drawmapboundary(linewidth=0.0, fill_color=fill_color)
            # Plot data
            x2, y2 = m(*np.meshgrid(lons, lats))
#            img = m.pcolormesh(x2, y2, data, shading='flat', cmap=d_cmap, norm=norm)
            #img = m.contourf(x2, y2, data, levels=cm_edge_values, cmap=d_cmap, norm=norm, antialiased=True, zorder=0)
            #img = m.contourf(x2, y2, data, levels=cm_edge_values, cmap=basemap_cmap, norm=norm, antialiased=False, zorder=0)
            img = m.contourf(x2, y2, data, levels=cm_edge_values, cmap=basemap_cmap, norm=norm, antialiased=False)
            img.set_clim(cm_edge_values.min(), cm_edge_values.max())
            
            #bug798 comment out
            #img = plt.contour(x2, y2, data, levels=cm_edge_values, colors='w', norm=norm, linewidths=0.5, zorder=1)
            plt.savefig(region['output_filename'], dpi=120,
                        bbox_inches='tight', pad_inches=0.0)
            # generate shape file
            gdal_process(region['output_filename'], region['lon_min'],
                                                    region['lat_max'],
                                                    region['lon_max'],
                                                    region['lat_min'])

            pngcrush(region['output_filename'])

            baseName = os.path.splitext(region['output_filename'])[0]

            #plot contouring labels
            if clabel:
                plt.clf()
             #   m.drawmapboundary(linewidth=0.0, fill_color=fill_color)
                m.drawmapboundary(linewidth=0.0)
                #labels = plt.clabel(img, cm_edge_values[::4], inline=True, fmt='%.0f', colors='k', fontsize=5, zorder=2)
                img = plt.contour(x2, y2, data, levels=cm_edge_values, colors='w', norm=norm, linewidths=0.5, zorder=1)
                labels = plt.clabel(img, cm_edge_values[::4], inline=True, fmt='%.0f', colors='k', fontsize=5)
            #    labels = plt.clabel(img, cm_edge_values[::4], inline=True, fmt='%.0f', colors='0.06', fontsize=5, zorder=2)
             #   bbox_props = dict(boxstyle="round", fc="w", ec="w", alpha=0.9)
                bbox_props = dict(boxstyle="round", fc="w", ec="w")
                for text in labels:
                    text.set_linespacing(1)
                    text.set_bbox(bbox_props)
                labelFile = baseName + '_label.png'
                plt.savefig(labelFile, dpi=120,
                            bbox_inches='tight', pad_inches=0.0, transparent=True)
                # generate shape file
                gdal_process(labelFile, region['lon_min'],
                                                        region['lat_max'],
                                                        region['lon_max'],
                                                        region['lat_min'])

                pngcrush(labelFile)

            #extract the overlay grid
            if vector:
                plt.clf()
                m.drawmapboundary(linewidth=0.0)
#                overlay_grid = kwargs.get('overlay_grid', None)
                every = 10 
               # every = 15 
                lons = lons[::every]
                lats = lats[::every]
                x2, y2 = m(*np.meshgrid(lons, lats))
                if overlay_grid is not None:
                    radians_array = np.radians(overlay_grid)
                    radians_array = np.pi + radians_array
                    radians_array = radians_array[::every, ::every]
                m.quiver(x2, y2, np.sin(radians_array), np.cos(radians_array), scale=60, zorder=3)
                #m.quiver(x2, y2, np.sin(radians_array), np.cos(radians_array), scale=60, zorder=3, color='0.06', antialiased=True)
                #m.quiver(x2, y2, np.sin(radians_array), np.cos(radians_array), scale=60, zorder=3, color='0.06', antialiased=False)
                #m.quiver(x2, y2, np.sin(radians_array), np.cos(radians_array), scale=60, headwidth=4, headlength=4.5, headaxislength=2, zorder=3, color='0.06', antialiased=False)
                #m.quiver(x2, y2, np.sin(radians_array), np.cos(radians_array), scale=60, zorder=3, color='0.06', antialiased=False, width=0.001)
                #m.quiver(x2, y2, np.sin(radians_array), np.cos(radians_array), scale=60, zorder=3, color='0.06', edgecolor='0.06', antialiased=False, headaxislength=2.5, headlength=3, linewidths=(0.01,))
                arrowFile = baseName + '_arrow.png'
                plt.savefig(arrowFile, dpi=120,
                            bbox_inches='tight', pad_inches=0.0, transparent=True)
                # generate shape file
                gdal_process(arrowFile, region['lon_min'],
                                        region['lat_max'],
                                        region['lon_max'],
                                        region['lat_min'])

                pngcrush(labelFile)

            m.drawmapboundary(linewidth=0.0, fill_color=fill_color)

#            m.drawcoastlines(linewidth=0.5, color='#505050', zorder=8)
#            m.fillcontinents(color='#F1EBB7', zorder=7)

            # Save figure
#            plt.savefig(region['output_filename'], dpi=120,
#                        bbox_inches='tight', pad_inches=0.0)
            plt.close()

            # generate shape file
#            gdal_process(region['output_filename'], region['lon_min'],
#                                                    region['lat_max'],
#                                                    region['lon_max'],
#                                                    region['lat_min'])

#            pngcrush(region['output_filename'])

        @logger.time_and_log('subprocess-plot-colorbar')
        def _plot_colorbar(lats, lons, data,
                           units='', cb_tick_fmt="%.0f",
                           cb_labels=None, extend='both',
                           proj=self._DEFAULT_PROJ, **kwargs):
            # Draw colorbar
            fig = plt.figure(figsize=(1.5,2))
            ax1 = fig.add_axes([0.05, 0.02, 0.125, 0.96])

#            norm = mpl.colors.Normalize(*[cm_edge_values[0],
#                                        cm_edge_values[-1]])
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

    def plot_surface_data(self, *args, **kwargs):
        def _plot_surface_data(lats, lons, data,
                               lat_min, lat_max, lon_min, lon_max,
                               output_filename='noname.png', title='', units='',
                               cm_edge_values=None, cb_tick_fmt="%.0f",
                               cb_labels=None, cb_label_pos=None,
                               colormap_strategy='nonlinear',
                               cmp_name='jet', colors=None, extend='both',
                               fill_color='1.0',
                               plotStyle='contourf', contourLines=True,
                               contourLabels=True, smoothFactor=1,
                               proj=self._DEFAULT_PROJ, product_label_str=None,
                               vlat=None, vlon=None, u=None, v=None,
                               draw_every=1, arrow_scale=10,
                               vector=False, overlay_grid = None,
                               resolution=None, area=None, boundaryInUse='True'):

            cmArray = customColorMap[cmp_name]

            if colormap_strategy == 'discrete':
                n_colours = cm_edge_values.size - 1
                d_cmap = discrete_cmap(cmp_name, n_colours, extend)
                norm = None
            elif colormap_strategy == 'levels':
                d_cmap, norm = from_levels_and_colors(customTicks[cm_edge_values], np.array(cmArray) / 255.0)
            elif colormap_strategy == 'nonlinear':
                d_cmap, norm = from_levels_and_colors(customTicks[cm_edge_values], None, cmp_name, extend)

            cm_edge_values = np.array(customTicks[cm_edge_values])

            m = Basemap(projection=proj,
                        llcrnrlat=lat_min, llcrnrlon=lon_min,
                        urcrnrlat=lat_max, urcrnrlon=lon_max,
                        resolution='i')

            # Plot data
            x2, y2 = m(*np.meshgrid(lons, lats))

            img = m.contourf(x2, y2, data, levels=cm_edge_values, cmap=d_cmap, norm=norm, antialiased=True, zorder=0)
            img.set_clim(cm_edge_values.min(), cm_edge_values.max())

            #plot contouring labels
            if contourLabels:
                labels = plt.clabel(img, cm_edge_values[::4], inline=True, fmt='%.0f', colors='k', fontsize=5, zorder=2)
                bbox_props = dict(boxstyle="round", fc="w", ec="w", alpha=0.9)
                for text in labels:
                    text.set_linespacing(1)
                    text.set_bbox(bbox_props)

            #plot vectors
            if vector:
                every = 10
                lons = lons[::every]
                lats = lats[::every]
                x2, y2 = m(*np.meshgrid(lons, lats))
                if overlay_grid is not None:
                    radians_array = np.radians(overlay_grid)
                    radians_array = np.pi + radians_array
                    radians_array = radians_array[::every, ::every]
                m.quiver(x2, y2, np.sin(radians_array), np.cos(radians_array), scale=60, zorder=3)

            # Draw land, coastlines, parallels, meridians and add title
            m.drawmapboundary(linewidth=1.0, fill_color=fill_color)
            m.drawcoastlines(linewidth=0.5, color='#505050', zorder=8)
            m.fillcontinents(color='0.58', zorder=7)

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

            if boundaryInUse == 'True':
                cb = plt.colorbar(img, cax=cax,
    #                             spacing='proportional',
                                 spacing='uniform',
                                 drawedges='False',
                                 orientation='vertical',
                                 extend=extend,
                                 ticks=tick_pos,
                                 boundaries=cm_edge_values)
            else:
                cb = plt.colorbar(img, cax=cax,
                                 spacing='uniform',
                                 drawedges='False',
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
                copyright_label_yadj = -0.10
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
                        bbox_inches='tight', pad_inches=0.6)

            plt.close()

            pngcrush(output_filename)

        self.queue_plot(_plot_surface_data, *args, **kwargs)

def from_levels_and_colors(levels, colors, extend='neither'):
    """
    A helper routine to generate a cmap and a norm instance which
    behave similar to contourf's levels and colors arguments.

    Parameters
    ----------
    levels : sequence of numbers
        The quantization levels used to construct the :class:`BoundaryNorm`.
        Values ``v`` are quantizized to level ``i`` if
        ``lev[i] <= v < lev[i+1]``.
    colors : sequence of colors
        The fill color to use for each level. If `extend` is "neither" there
        must be ``n_level - 1`` colors. For an `extend` of "min" or "max" add
        one extra color, and for an `extend` of "both" add two colors.
    extend : {'neither', 'min', 'max', 'both'}, optional
        The behaviour when a value falls out of range of the given levels.
        See :func:`~matplotlib.pyplot.contourf` for details.

    Returns
    -------
    (cmap, norm) : tuple containing a :class:`Colormap` and a \
                   :class:`Normalize` instance
    """
    colors_i0 = 0
    colors_i1 = None

    if extend == 'both':
        colors_i0 = 1
        colors_i1 = -1
        extra_colors = 2
    elif extend == 'min':
        colors_i0 = 1
        extra_colors = 1
    elif extend == 'max':
        colors_i1 = -1
        extra_colors = 1
    elif extend == 'neither':
        extra_colors = 0
    else:
        raise ValueError('Unexpected value for extend: {0!r}'.format(extend))

    n_data_colors = len(levels) - 1
    n_expected_colors = n_data_colors + extra_colors
    if len(colors) != n_expected_colors:
        raise ValueError('With extend == {0!r} and n_levels == {1!r} expected'
                         ' n_colors == {2!r}. Got {3!r}.'
                         ''.format(extend, len(levels), n_expected_colors,
                                   len(colors)))

    cmap = mpl.colors.ListedColormap(colors[colors_i0:colors_i1], N=n_data_colors)

    if extend in ['min', 'both']:
        cmap.set_under(colors[0])
    else:
        cmap.set_under('none')

    if extend in ['max', 'both']:
        cmap.set_over(colors[-1])
    else:
        cmap.set_over('none')

    cmap.colorbar_extend = extend

    norm = mpl.colors.BoundaryNorm(levels, ncolors=n_data_colors)
    return cmap, norm

def get_grid_edges(x):
    x = np.array(x)
    cntrs = (x[1:] + x[0:-1]) / 2.0
    edges_strt = 2*x[0] - cntrs[0]
    edges_end = 2*x[-1] - cntrs[-1]
    edges = np.append(edges_strt, cntrs)
    edges = np.append(edges, edges_end)
    return edges

def get_vector_plot_settings(lat_min, lat_max, lon_min, lon_max):
    lat_extent = lat_max - lat_min
    lon_extent = lon_max - lon_min
    max_extent = max(lat_extent, lon_extent)
    if max_extent >= 80:
        draw_every = None
        arrow_scale = None
    elif (max_extent >= 60) and (max_extent < 80):
        draw_every = 10
        arrow_scale = 20
    elif (max_extent >= 20) and (max_extent < 60):
        draw_every = 5
        arrow_scale = 15
    elif (max_extent >= 10) and (max_extent < 20):
        draw_every = 5
        arrow_scale = 10
    elif (max_extent >= 7) and (max_extent < 10):
        draw_every = 4
        arrow_scale = 5
    elif (max_extent >= 4) and (max_extent < 7):
        draw_every = 3
        arrow_scale = 5
    else:
        draw_every = 1
        arrow_scale = 5
    return draw_every, arrow_scale

def format_longitude(x, pos=None):
    x = np.mod(x + 180, 360) - 180
    if x==-180:
        return u"{0:.0f}\u00B0".format(abs(x))
    elif x<0:
        return u"{0:.0f}\u00B0W".format(abs(x))
    else:
        return u"{0:.0f}\u00B0E".format(x)

def format_latitude(y, pos=None):
    if y<0:
        return u"{0:.0f}\u00B0S".format(abs(y))
    elif y>0:
        return u"{0:.0f}\u00B0N".format(y)
    else:
        return u"{0:.0f}\u00B0".format(y)
