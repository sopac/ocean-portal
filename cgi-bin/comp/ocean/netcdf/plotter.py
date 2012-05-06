#!/user/bin/python

"""
Plotter is the base class for plotting.

Author: Sheng Guo
(c)Climate and Oceans Support Program for the Pacific(COSPPAC), Bureau of Meteorology, Australia
"""

from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt


class Plotter:
    """The base class for plotting netCDF files."""

    _DEFAULT_PROJ = "cyl" #Equidistant Cylindrical Projection
    
    output_directory = "/data/comp/raster/"

    def __init__(self):
        """The simple constructor of Plotter"""


#    def plot(inputFile, outputFile, projection=__DEFAULT_PROJ):
        """Plot the input file using the specified projection and save thei
        plot to the output file.
        """

    def plot(self, data, lats, lons, variable, config, outputFile, proj=_DEFAULT_PROJ):
        """Plot the input data using the specified project and save the            plot to the output file.
        """ 
        #*******************************************
        #* Generate image for the thumbnail and download
        #*******************************************
        m = Basemap(projection=proj, llcrnrlat=-26, llcrnrlon=134,\
                    urcrnrlat=23, urcrnrlon=214, resolution='l')
        m.pcolormesh(x, y, data, shading='flat', cmap=config.getColorMap(variable))
        m.drawcoastlines(linewidth=0.1)
        m.fillcontinents(color='#F1EBB7')
        plt.title(config.getTitle(variable), fontsize=8)
        plt.clim(*config.getColorBounds(variable))
        cax = plt.axes([0.93, 0.18, 0.02, 0.65])
        cbar = plt.colorbar(format=config.getValueFormat(variable), cax=cax, extend='both')

        plt.savefig(self.output_directory + 'thumbnail.png', dpi=150, bbox_inches='tight', pad_inches=.3)  


        plt.close()



    def plotBasemap(self, data, lats, lons, variable, config, outputFile, proj=_DEFAULT_PROJ):
        """Plot the input data using the specified project and save the            plot to the output file.
        """ 
        #left part
        m = Basemap(projection=proj, llcrnrlat=-90, llcrnrlon=180,\
                   urcrnrlat=90, urcrnrlon=360, resolution=None)
        x, y = m(*np.meshgrid(lons, lats))

        #Plot the data
        m.pcolormesh(x, y, data, shading='flat', cmap=config.getColorMap(variable))
        plt.clim(*config.getColorBounds(variable))
        
        #Do not draw the black border around the map by setting the linewidth to 0
        m.drawmapboundary(linewidth=0.0)

        #Save the figure with no white padding around the map.
        plt.savefig(self.output_directory + 'left.png', edgecolor='r', dpi=150, bbox_inches='tight', pad_inches=0) 
        plt.clf()
 
        #right part
        m = Basemap(projection=proj, llcrnrlat=-90, llcrnrlon=0,\
                   urcrnrlat=90, urcrnrlon=180, resolution=None)

        #Plot the data
        m.pcolormesh(x, y, data, shading='flat', cmap=config.getColorMap(variable))
        plt.clim(*config.getColorBounds(variable))
        
        #Do not draw the black border around the map by setting the linewidth to 0
        m.drawmapboundary(linewidth=0.0)

        #Save the figure with no white padding around the map.
        plt.savefig(self.output_directory + 'right.png', edgecolor='r', dpi=150, bbox_inches='tight', pad_inches=0) 
        plt.close()
