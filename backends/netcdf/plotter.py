#!/user/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Nicholas Summons <n.summons@bom.gov.au>
"""
Plotter is the base class for plotting.
"""

import os
import bisect
import math
import shutil
import datetime
import sys

from matplotlib import mpl
from mpl_toolkits.basemap import Basemap
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea
from matplotlib.transforms import offset_copy
import matplotlib.pyplot as plt

import numpy as np

import ocean.util as util
import ocean.util.regionConfig as rc

COMMON_FILES = {
    'img': '.png',
    'mapeast': '_east.png',
    'mapeastw': '_east.pgw',
    'mapwest': '_west.png',
    'mapwestw': '_west.pgw',
    'scale': '_scale.png',
}

def getCopyright():
    return ur'\u00A9' + "Commonwealth of Australia "\
           + datetime.date.today().strftime('%Y')\
           + "\nAustralian Bureau of Meteorology, COSPPac COMP"

class Plotter:
    """The base class for plotting netCDF files."""

    _DEFAULT_PROJ = "cyl" #Equidistant Cylindrical Projection
    serverConfig = None

    def __init__(self):
        """The simple constructor of Plotter"""
        self.serverConfig = util.get_server_config()
        self.regionConfig = rc.regions

    def contour(self, data, lats, lons, variable, config, outputFile,\
                title, lllat, lllon, urlat, urlon, res = 'h', proj=_DEFAULT_PROJ,\
                contourLines = False, centerLabel = False):
	"""
	Plot the input data with contours using the specified project and save the plot to the output file.
	"""
	#*******************************************
        #* Generate image for the thumbnail and download
        #*******************************************
	m = Basemap(projection=proj, llcrnrlat=lllat, llcrnrlon=lllon,\
                    urcrnrlat=urlat, urcrnrlon=urlon, resolution=res)
        x, y = m(*np.meshgrid(lons, lats))
	if contourLines:
	    contourPlt = m.contour(x, y, data, levels=config.getContourLevels(variable), colors='k', linewidths=0.4)
#            plt.clabel(contourPlt, inline=True, fmt='%3.1f', fontsize=6)

        delon = lons[1]-lons[0]; delat = lats[1]-lats[0]
        lons = (lons - 0.5*delon).tolist()
        lons.append(lons[-1]+delon)
        lons = np.array(lons,np.float64)
        lats = (lats - 0.5*delat).tolist()
        lats.append(lats[-1]+delat)
        lats = np.array(lats,np.float64)

        x, y = m(*np.meshgrid(lons, lats))
        m.pcolormesh(x, y, data, shading='flat', cmap=config.getColorMap(variable))

#        m.contourf(x, y, data, levels=config.getContourLevels(variable), shading='flat', cmap=config.getColorMap(variable))
	m.drawcoastlines(linewidth=0.1, zorder=6)
        m.fillcontinents(color='#F1EBB7', zorder=7)

        parallels, p_dec_places = get_tick_values(lllat, urlat)
        meridians, m_dec_places = get_tick_values(lllon, urlon)
        m.drawparallels(parallels, labels=[True, False, False, False], fmt='%.' + str(p_dec_places) + 'f', fontsize=6, dashes=[3, 3], color='gray')
        m.drawmeridians(meridians, labels=[False, False, False, True], fmt='%.' + str(m_dec_places) + 'f', fontsize=6, dashes=[3, 3], color='gray')

        plt.title(title, fontsize=10)
        plt.clim(*config.getColorBounds(variable))
        ax = plt.gca()
        box = TextArea(getCopyright(), textprops=dict(color='k', fontsize=6))
        copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor= (-0.1, -0.3), frameon=False, bbox_transform=ax.transAxes)
#        copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor= (0,0,1,1), frameon=False, bbox_transform=plt.gcf().transFigure)
        ax.add_artist(copyrightBox)
#        cax = plt.axes([0.93, 0.18, 0.02, 0.65])
#        cbar = plt.colorbar(format=config.getValueFormat(variable), cax=cax, extend='both')
   
