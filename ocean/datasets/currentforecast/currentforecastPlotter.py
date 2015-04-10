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

from ocean import logger
from ocean.plotter import Plotter, COMMON_FILES, from_levels_and_colors
from ocean.config import regionConfig
from ocean.util.pngcrush import pngcrush
 
SCALE_FACTOR = 0.001

class CurrentForecastPlotter(Plotter):
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
        extend = kwargs.get('extend', 'neither')
        cb_label_pos = kwargs.get('cb_label_pos', None)
        clabel = kwargs.get('clabel', False)
        vector = kwargs.get('vector', False)
        regionName = kwargs.get('regionName', None)

#        d_cmap = mpl.colors.ListedColormap(np.array(cmArray) / 255.0)
        d_cmap, norm = from_levels_and_colors(cm_edge_values, None, cmp_name, extend=extend)

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
        def _plot_basemap(region, lats, lons, data, time, 
                          units='', cb_tick_fmt="%.0f", cb_labels=None,
                          proj=self._DEFAULT_PROJ, **kwargs):

            m = Basemap(projection=proj,
                        llcrnrlat=region['lat_min'],
                        llcrnrlon=region['lon_min'],
                        urcrnrlat=region['lat_max'],
                        urcrnrlon=region['lon_max'],
                        resolution='i')

            # Plot data
            x2, y2 = m(*np.meshgrid(lons, lats))

            u = data[0]
            v = data[1]
            mag = np.sqrt(u**2 + v**2)

            img = m.pcolormesh(x2, y2, mag, shading='flat', cmap=d_cmap, norm=norm)
            img.set_clim(cm_edge_values.min(), cm_edge_values.max())

            #plot contouring labels
            if clabel:
                labels = plt.clabel(img, cm_edge_values[::4], inline=True, fmt='%.0f', colors='k', fontsize=5, zorder=2)
                bbox_props = dict(boxstyle="round", fc="w", ec="w", alpha=0.9)
                for text in labels:
                    text.set_linespacing(1)
                    text.set_bbox(bbox_props)
 
            #plot vectors
            every = 10 
            lons = lons[::every]
            lats = lats[::every]
            x2, y2 = m(*np.meshgrid(lons, lats))
            print time
#            u2 = u[time, ::every, ::every]
#            v2 = v[time, ::every, ::every]
            u2 = u[::every, ::every]
            v2 = v[::every, ::every]
            rad = np.arctan2(v2, u2)
            m.quiver(x2, y2, np.cos(rad), np.sin(rad), scale=10, zorder=3, scale_units='inches', pivot='middle')
            m.drawmapboundary(linewidth=0.0)

            m.drawcoastlines(linewidth=0.5, color='#505050', zorder=8)
#            m.fillcontinents(color='#F1EBB7', zorder=7)
            m.fillcontinents(color='white', zorder=7)

            # Save figure
            plt.savefig(region['output_filename'], dpi=120,
                        bbox_inches='tight', pad_inches=0.0)
            plt.close()
            pngcrush(region['output_filename'])

        @logger.time_and_log('subprocess-plot-colorbar')
        def _plot_colorbar(lats, lons, data, time,
                           units='', cb_tick_fmt="%.0f",
                           cb_labels=None, extend='both',
                           proj=self._DEFAULT_PROJ, **kwargs):
            # Draw colorbar
            fig = plt.figure(figsize=(1.5,2))
            ax1 = fig.add_axes([0.05, 0.02, 0.125, 0.96])

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
 
        if regionName is not None:
            regions = [convertRegionBounds(regionConfig.regions[regionName], outputfile_map)]
        for region in regions:
            self.queue_plot(_plot_basemap, region, *args, **kwargs)

        self.queue_plot(_plot_colorbar, *args, **kwargs)

def convertRegionBounds(regionBound, outputfile):

    bounds = {'lat_min':regionBound[1]['llcrnrlat'],
     'lat_max':regionBound[1]['urcrnrlat'],
     'lon_min':regionBound[1]['llcrnrlon'],
     'lon_max':regionBound[1]['urcrnrlon'],
     'output_filename':outputfile}    
    return bounds
