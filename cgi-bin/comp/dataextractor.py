#!/usr/bin/python


from netCDF4 import Dataset
import numpy as np

def extract(filename, latTop, latBottom, lonLeft, lonRight):
    nc = Dataset(filename, 'r')
    lats = nc.variables['lat'][:]
    lons = nc.variables['lon'][:]
        
    latmin = lats >= latBottom
    latmax = lats <= latTop
    lonmin = lons >= lonLeft
    lonmax = lons <= lonRight

    latrange = latmin & latmax
    lonrange = lonmin & lonmax
   
        #extract values
    sst = nc.variables['sst'][0][0]
#    xrange = sst[latrange]
#    grid = xrange[:, lonrange] 
    grid = sst 
    
    nc.close()
    return grid