#        cbar = plt.colorbar(format=config.getValueFormat(variable), extend='both', shrink=0.5)
        cbar = plt.colorbar(format=config.getValueFormat(variable), extend='both')

        cbar.set_label(config.getUnit(variable), rotation='horizontal', fontsize=6)


        l,b,w,h = plt.gca().get_position().bounds
        ll,bb,ww,hh = cbar.ax.get_position().bounds
        cbar.ax.set_position([ll, b+0.25*h, ww, h*0.5])

	colorbarLabels = config.getColorbarLabels(variable)
	if len(colorbarLabels) != 0:
            cbar.ax.set_yticklabels(colorbarLabels)

        for tick in cbar.ax.get_yticklabels():
            tick.set_fontsize(6)
            if centerLabel:
                try:
                    tick.set_transform(offset_copy(cbar.ax.transData, x=10, y=-40, units='dots'))
                except KeyError:
                    pass

        plt.savefig(self.serverConfig["outputDir"] + outputFile + '.png', dpi=150, bbox_inches='tight', pad_inches=1., bbox_extra_artists=[copyrightBox])
        plt.close()

    def plotScale(self, data, variable, config, outputFile):
        # plot another colour bar
        fig = plt.figure(figsize=(0.75,2))
        ax1 = fig.add_axes([0.05, 0.01, 0.25, 0.98])

        norm = mpl.colors.Normalize(*config.getColorBounds(variable))
        cb1 = mpl.colorbar.ColorbarBase(ax1,
                cmap=config.getColorMap(variable),
                norm=norm,
                orientation='vertical',
                format=config.getValueFormat(variable),
                extend='both')
        cb1.set_label(config.getUnit(variable),
                rotation='horizontal',
                fontsize=6)

        for tick in cb1.ax.get_yticklabels():
            tick.set_fontsize(6)

        plt.savefig(self.serverConfig['outputDir'] + outputFile + '_scale.png',
                dpi=120,
                transparent=True)
        plt.close()

    def contourBasemapWest(self, data, lats, lons, variable, config, outputFile,\
                           lllat=-90, lllon=180, urlat=90, urlon=360, proj=_DEFAULT_PROJ,\
                           contourLines=False,  worldfile=None):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """

        if not worldfile:
            worldfile = util.get_resource('west.pgw')

        #left part
        m = Basemap(projection=proj, llcrnrlat=lllat, llcrnrlon=lllon,\
                   urcrnrlat=urlat, urcrnrlon=urlon, resolution=None)
        x, y = m(*np.meshgrid(lons, lats))

        #Plot the data
	if contourLines:
	    m.contour(x, y, data, levels=config.getContourLevels(variable), colors='k', linewidths=0.4)
        m.contourf(x, y, data, levels=config.getContourLevels(variable), shading='flat', cmap=config.getColorMap(variable))
        plt.clim(*config.getColorBounds(variable))

        #Do not draw the black border around the map by setting the linewidth to 0
        m.drawmapboundary(linewidth=0.0)

        #Save the figure with no white padding around the map.
        plt.savefig(self.serverConfig["outputDir"] + outputFile + '_west.png', dpi=150, bbox_inches='tight', pad_inches=0)
        plt.close()
        shutil.copyfile(worldfile, self.serverConfig["outputDir"] + outputFile + '_west.pgw')

    def contourBasemapEast(self, data, lats, lons, variable, config, outputFile,\
                        lllat=-90, lllon=0, urlat=90, urlon=180.5, proj=_DEFAULT_PROJ,\
                        contourLines=False,  worldfile=None):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """

        if not worldfile:
            worldfile = util.get_resource('east.pgw')

        m = Basemap(projection=proj, llcrnrlat=lllat, llcrnrlon=lllon,\
                   urcrnrlat=urlat, urcrnrlon=urlon, resolution=None)
        x, y = m(*np.meshgrid(lons, lats))

        #Plot the data
	if contourLines:
	    m.contour(x, y, data, levels=config.getContourLevels(variable), colors='k', linewidths=0.4)
        m.contourf(x, y, data, levels=config.getContourLevels(variable), shading='flat', cmap=config.getColorMap(variable))
        plt.clim(*config.getColorBounds(variable))

        #Do not draw the black border around the map by setting the linewidth to 0
        m.drawmapboundary(linewidth=0.0)

        #Save the figure with no white padding around the map.
        plt.savefig(self.serverConfig["outputDir"] + outputFile + '_east.png', dpi=150, bbox_inches='tight', pad_inches=0)
        plt.close()
        shutil.copyfile(worldfile, self.serverConfig["outputDir"] + outputFile + '_east.pgw')


    def plot(self, data, lats, lons, variable, config, outputFile, lllat, lllon, urlat, urlon, res = 'h', proj=_DEFAULT_PROJ, centerLabel = False, **args):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """
        #*******************************************
        #* Generate image for the thumbnail and download
        #*******************************************
        m = Basemap(projection=proj, llcrnrlat=lllat, llcrnrlon=lllon,\
                    urcrnrlat=urlat, urcrnrlon=urlon, resolution=res)
        x, y = m(*np.meshgrid(lons, lats))
        m.pcolormesh(x, y, data, shading='flat', cmap=config.getColorMap(variable))
        m.drawcoastlines(linewidth=0.1, zorder=6)
#        m.fillcontinents(color='#F1EBB7', zorder=7)
        m.fillcontinents(color='#cccccc', zorder=7)

        parallels, p_dec_places = get_tick_values(lllat, urlat)
        meridians, m_dec_places = get_tick_values(lllon, urlon)
        m.drawparallels(parallels, labels=[True, False, False, False], fmt='%.' + str(p_dec_places) + 'f', fontsize=6, dashes=[3, 3], color='gray')
        m.drawmeridians(meridians, labels=[False, False, False, True], fmt='%.' + str(m_dec_places) + 'f', fontsize=6, dashes=[3, 3], color='gray')

        title = ''
        if hasattr(config, 'getPeriodPrefix') and 'period' in args:
            title += config.getPeriodPrefix(args['period'])

        title += config.getTitle(variable) + args['formattedDate']
        plt.title(title, fontsize=8)
        plt.clim(*config.getColorBounds(variable))
        ax = plt.gca()
        box = TextArea(getCopyright(), textprops=dict(color='k', fontsize=6))
        copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor= (-0.1, -0.3), frameon=False, bbox_transform=ax.transAxes)
#        copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor= (0,0,1,1), frameon=False, bbox_transform=plt.gcf().transFigure)
        ax.add_artist(copyrightBox)

#        cax = plt.axes([0.93, 0.18, 0.02, 0.65])
#        cbar = plt.colorbar(format=config.getValueFormat(variable), cax=cax, extend='both')
#        cbar = plt.colorbar(format=config.getValueFormat(variable), cax=cax, extend='both')
#        cbar = plt.colorbar(format=config.getValueFormat(variable), extend='both', shrink=0.5)
        cbar = plt.colorbar(format=config.getValueFormat(variable), extend='both')
        
        cbar.set_label(config.getUnit(variable), rotation='horizontal', fontsize=6)
#        cbar.set_label(ax.get_window_extent(), rotation='horizontal')

        l,b,w,h = plt.gca().get_position().bounds
        ll,bb,ww,hh = cbar.ax.get_position().bounds
        cbar.ax.set_position([ll, b+0.25*h, ww, h*0.5])

        colorbarLabels = config.getColorbarLabels(variable)
        if len(colorbarLabels) != 0:
            cbar.ax.set_yticklabels(colorbarLabels)

        for tick in cbar.ax.get_yticklabels():
            tick.set_fontsize(6)
            if centerLabel:
                try:
                    tick.set_transform(offset_copy(cbar.ax.transData, x=10, y=40, units='dots'))
                except KeyError:
                    pass

        plt.savefig(self.serverConfig["outputDir"] + outputFile + '.png', dpi=150, bbox_inches='tight', pad_inches=0.3, bbox_extra_artists=[copyrightBox])
        plt.close()

    def plotBasemapWest(self, data, lats, lons, variable, config, outputFile,\
                        lllat=-90, lllon=180, urlat=90, urlon=360,
                        proj=_DEFAULT_PROJ, worldfile='west.pgw'):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """

        worldfile = util.get_resource(worldfile)

        #left part
        m = Basemap(projection=proj, llcrnrlat=lllat, llcrnrlon=lllon,\
                   urcrnrlat=urlat, urcrnrlon=urlon, resolution=None)
        x, y = m(*np.meshgrid(lons, lats))

        #Plot the data
        m.pcolormesh(x, y, data, shading='flat', cmap=config.getColorMap(variable))
        plt.clim(*config.getColorBounds(variable))

        #Do not draw the black border around the map by setting the linewidth to 0
        m.drawmapboundary(linewidth=0.0)

        #Save the figure with no white padding around the map.
        plt.savefig(self.serverConfig["outputDir"] + outputFile + '_west.png', dpi=150, bbox_inches='tight', pad_inches=0)
        plt.close()
        shutil.copyfile(worldfile, self.serverConfig["outputDir"] + outputFile + '_west.pgw')

    def plotBasemapEast(self, data, lats, lons, variable, config, outputFile,\
                        lllat=-90, lllon=0, urlat=90, urlon=180.5,
                        proj=_DEFAULT_PROJ, worldfile='east.pgw'):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """

        worldfile = util.get_resource(worldfile)

        #right part
        m = Basemap(projection=proj, llcrnrlat=lllat, llcrnrlon=lllon,\
                   urcrnrlat=urlat, urcrnrlon=urlon, resolution=None)
        x, y = m(*np.meshgrid(lons, lats))

        #Plot the data
        m.pcolormesh(x, y, data, shading='flat', cmap=config.getColorMap(variable))
        plt.clim(*config.getColorBounds(variable))

        #Do not draw the black border around the map by setting the linewidth to 0
        m.drawmapboundary(linewidth=0.0)

        #Save the figure with no white padding around the map.
        plt.savefig(self.serverConfig["outputDir"] + outputFile + '_east.png', dpi=150, bbox_inches='tight', pad_inches=0)
        plt.close()
        shutil.copyfile(worldfile, self.serverConfig["outputDir"] + outputFile + '_east.pgw')

    def plotlatx(self, data, dep, lons, variable, config, outputFile, **args):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """
        #*******************************************
        #* Generate image for the thumbnail and download
        #*******************************************
        plt.pcolormesh(lons,(-1*dep),data, shading='flat', cmap=config.getColorMap(variable))
        plt.ylabel('m', rotation='horizontal')
        plt.title(config.getTitle(variable) + args['formattedDate'], fontsize=8)
        plt.clim(*config.getColorBounds(variable))
        ax = plt.gca()
        box = TextArea(getCopyright(), textprops=dict(color='k', fontsize=6))
        copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor= (-0.1, -0.15), frameon=False, bbox_transform=ax.transAxes)
