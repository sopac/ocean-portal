#!/usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib.patches as pa

def heightpack(wavg):
    '''Plots a 4 entry custom legend on the current axis.

       Argument:
       wavg - mean significant wave height, used to calculate rogue wave height. (float)
       '''
    #calculate rogue wave height
    rwh = round(2*wavg,2)
    #plot line on axes at rogue wave height
    #plt.axvline(rwh, color='m', lw='3')
    #basic legend using matplotlib artists
    #p0 = pa.Rectangle((0, 0), 1, 1, fc = (0,0,0), alpha = 0.5)
    p1 = pa.Rectangle((0, 0), 1, 1, fc = "b", alpha = 0.5)
    p2 = pa.Rectangle((0, 0), 1, 1, fc = "g", alpha = 0.5)
    p3 = pa.Rectangle((0, 0), 1, 1, fc = "r", alpha = 0.5)
    #plot legend on figure, not axes
    plt.figlegend((p3,p2,p1),('Lower Quartile','Interquartile Range','Upper Quartile'),loc='upper left', bbox_to_anchor = (0.785,0.765),prop={'size':10})
    return

def timepack():
    '''Plots a 3 entry custom legend on the current axis.'''
    #basic legend using matplotlib artists
    p1 = pa.Rectangle((0, 0), 1, 1, fc = "b", alpha = 0.5)
    p2 = pa.Rectangle((0, 0), 1, 1, fc = "g", alpha = 0.5)
    p3 = pa.Rectangle((0, 0), 1, 1, fc = "r", alpha = 0.5)
    #plot legend on figure, not axes.
    plt.figlegend((p3,p2,p1),('Lower Quartile','Interquartile Range','Upper Quartile'),loc='upper left', bbox_to_anchor = (0.785,0.765), prop={'size':10})
    return

def rosepack():
    '''Plots a decile based custom legend on the current axis.'''
    p6 = pa.Rectangle((0, 0), 1, 1, fc = (0.8,0,0.8), alpha = 0.5)
    p5 = pa.Rectangle((0, 0), 1, 1, fc = (0,0.5,1), alpha = 0.5)
    p4 = pa.Rectangle((0, 0), 1, 1, fc = (0,1,0), alpha = 0.5)
    p3 = pa.Rectangle((0, 0), 1, 1, fc = (1,1,0), alpha = 0.5)
    p2 = pa.Rectangle((0, 0), 1, 1, fc = (1,0.5,0), alpha = 0.5)
    p1 = pa.Rectangle((0, 0), 1, 1, fc = "r", alpha = 0.5)

    plt.figlegend((p6,p5,p4,p3,p2,p1),('> 0.50','0.40-0.50','0.30-0.40','0.20-0.30','0.10-0.20', '< 0.10'),loc='upper left', bbox_to_anchor = (0.755,0.805),prop={'size':10})
