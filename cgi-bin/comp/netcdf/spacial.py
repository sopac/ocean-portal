#!/usr/bin/python
#
# AUSTRALIAN BUREAU OF METEOROLOGY
# NATIONAL CLIMATE CENTRE
# SECTION: CLIMATE DATA SERVICES - OCEAN CLIMATE
#
# SCRIPT: spacial.py
# LANGUAGE: python
# AUTHOR: Luke Garde & Sheng Guo
# LOCATION: /data/sst/reynolds/bin
# 
# PURPOSE: Spacial plotter of 2-D gridded data from a NetCDF files
####################################################################

# Import Python modules
import os
import sys,getopt
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import datetime
import daterange

from mpl_toolkits.basemap import Basemap, shiftgrid, cm 
from netCDF4 import Dataset as NetCDFFile 
from pylab import *

verbose='1'
currentDate=datetime.datetime.now()
strCurrentYear = str(currentDate.year)

# Set variables based on commandline arguements
alloptions, otherargs= getopt.getopt(sys.argv[1:],'d:p:r:t:')
print '\n'
print currentDate
for theopt,thearg in alloptions:
    print theopt,thearg
    if theopt=='-d':
        date=thearg
    elif theopt=='-p':
        period=thearg
    elif theopt=='-r':
        region=thearg
    elif theopt=='-t':
        type=thearg
    else: 
        print "ERROR: Please check input parameters", theopt, thearg
        sys.exit()
        
year = date[0:4]
month = date[4:6]
day = date[6:8]
monthmap = {'01':'January', '02':'February', \
            '03': 'March', '04': 'April', \
            '05': 'May', '06': 'June', \
            '07': 'July', '08': 'August', \
            '09': 'September', '10': 'October', \
            '11': 'November', '12': 'December'}
cmonth = monthmap[month]
if cmonth==None:
    print "ERROR with month int to str conversion"


if period=='daily':
    path = '/data/sst/reynolds/daily/' + year + '/'
    fname = 'avhrr-only-v2.' + date
elif period=='predaily':
    path = '/data/sst/reynolds/daily/' + year + '/'
    fname = 'avhrr-only-v2.' + date + '_preliminary'
elif period=='weekly':
    path = '/data/sst/reynolds/weekly/'
    fname = 'avhrr-only-v2.' + date + 'ave'
    startDate, endDate = daterange.generateWeekly(date)
elif period=='monthly':
    path = '/data/sst/reynolds/monthly/' + year + '/'
    fname = 'avhrr-only-v2.' + year + month + 'ave' 
elif period=='3monthly':
    path = '/data/sst/reynolds/3monthly/'
    fname = 'avhrr-only-v2.' + year + month + 'ave'
    startDate = daterange.generate3Month(date)
elif period=='6monthly':
    path = '/data/sst/reynolds/6monthly/'
    fname = 'avhrr-only-v2.' + year + month + 'ave'
    startDate = daterange.generate6Month(date)
elif period=='yearly':
    path = '/data/sst/reynolds/yearly/'
    fname = 'avhrr-only-v2.' + year + 'ave'
else:
    print "ERROR in setting period"


out_path = '/data/sst/reynolds/images/'
copyrightText = ur'\u00A9' + "  Bureau of Meteorology " + strCurrentYear
climText = "Climatology: 1971 - 2000 OI.V2 SST"

# Set up the projections based on the regions
if region=='sh':
    proj='spstere'
elif region=='aus':
    proj='lam'
else:
    proj='cyl'

startlon=0

print path + fname + '.nc'
try: 
    ncfile = NetCDFFile(path + fname + '.nc', 'r')
except RuntimeError:
    print path + fname + "not exist"
    sys.exit(-1) 
allattr=dir(ncfile)

