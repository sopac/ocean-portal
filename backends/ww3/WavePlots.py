#!/usr/bin/env python

import scipy as sci
import scipy.stats
import numpy as np
import datetime
import matplotlib.cm as cm
from matplotlib.pyplot import figure, show, rc
import matplotlib.pyplot as plt
import matplotlib.patches as pa
import legend_pack as lpack
from numpy import arange
from numpy import linspace
from numpy.random import random
import histcolor as hc
import landerror as le
from radbearing import meanbearing
import angleconv as conv
from formatter import NESWformat
from ocean.netcdf.plotter import getCopyright

def RosePlot(opath, wdir, units, lat, lon, ilat, ilon, xstr, title, var, binwd):

    '''Plots a windrose of angular values in wdir, with annotations

       Arguments:
       wdir -- an array of angles in the range (0,360). (NumPy Array)
       units -- measurements units for wdir variable. (float)
       lat -- latitude of point. (float)
       lon -- longitude of point. (float)
       xstr -- x-axis label. (string)
       title -- plot title. (string)
       var -- the variable that is measured by wdir. (string)
       binwd -- width of histogram bins. (float)

       Returns:
       rosefig -- An annotated windrose of wdir values.
       '''

    #set number of bins and max bin value.
    N,wdnbin,wdmax = 8,8,2*np.pi
    degree = ur'\u00b0'
    if wdir[0] == -999.0:
       raise le.LandError("Error")
    #flip directions as WWIII direction are given in meteorological convention.
    if var == "Dm":
        wdir = conv.dirflip(wdir)
        wdir = conv.dirshift(wdir)
    else:
        wdir = conv.dirshift(wdir)
    #make a basic histogram of wave directions over the range (-22.5,337.5).
    whist = np.histogram(wdir, wdnbin, (-22.5,337.5), density=False)
    #calculate mean bearing
    meanb = meanbearing(wdir)
    #force square figure and square axes looks better for polar
    rosefig = figure(figsize=(10,7.5))
    ax = rosefig.add_axes([0.075, 0.1, 0.6, 0.725], polar=True)
    #plot radial gridlines at seperations of 45 degrees
    plt.thetagrids((0,45,90,135,180,225,270,315),('N', '45' + degree, 'E', '135' + degree, 'S', '215' + degree, 'W', '315' + degree),frac = 1.1)
    #rotate axis to zero at North and set direction of increasing angle clockwise.
    plt.rgrids((0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9), angle=0)
    plt.ylim(0.0,1.0)
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location('N')
    #lines, labels = plt.rgrids()
    #set Nmax
    Nmax = 1
    #initialize prob and perc arrays
    prob = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    perc = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    #variable to normalize bins so that they sum to 1 (probability)
    normalizer = 1/float(len(wdir))
    #normalize histogram to calculate probabilities and percentages
    for i in range(0,N):
	prob[i] = float(whist[0][i])*normalizer
        perc[i] = round(100*prob[i],2)

    units = '%'
    theta = np.linspace(-2*np.pi/(2*N), 2*np.pi-2*np.pi/(2*N), N, endpoint=False)
    #some basic settings for graphics
    width = 2*np.pi/N
    length = np.size(wdir)
    #rounded mean bearing for labelling purposes
    meanbr = round((meanb*180)/(np.pi),1)
    #set up bar chart properties
    bars = ax.bar(theta, prob, width, bottom=0.0)
    my_cmap = hc.decile_rose()
    #plot a line to indicate mean bearing
    ax.arrow(0, 0, meanb, 1.0, edgecolor = 'r', facecolor = 'r', lw='3')
    #plot bar chart of histogram in theta space
    for r,bar in zip(prob, bars):
        bar.set_facecolor(my_cmap(r))
        bar.set_alpha(0.5)
    lpack.rosepack()
    formilat,formilon =  NESWformat(ilat,ilon)
    formlat,formlon = NESWformat(lat,lon)
    #title of figure
    plt.figtext(0.12,0.92,'%s' % title, fontsize=16, weight=800)
    #various annotations to plot
    plt.figtext(0.76, 0.82,'Probabilities:', fontsize = 10, weight = 550)
    plt.figtext(0.76, 0.575,'Location & Plot Data:', fontsize=10, weight = 550)

    plt.figtext(0.76, 0.51, 'Input Lat/Lon:\n %s %s' % (formilat,formilon), fontsize=10)
    plt.figtext(0.76, 0.46, 'Grid Lat/Lon:\n %s %s' % (formlat, formlon), fontsize=10)

    plt.figtext(0.76, 0.425, 'Data points: %s' % length, fontsize=10)
    plt.figtext(0.76, 0.4, 'Bins: %s' % int(N), fontsize=10)
    plt.figtext(0.76, 0.375, 'Bin Width: %s %s' % (binwd, degree), fontsize=10)

    plt.figtext(0.76, 0.275, 'Mean True Bearing: %s %s' % (meanbr, degree), color='r', fontsize=10)
    #display wave direction percentages for 8 primary compass points in the windrose
    plt.figtext(0.76, 0.325, 'Directional Statistics:', fontsize=10, weight=550)
    plt.figtext(0.76, 0.25, 'North: %s %s' % (perc[0], units), fontsize=10)
    plt.figtext(0.76, 0.225, 'North East: %s %s' % (perc[1], units), fontsize=10)
    plt.figtext(0.76, 0.2, 'East: %s %s' % (perc[2], units), fontsize=10)
    plt.figtext(0.76, 0.175, 'South East: %s %s' % (perc[3], units), fontsize=10)
    plt.figtext(0.76, 0.15, 'South: %s %s' % (perc[4], units), fontsize=10)
    plt.figtext(0.76, 0.125, 'South West: %s %s' % (perc[5], units), fontsize=10)
    plt.figtext(0.76, 0.1, 'West: %s %s' % (perc[6], units), fontsize=10)
    plt.figtext(0.76, 0.075, 'North West: %s %s' % (perc[7], units), fontsize=10)
    #Bureau of Meteorology Copyright
    plt.figtext(0.58, 0.03, u'WAVEWATCH III$^{\u00AE}$', fontsize=10)
    plt.figtext(0.02, 0.02, getCopyright(), fontsize=8)
    #define image name
    imgname = opath + '.png'
     #write image file
    plt.savefig(imgname)

    return

