#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Matthew Howie

import os
import sys,getopt
import numpy as np
from pylab import *
import warnings


'''
Variables:
data is the array to be smoothed
xlen and ylen are the length of each axis in data
size is the size of the window i.e size by size-must be odd
'''

  


def smooth(data, size):

    shape = data.shape
#    print shape
    xlen = shape[0]
    ylen = shape[1]
#    print xlen
#    print ylen

    
    half = (size-1)/2
    gridpoint = ([1])

    x, y = np.mgrid[-half:half+1, -half:half+1]
    w = np.exp(-(x**2/float(half) + y**2/float(half)))
    weights = w / w.sum()
#    print weights
#    print weights.sum()

    if size % 2==0:
        print "\nEven window size chosen-choose odd size\n"
    else:
        window = zeros( (size,size) )
        dataNew = data[:]
        for i in range(half+1,xlen-half):
            for j in range(half+1,ylen-half):
                window = data[i-half-1:i+half,j-half-1:j+half]
                count = np.ma.count_masked(window)
                if count < size**2:
                    gridpoint = data[i, j]
            countgrid = np.ma.count_masked(gridpoint)
            if countgrid ==1:
                        dataNew[i,j] = ma.average(window, weights=weights)
        return dataNew
 