if verbose=='2':
    print "\n\nDIMENSIONS:"
    for name in ncfile.dimensions.keys():
        print "\nDIMENSION:",
        try:
            print name, ncfile.variables[name][:]
        except:
	    print name, ncfile.dimensions[name]
        try:
	    print '   ',ncfile.variables[name].units
        except:
	    pass
        try:
	    print '   ',ncfile.variables[name].gridtype
        except:
	    pass

    print "\n'*****************'\nVARIABLES:"
    for name in ncfile.variables.keys():
        if name in ncfile.dimensions.keys(): continue
        print "\nVARIABLE:",
        print name, ncfile.variables[name].dimensions,
        try:
	    print '   ',ncfile.variables[name].units
        except:
	    pass
        try:
            print "   missing value=",ncfile.variables[name].missing_value
        except:
	    pass

    print "\n********************"

# Set x and y dimension
xvar='lon'
lon1d=ncfile.variables[xvar][:]
yvar='lat'
lat1d=ncfile.variables[yvar][:]

# Set variable and corresponding title
if type == 'mean':
    thevar='sst'
    if period=='daily':
        thetitle='Daily Reynolds Sea Surface Temperature:   ' + day + ' ' + cmonth + ' ' + year
    elif period=='predaily':
        thetitle='Daily Reynolds Sea Surface Temperature:   ' + day + ' ' + cmonth + ' ' + year + '(preliminary)'
    elif period=='weekly':
        thetitle='Weekly Average Reynolds Sea Surface Temperature:   ' + startDate.strftime("%d %B %Y") + ' to ' + endDate.strftime("%d %B %Y")
    elif period=='monthly':
        thetitle='Monthly Average Reynolds Sea Surface Temperature:   ' + cmonth + ' ' + year
    elif period=='3monthly':
        thetitle='Three Month Average Reynolds Sea Surface Temperature:   ' + startDate.strftime("%B %Y") + ' to ' + cmonth + ' ' + year
    elif period=='6monthly':
        thetitle='Six Month Average Reynolds Sea Surface Temperature:   ' + startDate.strftime("%B %Y") + ' to ' + cmonth + ' ' + year
    elif period=='yearly':
        thetitle='Yearly Average Reynolds Sea Surface Temperature:   ' + year
elif type == 'anom':
    thevar='anom'
    if period=='daily':
        thetitle='Daily Reynolds Sea Surface Temperature Anomaly:   ' + day + ' ' + cmonth + ' ' + year
    elif period=='predaily':
        thetitle='Daily Reynolds Sea Surface Temperature Anomaly:   ' + day + ' ' + cmonth + ' ' + year + '(preliminary)'
    elif period=='weekly':
        thetitle='Weekly Average Reynolds Sea Surface Temperature Anomaly:   ' + startDate.strftime("%d %B %Y") + ' to ' + endDate.strftime("%d %B %Y")
    elif period=='monthly':
        thetitle='Monthly Average Reynolds Sea Surface Temperature Anomaly:   ' + cmonth + ' ' + year
    elif period=='3monthly':
        thetitle='Three Month Average Reynolds Sea Surface Temperature Anomaly:   ' + startDate.strftime("%B %Y") + ' to ' + cmonth + ' ' + year
    elif period=='6monthly':
        thetitle='Six Month Average Reynolds Sea Surface Temperature Anomaly:   ' + startDate.strftime("%B %Y") + ' to ' + cmonth + ' ' + year
    elif period=='yearly':
        thetitle='Yearly Average Reynolds Sea Surface Temperature Anomaly:   ' + year
