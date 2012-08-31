#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox, TextArea
import datetime
import math
import glob
from netCDF4 import Dataset
import json
import os.path

import ocean.util as util
from ..util import productName
from ..util import regionConfig

serverCfg = util.get_server_config()

ersstProduct = productName.products["ersst"]

regionCfg = regionConfig.regions

CACHE_DIR = os.path.join(serverCfg['outputDir'],
                         serverCfg['cacheDir']['ersst'])

currentDate = datetime.datetime.today()
strCurrentYear = str(currentDate.year)

copyright = ur'\u00A9' + "Commonwealth of Australia " + strCurrentYear\
            + ", Australian Bureau of Meteorology, COSPPac Project"
unit = ur'\u00b0' + 'C'

now = datetime.datetime.now()
currentYear = int(now.year)

def nans(shape,dtype=float):
    a = np.zeros(shape,dtype)
    a.fill(np.nan)
    return a

months = {'01':'January',
          '02':'Feburay',
          '03':'March',
          '04':'April',
          '05':'May',
          '06':'June',
          '07':'July',
          '08':'August',
          '09':'September',
          '10':'October',
          '11':'November',
          '12':'December'}

def generateMonthlyAverages():
    
    for month in months:
        meanFileName = CACHE_DIR \
                          + ersstProduct['monthlyAve']\
                          + '_' + month + '_mean.json'
        meanFile = open(meanFileName, 'w')
        monthlyAreaMean = {}

        for region in regionCfg:
            averageFileName = CACHE_DIR \
                            + ersstProduct['monthlyAve']\
                            + '_' +  month + '_ave_%s' % (region)

            averageFile = open(averageFileName + '.txt', 'w')

            files = glob.glob(serverCfg["dataDir"]["ersst"]\
                    + "monthly/ersst.[12][0-9][0-9][0-9]"\
                    + month + ".nc")
            files = sorted(files)

            date = []
            areaAve = []
            for index, file in enumerate(files):
                nc = Dataset(file, 'r')
                if index == 0:
                    lats = nc.variables['lat'][:]
                    lons = nc.variables['lon'][:]

                    latBottom = regionConfig.regions[region][1]["llcrnrlat"]
                    latTop = regionConfig.regions[region][1]["urcrnrlat"]
                    lonLeft =  regionConfig.regions[region][1]["llcrnrlon"]
                    lonRight = regionConfig.regions[region][1]["urcrnrlon"]

                    latmin = lats >= latBottom
                    latmax = lats <= latTop
                    lonmin = lons >= lonLeft
                    lonmax = lons <= lonRight

                    latrange = latmin & latmax
                    lonrange = lonmin & lonmax

                sst = nc.variables['sst'][0][0]
                xrange = sst[latrange]
                grid = xrange[:, lonrange]
                date.append(int(file[-12:-8]))
                areaAve.append(np.ma.average(grid))
                nc.close()

            mean = np.average(areaAve)
            anom = areaAve - mean

            monthlyAreaMean[region] = mean
            averageFile.write('Year/%s\tAverage\tAnomaly\n' % month)
            for dateCol, areaAveCol, anomCol in zip(date, areaAve, anom):
                averageFile.write('%4d\t% .2f\t% .2f\n' % (dateCol, areaAveCol, anomCol))
            averageFile.close()
 
            #Plot sst anomaly
            meanStr = str(round(mean,2))
            fig = plt.figure(figsize=(10, 4))
            ax = plt.gca()
            ax.axhline(y=0, color='k')
            plt.xticks(fontsize=9)
            plt.yticks(fontsize=9)

            ntime = len(date)
            pcol = list(range(ntime))

            for i in range(ntime):
                pcol[i]=('red')
                if anom[i] < 0:
                    pcol[i]=('blue')

            plt.grid(True)
            width = 1/1.5
            plt.bar(date, anom, width, color=pcol, align='center')

            box = TextArea(copyright, textprops=dict(color='k', fontsize=6))
            copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor= (-0.1, -0.2), frameon=False, bbox_transform=ax.transAxes)
            ax.add_artist(copyrightBox)
            box = TextArea('Average (1981-2010): ' + meanStr + unit, textprops=dict(color='k', fontsize=6))
            anchoredBox = AnchoredOffsetbox(loc=4, child=box, bbox_to_anchor= (1., -0.2),frameon=False, bbox_transform=ax.transAxes)
            ax.add_artist(anchoredBox)

            plt.title(months[month] + ' Sea Surface Temperature Anomaly - ' +  regionCfg[region][2], fontsize=12)
            plt.xlabel('Year', fontsize=10)
            plt.ylabel('Sea Surface Temperature Anomaly (' + ur'\u00b0'  + 'C)', fontsize=10)
            plt.xlim([1980,currentYear + 1])
            plt.savefig(averageFileName + '.png',\
                       dpi=150, bbox_inches='tight', pad_inches=.2,\
                        bbox_extra_artists=[copyrightBox, anchoredBox])
            plt.close()
 
            #plot trend line
            fig = plt.figure(figsize=(10, 4))
            ax = plt.gca()
            ax.axhline(y=0, color='k')
            plt.xticks(fontsize=9)
            plt.yticks(fontsize=9)
            plt.grid(True)
            width = 1/1.5
            plt.bar(date, anom, width, color=pcol, align='center')

            index = np.arange(0,len(date))
            (apoly,bpoly) = np.polyfit(index,anom,1)
            trendline = apoly * np.array(index) + bpoly
            plt.plot(date, trendline, color='k', lw=2)
            linearTrend = str(round(apoly * 10,2))

            box = TextArea(copyright, textprops=dict(color='k', fontsize=6))
            copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor= (-0.1, -0.2), frameon=False, bbox_transform=ax.transAxes)
            ax.add_artist(copyrightBox)
            box = TextArea('Linear Trend: ' + linearTrend + unit + '/decade', textprops=dict(color='k', fontsize=6))
            trendBox = AnchoredOffsetbox(loc=8, child=box, bbox_to_anchor= (0.5, -0.2), frameon=False, bbox_transform=ax.transAxes)
            ax.add_artist(trendBox)
            box = TextArea('Average (1981-2010): ' + meanStr + unit, textprops=dict(color='k', fontsize=6))
            averageBox = AnchoredOffsetbox(loc=4, child=box, bbox_to_anchor= (1., -.2),frameon=False, bbox_transform=ax.transAxes)
            ax.add_artist(averageBox)

            plt.title(months[month] + ' Sea Surface Temperature Anomaly - ' +  regionCfg[region][2], fontsize=12)
            plt.xlabel('Year', fontsize=10)
            plt.ylabel('Sea Surface Temperature Anomaly (' + ur'\u00b0'  + 'C)', fontsize=10)
            plt.xlim([1980,currentYear + 1])
            plt.savefig(averageFileName + '_trend.png',\
                       dpi=150, bbox_inches='tight', pad_inches=.2,\
                        bbox_extra_artists=[copyrightBox, anchoredBox, trendBox])
            plt.close()

            #plot running averages with the interval from 2 to 16
            for interval in range(2, 16):
                fig = plt.figure(figsize=(10, 4))
                ax = plt.gca()
                ax.axhline(y=0, color='k')
                plt.xticks(fontsize=9)
                plt.yticks(fontsize=9)
                plt.grid(True)
                width = 1/1.5
                plt.bar(date, anom, width, color=pcol, align='center')

                runningAve=nans(len(anom))
                runningMean=map(np.average, zip(*[iter(anom[x:]) for x in range(interval)]))
                runningMean=np.array(runningMean)
                insertPoint = math.floor((interval - 1) / 2.0)
                runningAve[insertPoint:insertPoint + len(runningMean)]= runningMean
                plt.plot(date, runningAve, color='k', lw=2)
    
                box = TextArea(copyright, textprops=dict(color='k', fontsize=6))
                copyrightBox = AnchoredOffsetbox(loc=3, child=box, bbox_to_anchor= (-0.1, -0.2),\
                                             frameon=False, bbox_transform=ax.transAxes)
                ax.add_artist(copyrightBox)
                box = TextArea('%d-year running averages shown by black curve' % interval, textprops=dict(color='k', fontsize=6))
                runningBox = AnchoredOffsetbox(loc=8, child=box, bbox_to_anchor= (0.6, -0.2),\
                                           frameon=False, bbox_transform=ax.transAxes)
                ax.add_artist(runningBox)
                box = TextArea('Average (1981-2010): ' + meanStr + unit, textprops=dict(color='k', fontsize=6))
                averageBox = AnchoredOffsetbox(loc=4, child=box, bbox_to_anchor= (1., -.2),\
                                           frameon=False, bbox_transform=ax.transAxes)
                ax.add_artist(averageBox)

                plt.title(months[month] + ' Sea Surface Temperature Anomaly - ' + regionCfg[region][2], fontsize=12)
                plt.xlabel('Year', fontsize=10)
                plt.ylabel('Sea Surface Temperature Anomaly (' + ur'\u00b0'  + 'C)', fontsize=10)
                plt.xlim([1980,currentYear + 1])
                plt.savefig(averageFileName + '_%02drunning' % (interval) + '.png', dpi=150,\
                          bbox_inches='tight', pad_inches=.2, bbox_extra_artists=[copyrightBox,\
                          averageBox, runningBox])
                plt.close()
        json.dump(monthlyAreaMean, meanFile, sort_keys=True, indent=4)
        meanFile.flush()
        meanFile.close()
