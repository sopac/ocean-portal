#!/user/bin/python

"""
Plotter is the base class for plotting.

Author: Sheng Guo
(c)Climate and Oceans Support Program for the Pacific(COSPPAC), Bureau of Meteorology, Australia
"""

import os, os.path
import bisect
import math
import shutil
import datetime

import numpy as np

from mpl_toolkits.basemap import Basemap
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea
from matplotlib.transforms import offset_copy
import matplotlib.pyplot as plt

import ocean
from ..util import serverConfig

class Plotter:
    """The base class for plotting netCDF files."""

    _DEFAULT_PROJ = "cyl" #Equidistant Cylindrical Projection
    serverConfig = None

    def __init__(self):
        """The simple constructor of Plotter"""
        self.serverConfig = serverConfig.servers[serverConfig.currentServer]

#    def plot(inputFile, outputFile, projection=__DEFAULT_PROJ):
        """
        Plot the input file using the specified projection and save the
        plot to the output file.
        """
    def contour(self, data, lats, lons, variable, config, outputFile,\
                title, lllat, lllon, urlat, urlon, proj=_DEFAULT_PROJ,\
                contourLines = False, centerLabel = False):
	"""
	Plot the input data with contours using the specified project and save the plot to the output file.
	"""
	#*******************************************
        #* Generate image for the thumbnail and download
        #*******************************************
	m = Basemap(projection=proj, llcrnrlat=lllat, llcrnrlon=lllon,\
                    urcrnrlat=urlat, urcrnrlon=urlon, resolution='h')
        x, y = m(*np.meshgrid(lons, lats))
	if contourLines:
	    m.contour(x, y, data, levels=config.getContourLevels(variable), colors='k', linewidths=0.4)

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

        if math.fabs(lllat - urlat) < 5:
            parallels = np.linspace(lllat, urlat, 4)
        else:
            parallels = np.linspace(lllat, urlat, 9)
        m.drawparallels(parallels, labels=[True, False, False, False], fmt='%.2f', fontsize=8, dashes=[3, 3], color='gray')
        if math.fabs(lllon - urlon) < 5:
            meridians = np.linspace(lllon, urlon, 4)
        else:
            meridians = np.linspace(lllon, urlon, 9)
        m.drawmeridians(meridians, labels=[False, False, False, True], fmt='%.2f', fontsize=8, dashes=[3, 3], color='gray')

        plt.title(config.getTitle(variable), fontsize=10)
        plt.clim(*config.getColorBounds(variable))
        cax = plt.axes([0.93, 0.18, 0.02, 0.65])
        cbar = plt.colorbar(format=config.getValueFormat(variable), cax=cax, extend='both')
	colorbarLabels = config.getColorbarLabels(variable)
	if len(colorbarLabels) != 0:
            cbar.ax.set_yticklabels(colorbarLabels)

        if centerLabel:
            try:
                for tick in cbar.ax.get_yticklabels():
                    tick.set_fontsize(6)
                    tick.set_transform(offset_copy(cax.transData, x=10, y=-40, units='dots'))
            except KeyError:
                pass

        plt.savefig(self.serverConfig["outputDir"] + outputFile + '.png', dpi=150, bbox_inches='tight', pad_inches=1.)
        plt.close()

    def contourBasemapWest(self, data, lats, lons, variable, config, outputFile,\
                           lllat=-90, lllon=180, urlat=90, urlon=360, proj=_DEFAULT_PROJ,\
                           contourLines=False,  worldfile=None):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """

        if not worldfile:
            worldfile = os.path.join(ocean.__path__[0], 'resource', 'west.pgw')

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
                        lllat=-90, lllon=0, urlat=90, urlon=180, proj=_DEFAULT_PROJ,\
                        contourLines=False,  worldfile=None):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """

        if not worldfile:
            worldfile = os.path.join(ocean.__path__[0], 'resource', 'east.pgw')

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


    def plot(self, data, lats, lons, variable, config, outputFile, lllat, lllon, urlat, urlon, proj=_DEFAULT_PROJ, centerLabel = False, **args):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """
        #*******************************************
        #* Generate image for the thumbnail and download
        #*******************************************
        m = Basemap(projection=proj, llcrnrlat=lllat, llcrnrlon=lllon,\
                    urcrnrlat=urlat, urcrnrlon=urlon, resolution='h')
        x, y = m(*np.meshgrid(lons, lats))
        m.pcolormesh(x, y, data, shading='flat', cmap=config.getColorMap(variable))
        m.drawcoastlines(linewidth=0.1, zorder=6)
#        m.fillcontinents(color='#F1EBB7', zorder=7)
        m.fillcontinents(color='#cccccc', zorder=7)

        if math.fabs(lllat - urlat) < 5:
            parallels = np.linspace(lllat, urlat, 4)
        else:
            parallels = np.linspace(lllat, urlat, 9)
        m.drawparallels(parallels, labels=[True, False, False, False], fmt='%.2f', fontsize=6, dashes=[3, 3], color='gray')
        if math.fabs(lllon - urlon) < 5:
            meridians = np.linspace(lllon, urlon, 4)
        else:
            meridians = np.linspace(lllon, urlon, 9)
        m.drawmeridians(meridians, labels=[False, False, False, True], fmt='%.2f', fontsize=6, dashes=[3, 3], color='gray')


        plt.title(config.getTitle(variable) + args['formattedDate'], fontsize=8)
        plt.clim(*config.getColorBounds(variable))
        ax = plt.gca()
        box = TextArea(self.getCopyright(), textprops=dict(color='k', fontsize=6))
        copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor= (-0.1, -0.15), frameon=False, bbox_transform=ax.transAxes)
        ax.add_artist(copyrightBox)

#        cax = plt.axes([0.93, 0.18, 0.02, 0.65])
#        cbar = plt.colorbar(format=config.getValueFormat(variable), cax=cax, extend='both')
#        cbar = plt.colorbar(format=config.getValueFormat(variable), cax=cax, extend='both')
        cbar = plt.colorbar(format=config.getValueFormat(variable), extend='both')
        cbar.set_label(config.getUnit(variable), rotation='horizontal', fontsize=6)
#        cbar.set_label(ax.get_window_extent(), rotation='horizontal')

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


        plt.savefig(self.serverConfig["outputDir"] + outputFile + '.png', dpi=150, bbox_inches='tight', pad_inches=0.8, bbox_extra_artists=[copyrightBox])
        plt.close()

    def plotBasemapWest(self, data, lats, lons, variable, config, outputFile,\
                        lllat=-90, lllon=180, urlat=90, urlon=360,
                        proj=_DEFAULT_PROJ, worldfile=None):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """

        if not worldfile:
            worldfile = os.path.join(ocean.__path__[0], 'resource', 'west.pgw')

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
                        lllat=-90, lllon=0, urlat=90, urlon=180,
                        proj=_DEFAULT_PROJ, worldfile=None):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """

        if not worldfile:
            worldfile = os.path.join(ocean.__path__[0], 'resource', 'east.pgw')

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
        box = TextArea(self.getCopyright(), textprops=dict(color='k', fontsize=6))
        copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor= (-0.1, -0.15), frameon=False, bbox_transform=ax.transAxes)
        ax.add_artist(copyrightBox)

        cbar = plt.colorbar(format=config.getValueFormat(variable), extend='both')
        cbar.set_label(config.getUnit(variable), rotation='horizontal', fontsize=6)

        colorbarLabels = config.getColorbarLabels(variable)
        if len(colorbarLabels) != 0:
            cbar.ax.set_yticklabels(colorbarLabels)

        for tick in cbar.ax.get_yticklabels():
            tick.set_fontsize(6)

        contourPlt = plt.contour(lons,(-1*dep), data, levels=config.getContourLevels(variable), colors='k')
        plt.clabel(contourPlt, inline=True, fmt='%3.0f', fontsize=8)
        plt.savefig(self.serverConfig["outputDir"] + outputFile + '.png', dpi=150, bbox_inches='tight', pad_inches=0.8, bbox_extra_artists=[copyrightBox])
        plt.close()

    def getCopyright(self):
        return ur'\u00A9' + "Commonwealth of Australia "\
               + datetime.date.today().strftime('%Y')\
               + "\nAustralian Bureau of Meteorology, COSPPac COMP"


