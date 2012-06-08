#!/usr/bin/env python

import os
import sys, getopt
import re
import matplotlib.mlab as mlab
import scipy as sci
import numpy as np
import time
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, show, rc
from numpy import arange
from WavePlots import HistPlot
from WavePlots import RosePlot
from formatter import nameformat

def wavecaller(opath, productId, gridLat, gridLon, pointValues):
    
    #convert lat,lon to floats
    lat = float(gridLat)
    lon = float(gridLon)
    #convert lat,lon to consistant format
    latstr,lonstr = nameformat(lat,lon)
    #set output path and label for product
    opath = "/data/wavewatch3/extracted_data/"
    #make a numpy array for extracted data for calculations
    extdata = np.array(pointValues)
    #determine which plot module to call based on variable input
    if var == 'Dm':
        title = 'Windrose of wave direction probability'
        units = 'degrees'
        xstr = 'Mean wave direction'
        binwd = 45
        RosePlot(extdata,units,gridLat,gridLon,xstr,title,var,binwd)

    elif var == 'Hs':
        title = 'Histogram of significant wave height'
    	units = 'm'
    	xstr = 'Significant wave height'
    	binwd = 0.1
    	HistPlot(extdata,units,gridLat,gridLon,xstr,title,var,binwd)

    elif var == 'Tm':
    	title = 'Histogram of peak wave period'
    	units = 's'
    	xstr = 'Peak wave period'
    	binwd = 0.2
    	HistPlot(extdata,units,gridLat,gridLon,xstr,title,var,binwd)

        #define image name
	imgname = opath + productId + '_' + latstr + '_' + lonstr + '_' + var + '_graph.png'
        #write image file
        plt.savefig(imgname)
   