#       copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor= (0,0,1,1), frameon=False, bbox_transform=plt.gcf().transFigure)
        ax.add_artist(copyrightBox)

#        cbar = plt.colorbar(format=config.getValueFormat(variable), extend='both', shrink=0.5)
        cbar = plt.colorbar(format=config.getValueFormat(variable), extend='both')

        cbar.set_label(config.getUnit(variable), rotation='horizontal', fontsize=6)

        l,b,w,h = plt.gca().get_position().bounds
        ll,bb,ww,hh = cbar.ax.get_position().bounds
        cbar.ax.set_position([ll,  b+0.25*h, ww, h*0.5])

        colorbarLabels = config.getColorbarLabels(variable)
        if len(colorbarLabels) != 0:
            cbar.ax.set_yticklabels(colorbarLabels)

        for tick in cbar.ax.get_yticklabels():
            tick.set_fontsize(6)

        contourPlt = plt.contour(lons,(-1*dep), data, levels=config.getContourLevels(variable), colors='k')
        plt.clabel(contourPlt, inline=True, fmt='%3.1f', fontsize=6)
        plt.savefig(self.serverConfig["outputDir"] + outputFile + '.png', dpi=150, bbox_inches='tight', pad_inches=0.8, bbox_extra_artists=[copyrightBox])
        plt.close()

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
        intv_colours = clrs

    cmap = mpl.colors.ListedColormap(intv_colours)
    if min_colour is not None:
        cmap.set_under(min_colour)
    if max_colour is not None:
        cmap.set_over(max_colour)
    return cmap
