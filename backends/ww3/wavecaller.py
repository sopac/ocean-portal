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

def wavecaller(opath, var, gridLat, gridLon, pointValues, mthStr):
    #convert lat,lon to floats
    lat = float(gridLat)
    lon = float(gridLon)
    #convert lat,lon to consistant format
    latstr,lonstr = nameformat(lat,lon)
    #make a numpy array for extracted data for calculations
    extdata = np.array(pointValues)
    #determine which plot module to call based on variable input
    if var == 'Dm':
        title = mthStr + ' ' + 'mean daily wave direction (1979-2009)'
        units = 'degrees'
        xstr = 'Wave direction'
        binwd = 45
        RosePlot(opath, extdata,units,gridLat,gridLon,xstr,title,var,binwd)

    elif var == 'Hs':
        title = mthStr + ' ' + 'mean daily significant wave height (1979-2009)'
    	units = 'm'
    	xstr = 'Significant wave height'
    	binwd = 0.1
    	HistPlot(opath, extdata,units,gridLat,gridLon,xstr,title,var,binwd)

    elif var == 'Tm':
    	title = mthStr + ' ' + 'mean daily peak wave period (1979-2009)'
    	units = 's'
    	xstr = 'Peak wave period'
    	binwd = 0.1
    	HistPlot(opath, extdata,units, gridLat, gridLon, xstr, title, var, binwd)