elif type == 'error':
    thevar='err'
    if period=='daily':
        thetitle='Daily Reynolds Sea Surface Temperature Error:   ' + day + ' ' + cmonth + ' ' + year
    elif period=='predaily':
        thetitle='Daily Reynolds Sea Surface Temperature Error:   ' + day + ' ' + cmonth + ' ' + year + '(preliminary)'
    elif period=='weekly':
        thetitle='Weekly Average Reynolds Sea Surface Temperature Error:   ' + startDate.strftime("%d %B %Y") + ' to ' + endDate.strftime("%d %B %Y")
    elif period=='monthly':
        thetitle='Monthly Reynolds Sea Surface Temperature Error:   ' + cmonth + ' ' + year
    elif period=='3monthly':
        thetitle='Three Month Average Reynolds Sea Surface Temperature Error:   ' + startDate.strftime("%B %Y") + ' to ' + cmonth + ' ' + year
    elif period=='6monthly':
        thetitle='Six Month Average Reynolds Sea Surface Temperature Error:   ' + startDate.strftime("%B %Y") + ' to ' + cmonth + ' ' + year
    elif period=='yearly':
        thetitle='Yearly Reynolds Sea Surface Temperature Error:   ' + year
elif type == 'ice':
    thevar='ice'
    if period=='daily':
        thetitle='Daily Reynolds Sea Ice Concentration:   ' + day + ' ' + cmonth + ' ' + year
    elif period=='predaily':
        thetitle='Daily Reynolds Sea Ice Concentration:   ' + day + ' ' + cmonth + ' ' + year + '(preliminary)'
    elif period=='weekly':
        thetitle='Weekly Average Reynolds Sea Ice Concentration:   ' + startDate.strftime("%d %B %Y") + ' to ' + endDate.strftime("%d %B %Y")
    elif period=='monthly':
        thetitle='Monthly Reynolds Sea Ice Concentration:   ' + cmonth + ' ' + year
    elif period=='3monthly':
        thetitle='Three Month Average Reynolds Sea Ice Concentration:   ' + startDate.strftime("%B %Y") + ' to ' + cmonth + ' ' + year
    elif period=='6monthly':
        thetitle='Six Month Average Reynolds Sea Ice Concentration:   ' + startDate.strftime("%B %Y") + ' to ' + cmonth + ' ' + year
    elif period=='yearly':
        thetitle='Yearly Reynolds Sea Ice Concentration:   ' + year
else:
    print "ERROR: Please check the input type parameter:", type
    sys.exit()


data=ncfile.variables[thevar]
dataa=data[:]
theshape=dataa.shape

## Sets the record
therec = 0
therec=int(therec)
extratext=" rec=%d" %therec

slice=dataa[therec,:,:]
mval=data._FillValue
maskdat=ma.masked_values(slice,mval)
datamax=max(maskdat.compressed().flat)
datamin=min(maskdat.compressed().flat)

delon = lon1d[1]-lon1d[0]
delat = lat1d[1]-lat1d[0]
lons = zeros(len(lon1d)+1,'d')
lats = zeros(len(lat1d)+1,'d')
lons[0:len(lon1d)] = lon1d-0.5*delon
lons[-1] = lon1d[-1]+0.5*delon
lats[0:len(lat1d)] = lat1d-0.5*delon
lats[-1] = lat1d[-1]+0.5*delon
lons, lats = meshgrid(lon1d, lat1d)


# Setup the colormaps
colordict=cm.RdBu._segmentdata.copy()
for k in colordict.keys():
        colordict[k]=[list(q) for q in colordict[k]]
        for a in colordict[k]:
                a[0]=1.-a[0]
        colordict[k].reverse()
BuRd =  cm.colors.LinearSegmentedColormap("BuRd",  colordict)

print "\nPlotting, please wait......."


## Plotting

if region=='aus':
    #Lambert Conformal
    m = Basemap(llcrnrlon=60,llcrnrlat=-50.,urcrnrlon=170,urcrnrlat=20,\
    resolution='i',area_thresh=100.,projection='lcc',\
    lat_1=-35.,lon_0=135.,lat_0=-15)    
    xtxt=100000. #offset for text
    ytxt=100000.
    parallels = arange(-90.,90,20.)
    meridians = arange(10.,360.,20.)
elif region=='glob': 
    #cylindrical is default
    m = Basemap(llcrnrlon=startlon,llcrnrlat=-90,urcrnrlon=startlon+360.,urcrnrlat=90.,\
    resolution='l',area_thresh=1000.,projection='cyl')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,90.,30.)
    if startlon==-180:
        meridians = arange(-180.,180.,30.)
    else:
        meridians = arange(0.,360.,30.)