def HistPlot(opath, wheight, units, lat, lon, ilat, ilon, xstr, title, var, binwd):
    '''Returns a normalized, annotated histogram for values of wheight

       Arguments:
       wheight -- an array of positive doubles. (NumPy Array)
       units -- units associated with wheight. (string)
       lat -- latitude of the point. (float)
       lon -- longitude of the point. (float)
       xstr -- x-axis label. (string)
       title -- title of the plot. (string)
       var -- variable associated with the values in wheight. (string)
       binwd -- width of histogram bins. (float)

       Returns:
       histfig -- An annotated histogram of wheight values.
       '''
    #calculate the values of some pertinent statistical quantities
    wavg = np.average(wheight)
    wavgr = round(wavg,2)
    maxwave = round(np.max(wheight),2)
    minwave = round(np.min(wheight),2)
    imaxwave = int(np.max(wheight))+ 1
    Nmax = imaxwave
    length = np.size(wheight)
    debug = False
    #calculate range of data
    #binthresh = maxwave - minwave
    #Error message if selected coordinates are out of range or on land
    if maxwave == -999.0:
       raise le.LandError("Error")
    #alter bin width depending on range of data
    #if binthresh < 10:
     #  binwd = 0.1
    #elif binthresh > 10:
      # binwd = 0.2
    #else:
      # print "Error"
    #bins per unit and total number of bins
    binperunit = 1/binwd
    binnum = Nmax*binperunit
    initial = round(0.001,3)
    final = round(Nmax+0.001,3)

    #histogram of selected variable
    whist,wbins = np.histogram(wheight,Nmax*binperunit,(initial,final),density=True)
    #print wbins
    #calculate max and mins of histogram
    maxy = np.max(whist*binwd)
    maxx = np.max(wheight)
    minx = np.min(wheight)
    #do some basic statistics on histogram, std. deviation and quartiles.
    q1 = round(sci.stats.scoreatpercentile(wheight,25),1)
    q3 = round(sci.stats.scoreatpercentile(wheight,75),1)
    x=linspace(0,maxx+0.5,Nmax*binperunit)
    #set up figure
    histfig=plt.figure(figsize = (10,7.5))
    histax=histfig.add_axes([0.1,0.1,0.675,0.75])
    plt.xlim(0,maxx+0.5)
    plt.ylim(0,maxy+0.01)
    whistnorm = whist*binwd
    #np.hist(wheight,100,(0,Nmax),color='b',normed=True, histtype = 'stepfille)
    #set up bar chart properties
    bars=plt.bar(wbins[:-1],whistnorm,binwd,0)
    if debug == True:

        FILE = open('/home/jsmith/Test/verification/WW3' + '_' + str(lat) + '_' + str(lon) + '_' + var + '_array.txt', "w")
        FILE.writelines(list( "%s \n" % i for i in whist))
        FILE.close()

    my_cmap = hc.quartile_colors(wheight,wavg,Nmax,binwd)

    #bar chart of histogram
    for r,bar in zip(wbins[:-1], bars):
        bar.set_facecolor(my_cmap(r/Nmax))
        bar.set_alpha(0.5)

    #specify plot properties and plot guassian kde and average line
    plt.xlim(minx-0.5,maxx+0.5)
    plt.ylim(0,maxy+0.01)
    #histax.plot(x, approximate_pdf(x), color = 'black', linewidth=3, alpha=1)
    histax.axvline(wavg, color='r', lw='3')

    #choose which legend to display based on variable
    if var == 'Hs':
        lpack.heightpack(wavg)
    #plt.figtext(0.79,0.175, 'Rogue Wave Height: %s %s' % (2*wavgr,units), fontsize = 10, color = 'm')
    elif var == 'Tm':
        lpack.timepack()
    formilat, formilon = NESWformat(ilat,ilon)
    formlat, formlon = NESWformat(lat,lon)
    #specify graph grid properties
    xticks = [10,20,30,40,50,60,70,80,90,100]
    plt.xticks = xticks, [('%s' % str(x/10))]
    plt.grid(True)
    #x,y axis labels and title
    plt.xlabel('%s (%s)' % (xstr,units), fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.figtext(0.10,0.90,'%s' % title, fontsize=16, weight = 800)
    #various annotations for graphics
    plt.figtext(0.79, 0.8, 'Distribution:', fontsize=10, weight=550)
    plt.figtext(0.79, 0.625, 'Location & Plot Data:',fontsize = 10, weight = 550)
    plt.figtext(0.79, 0.56, 'Input Lat/Lon:\n %s %s' % (formilat,formilon), fontsize=10)
    plt.figtext(0.79, 0.51, 'Grid Lat/Lon:\n %s %s' % (formlat,formlon), fontsize=10)

    plt.figtext(0.79, 0.475, 'Data points: %s' % length ,fontsize=10)
    plt.figtext(0.79, 0.45, 'Bins: %s'  % int(binnum), fontsize=10)
    plt.figtext(0.79, 0.425, 'Bin Width: %s %s' % (binwd,units), fontsize=10)
    plt.figtext(0.79, 0.375, 'Statistical Information:', fontsize=10, weight=550)

    plt.figtext(0.79, 0.275, 'Mean: %s %s' % (round(wavgr,1), units), color='r', fontsize=10)
    plt.figtext(0.79, 0.325, 'Max: %s %s' % (round(maxwave,1), units), fontsize=10)
    plt.figtext(0.79, 0.225, 'Min: %s %s' % (round(minwave,1), units), fontsize=10)

    plt.figtext(0.79, 0.25,'25th Percentile: %s %s' % (round(q1,1),units), fontsize=10)
    plt.figtext(0.79, 0.3,'75th Percentile: %s %s' % (round(q3,1),units), fontsize=10)
    #Bureau of Meteorology Copyright
    plt.figtext(0.68, 0.03, u'WAVEWATCH III$^{\u00AE}$', fontsize=10)
    plt.figtext(0.02, 0.02, getCopyright(), fontsize=8)
     #define image name
    imgname = opath + '.png'
     #write image file
    plt.savefig(imgname)

    return
