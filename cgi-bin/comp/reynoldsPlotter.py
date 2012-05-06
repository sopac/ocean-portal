#!/usr/bin/python


import netcdf.plotter as plotter
import dataextractor

from netCDF4 import Dataset
import numpy as np
import reynoldsConfig as rc

class ReynoldsPlotter ():
    """ Reynolds plotter is specifically designed to plot the reynolds
    netcdf data
    """
    config = None

    def __init__(self):
       """Does nothing""" 
       self.config = rc.ReynoldsConfig()

    def plot(self, filename, variable, date):
        dataset = Dataset(filename)
        sst = dataset.variables[self.config.getVariableType(variable)][0][0]
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['lon'][:]
        
        delon = lons[1]-lons[0]; delat = lats[1]-lats[0]
        lons = (lons - 0.5*delon).tolist()
        lons.append(lons[-1]+delon)
        lons = np.array(lons,np.float64)
        lats = (lats - 0.5*delat).tolist()
        lats.append(lats[-1]+delat)
        lats = np.array(lats,np.float64)


        
#        data = dataextractor.extract('/home/sguo/data/avhrr-only-v2.20120116.nc', 23, -26, 134, 214)
        plot = plotter.Plotter()
        plot.plot(sst, lats, lons, variable, self.config, 'aaa.png')
        dataset.close()

if __name__ == "__main__":
    plt = ReynoldsPlotter()
    plt.plot('/data/sst/reynolds/monthly/2012/avhrr-only-v2.201201ave.nc', 'anom', '20120101')