elif region=='pac':
    startlon=100.
    m = Basemap(llcrnrlon=startlon,llcrnrlat=-45,urcrnrlon=startlon+200.,urcrnrlat=45.,\
    resolution='i',area_thresh=100.,projection='cyl')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,90.,30.)
    if startlon==-180:
        meridians = arange(-180.,180.,30.)
    else:
        meridians = arange(0.,360.,30.)
elif region=='ind':
    startlon=20.
    m = Basemap(llcrnrlon=startlon,llcrnrlat=-45,urcrnrlon=startlon+140.,urcrnrlat=45.,\
    resolution='i',area_thresh=100.,projection='cyl')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,90.,30.)
    if startlon==-180:
        meridians = arange(-180.,180.,30.)
    else:
        meridians = arange(0.,360.,30.)
elif region=='ntr':
    startlon=94.
    m = Basemap(llcrnrlon=startlon,llcrnrlat=-22,urcrnrlon=startlon+80.,urcrnrlat=0.,\
    resolution='i',area_thresh=100.,projection='cyl')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,90.,10.)
    if startlon==-180:
        meridians = arange(-180.,180.,10.)
    else:
        meridians = arange(0.,360.,10.)
elif region=='sth':
    startlon=94.
    m = Basemap(llcrnrlon=startlon,llcrnrlat=-50,urcrnrlon=startlon+80.,urcrnrlat=-30.,\
    resolution='i',area_thresh=100.,projection='cyl')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,90.,10.)
    if startlon==-180:
        meridians = arange(-180.,180.,10.)
    else:
        meridians = arange(0.,360.,10.)
elif region=='tas':
    startlon=150.
    m = Basemap(llcrnrlon=startlon,llcrnrlat=-46,urcrnrlon=startlon+24.,urcrnrlat=-26.,\
    resolution='h',area_thresh=10.,projection='cyl')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,90.,10.)
    if startlon==-180:
        meridians = arange(-180.,180.,10.)
    else:
        meridians = arange(0.,360.,10.)
elif region=='cor':
    startlon=142.
    m = Basemap(llcrnrlon=startlon,llcrnrlat=-26,urcrnrlon=startlon+32.,urcrnrlat=-4.,\
    resolution='h',area_thresh=10.,projection='cyl')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,90.,10.)
    if startlon==-180:
        meridians = arange(-180.,180.,10.)
    else:
        meridians = arange(0.,360.,10.)
elif region=='nws':
    startlon=94.
    m = Basemap(llcrnrlon=startlon,llcrnrlat=-22,urcrnrlon=startlon+36.,urcrnrlat=-4.,\
    resolution='h',area_thresh=10.,projection='cyl')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,90.,10.)
    if startlon==-180:
        meridians = arange(-180.,180.,10.)
    else:
        meridians = arange(0.,360.,10.)
elif region=='swr':
    startlon=94.
    m = Basemap(llcrnrlon=startlon,llcrnrlat=-46,urcrnrlon=startlon+22.,urcrnrlat=-22.,\
    resolution='h',area_thresh=10.,projection='cyl')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,90.,10.)
    if startlon==-180:
        meridians = arange(-180.,180.,10.)
    else:
        meridians = arange(0.,360.,10.)
elif region=='eca':
    startlon=140.
    m = Basemap(llcrnrlon=startlon,llcrnrlat=-50,urcrnrlon=startlon+40.,urcrnrlat=0.,\
    resolution='h',area_thresh=10.,projection='cyl')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,90.,10.)
    if startlon==-180:
        meridians = arange(-180.,180.,10.)
    else:
        meridians = arange(0.,360.,10.)
elif region=='wca':
    startlon=90.
    m = Basemap(llcrnrlon=startlon,llcrnrlat=-50,urcrnrlon=startlon+40.,urcrnrlat=0.,\
    resolution='h',area_thresh=10.,projection='cyl')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,90.,10.)
    if startlon==-180:
        meridians = arange(-180.,180.,10.)
    else:
        meridians = arange(0.,360.,10.)
