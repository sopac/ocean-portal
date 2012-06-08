#!/usr/bin/env python

import numpy as np

def meanbearing(wdir):
    '''Returns the mean true bearing of an array of true bearings.

       Arguments:
       wdir -- An array of angles between 0 and 360. (NumPy Array)

       Returns:
       bearing --  Mean bearing of the angles contained in array wdir. (float)
       '''
    #initialize x,y,wavedir
    x,y = 0, 0
    wavedir = wdir  
    for i in range(len(wavedir)):
       #convert to radians
       wavedir[i] = np.pi*(wavedir[i]/180.0)
       #disagreegate angles into x,y components
       y  = y + np.sin(wavedir[i])
       x  = x + np.cos(wavedir[i])
    
    #calculate the mean vector
    meany = y/len(wavedir)
    meanx = x/len(wavedir)
    #calculate mean bearing by taking the inverse tangent of y/x
    bearing = np.arctan2(meany,meanx)
    
    #arctan2 returns range -pi,pi rather than 0,2pi, so conversion is required if < 0.
    if bearing < 0:
        bearing = bearing + 2*np.pi

    return bearing
