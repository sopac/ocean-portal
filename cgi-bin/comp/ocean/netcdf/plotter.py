#!/user/bin/python

"""
Plotter is the base class for plotting.

Author: Sheng Guo
(c)Climate and Oceans Support Program for the Pacific(COSPPAC), Bureau of Meteorology, Australia
"""

from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
import os
import shutil
from ..util import serverConfig
from matplotlib.transforms import offset_copy


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
                    urcrnrlat=urlat, urcrnrlon=urlon, resolution='l')
        x, y = m(*np.meshgrid(lons, lats))
	if contourLines:
	    m.contour(x, y, data, levels=config.getContourLevels(variable), colors='k', linewidths=0.4)
        m.contourf(x, y, data, levels=config.getContourLevels(variable), shading='flat', cmap=config.getColorMap(variable))
	m.drawcoastlines(linewidth=0.1, zorder=6)
        m.fillcontinents(color='#F1EBB7', zorder=7)
        plt.title(config.getTitle(variable), fontsize=8)
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

        plt.savefig(self.serverConfig["outputDir"] + outputFile + '.png', dpi=150, bbox_inches='tight', pad_inches=.3)
        plt.close()

    def contourBasemapWest(self, data, lats, lons, variable, config, outputFile,\
                           lllat=-90, lllon=180, urlat=90, urlon=360, proj=_DEFAULT_PROJ,\
                           contourLines=False,  worldfile='ocean/resource/west.pgw'):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """ 
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
                        contourLines=False,  worldfile='ocean/resource/east.pgw'):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """ 
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


    def plot(self, data, lats, lons, variable, config, outputFile, lllat, lllon, urlat, urlon, proj=_DEFAULT_PROJ, centerLabel = False):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """ 
        #*******************************************
        #* Generate image for the thumbnail and download
        #*******************************************
        m = Basemap(projection=proj, llcrnrlat=lllat, llcrnrlon=lllon,\
                    urcrnrlat=urlat, urcrnrlon=urlon, resolution='l')
        x, y = m(*np.meshgrid(lons, lats))
        m.pcolormesh(x, y, data, shading='flat', cmap=config.getColorMap(variable))
        m.drawcoastlines(linewidth=0.1)
        m.fillcontinents(color='#F1EBB7')
        plt.title(config.getTitle(variable), fontsize=8)
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

        plt.savefig(self.serverConfig["outputDir"] + outputFile + '.png', dpi=150, bbox_inches='tight', pad_inches=.3)  
        plt.close()



    def plotBasemapWest(self, data, lats, lons, variable, config, outputFile,\
                        lllat=-90, lllon=180, urlat=90, urlon=360, proj=_DEFAULT_PROJ, worldfile='ocean/resource/west.pgw'):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """ 
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
                        lllat=-90, lllon=0, urlat=90, urlon=180, proj=_DEFAULT_PROJ, worldfile='ocean/resource/east.pgw'):
        """
        Plot the input data using the specified project and save the plot to the output file.
        """ 
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