elif region=='sh': 
    m = Basemap(boundinglat=-10,lon_0=0,resolution='l',area_thresh=1000.,projection='spstere')
    xtxt=1.
    ytxt=0.
    parallels = arange(-90.,10,30.)
    if startlon==-180:
        meridians = arange(-180.,180.,30.)
    else:
        meridians = arange(0.,360.,30.)  


xsize = rcParams['figure.figsize'][0]
fig=figure(figsize=(xsize,m.aspect*xsize))
ax = fig.add_axes([0.05,0.08,0.85,0.85],axisbg='white')
x, y = m(lons, lats)

if type=='mean':
    colorbounds=[-2,34]
    mycolormap=cm.jet
    units=ur'\u00b0' + 'C'        
elif type=='anom':
    colorbounds=[-2,2]
    mycolormap=BuRd
    units=ur'\u00b0' + 'C'
elif type=='error':
    colorbounds=[-2,2]
    mycolormap=cm.spectral
    units=ur'\u00b0' + 'C'
elif type=='ice':
    colorbounds=[0,1]
    mycolormap=cm.Blues
#    mycolormap=cm.gist_gray
    units='% (x100)'
else:
    print "ERROR: Check colourbar settings"
    sys.exit()

# Set the contours (create the mesh)
data = data[0][0][:,:]
CS1 = m.pcolormesh(x,y,data,cmap=mycolormap)


cbar=None
clim(*colorbounds)
cax = axes([0.93, 0.11, 0.02, 0.79]) # setup colorbar axes

# Draw colourbar
if type=='mean':
    cbar=colorbar(format='%d', cax=cax, extend='both')
elif type=='anom':
    cbar=colorbar(format='%5.1f', cax=cax, ticks=[-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3], extend='both')
elif type=='error':
    cbar=colorbar(format='%5.1f', cax=cax, ticks=[-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2], extend='both')
elif type=='ice':
    cbar=colorbar(format='%5.1f', cax=cax, ticks=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1], extend='both')
else:
    print "ERROR: Check colourbar draw settings"
    sys.exit()

for tick in cbar.ax.get_yticklabels():
    tick.set_fontsize(7)

axes(ax)

# Set the contour lines
#clevs = [26]
#CS1 = m.contour(x,y,data,clevs,colours='k',linewidth=0.2)


 

m.drawcoastlines(linewidth=0.5)
m.fillcontinents(color='#cccccc')
#m.drawcountries()

if region=='aus':
    m.drawstates()

# draw parallels and meridians.
# label on left, right and bottom of map.
m.drawparallels(parallels,labels=[1,0,0,0],linewidth=0.5,fontsize=7)
m.drawmeridians(meridians,labels=[0,0,0,1],linewidth=0.5,fontsize=7)

if not thetitle:
	title(thevar+extratext)
else:
	title(thetitle, fontsize=8)


dailypid='AAA12345'
weeklypid='FFF12345'
monthlypid='BBB12345'
monthly3pid='DDD12345'
monthly6pid='EEE12345'
yearlypid='CCC12345'
	
if region=='aus':
    plt.annotate('%s' % copyrightText, xy=(0,-390), xycoords='axes points', fontsize=7)
    if type=='anom':
        plt.annotate('%s' % climText, xy=(0,-400), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(400,-390), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,6)
elif region=='sh':
    plt.annotate('%s' % copyrightText, xy=(0,-390), xycoords='axes points', fontsize=7)
    if type=='anom':
        plt.annotate('%s' % climText, xy=(0,-400), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(400,-390), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,6)
elif region=='glob':
    plt.annotate('%s' % copyrightText, xy=(0,-236), xycoords='axes points', fontsize=7)
    if type=='anom':
        plt.annotate('%s' % climText, xy=(0,-246), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(435,-236), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,4)
