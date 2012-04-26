#!/usr/bin/python


import netcdf.plotter as plotter
import dataextractor

from netCDF4 import Dataset
import numpy as np


class ReynoldsPlotter ():
    """ Reynolds plotter is specifically designed to plot the reynolds
    netcdf data
    """
    def __init__(self):
       """Does nothing""" 


    def plot(self):
        dataset = Dataset('/home/sguo/data/avhrr-only-v2.20120116.nc')
        sst = dataset.variables['sst'][0][0]
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
        plot.plot(sst, lats, lons, 'aaa.png')
        dataset.close()

if __name__ == "__main__":
    plt = ReynoldsPlotter()
    plt.plot()