elif region=='pac':
    plt.annotate('%s' % copyrightText, xy=(0,-225), xycoords='axes points', fontsize=7)
    if type=='anom':
        plt.annotate('%s' % climText, xy=(0,-235), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(438,-225), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,4)
elif region=='ind':
    plt.annotate('%s' % copyrightText, xy=(0,-300), xycoords='axes points', fontsize=7)
    if type=='anom':
        plt.annotate('%s' % climText, xy=(0,-310), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(450,-300), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,5)
elif region=='ntr':
    plt.annotate('%s' % copyrightText, xy=(0,-146), xycoords='axes points', fontsize=7)
    if type=='anom':
        plt.annotate('%s' % climText, xy=(0,-156), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(400,-146), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,5)
elif region=='sth':
    plt.annotate('%s' % copyrightText, xy=(0,-146), xycoords='axes points', fontsize=7)
    if type=='anom':
        plt.annotate('%s' % climText, xy=(0,-156), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(400,-146), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,5)
elif region=='tas':
    plt.annotate('%s' % copyrightText, xy=(0,-380), xycoords='axes points', fontsize=7)
    if type=='anom':
        plt.annotate('%s' % climText, xy=(0,-390), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(400,-380), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,6)
elif region=='cor':
    plt.annotate('%s' % copyrightText, xy=(0,-330), xycoords='axes points', fontsize=7)
    if type=='anom':
        plt.annotate('%s' % climText, xy=(0,-340), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(400,-330), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,6)
elif region=='nws':
    plt.annotate('%s' % copyrightText, xy=(0,-236), xycoords='axes points', fontsize=7)
    if type=='anom':
        plt.annotate('%s' % climText, xy=(0,-246), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(400,-236), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,5)
elif region=='swr':
    plt.annotate('%s' % copyrightText, xy=(0,-386), xycoords='axes points', fontsize=7)
    if type=='anom':
       plt.annotate('%s' % climText, xy=(0,-396), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(400,-386), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,6)
elif region=='eca':
    plt.annotate('%s' % copyrightText, xy=(0,-389), xycoords='axes points', fontsize=7)
    if type=="anom":
        plt.annotate('%s' % climText, xy=(0,-399), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(375,-389), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,6)
elif region=='wca':
    plt.annotate('%s' % copyrightText, xy=(0,-389), xycoords='axes points', fontsize=7)
    if type=='anom':
        plt.annotate('%s' % climText, xy=(0,-399), xycoords='axes points', fontsize=7)
    plt.annotate("Units:" + units, xy=(375,-389), xycoords='axes points', fontsize=7)
    fig.set_size_inches(7,6)
     


if period=='daily' or period=='predaily':
    savefig(out_path + dailypid + '_' + type + '_' + region + '_' + date + '.png', \
            dpi=120, facecolor='w', edgecolor='w', orientation='landscape')
elif period=='weekly':
    savefig(out_path + weeklypid + '_' + type + '_' + region + '_' + year + month + day + 'ave.png', \
            dpi=120, facecolor='w', edgecolor='w', orientation='landscape')
elif period=='monthly':
    savefig(out_path + monthlypid + '_' + type + '_' + region + '_' + year + month + 'ave.png', \
            dpi=120, facecolor='w', edgecolor='w', orientation='landscape')
elif period=='3monthly':
    savefig(out_path + monthly3pid + '_' + type + '_' + region + '_' + year + month + 'ave.png', \
            dpi=120, facecolor='w', edgecolor='w', orientation='landscape')
elif period=='6monthly':
    savefig(out_path + monthly6pid + '_' + type + '_' + region + '_' + year + month + 'ave.png', \
            dpi=120, facecolor='w', edgecolor='w', orientation='landscape')
elif period=='yearly':
    savefig(out_path + yearlypid + '_' + type + '_' + region + '_' + year + 'ave.png', \
            dpi=120, facecolor='w', edgecolor='w', orientation='landscape')    
