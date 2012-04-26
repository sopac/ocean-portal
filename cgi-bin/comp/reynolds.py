#!/usr/bin/python
#This cgi script is to generate tidal gauge pages

import os
import os.path
from Cheetah.Template import Template
import re
import cgi
import cgitb
import sys
import StringIO
import subprocess
import time
import areaMean
import reynoldsPlotter

#Configurations
dailyProductId = "AAA12345"
monthlyProductId = "BBB12345"
yearlyProductId = "CCC12345"
monthly3ProductId = "DDD12345"
monthly6ProductId = "EEE12345"
weeklyProductId = "FFF12345"

yearlyAveProductId = "GGG12345"
monthlyAveProductId = "HHH12345"

decileMonthlyProductId = "DEC12345"

baseUrl = "http://tuscany.bom.gov.au/dev"
outputDir = "data/sst/reynolds/images"
#seaLevelDir = "data/sea_level/"
sstDir = baseUrl + "/data/sst/reynolds"
sstGraph = "%s_%s_%s_%s.png"
aveSstGraph = "%s_%s_%s_%save.png"
decGraph = "%s_%s_%sdec.png"

def process(form): 
    outputHTML = ""
    if "map" in form and "date" in form and "period" in form:
        mapStr = form["map"].value
        dateStr = form["date"].value
        areaStr = form["area"].value
        periodStr = form["period"].value
    
        if mapStr == 'anom' and form["average"].value == "true":
            dateStr = dateStr[4:6]
            outputHTML += '{"aveImg":'
            if form["trend"].value == "true":
                if periodStr == 'monthly':
                    outputHTML +=  '"%s/images/averages/%s_%s_ave_%s_trend.png"' % (sstDir, monthlyAveProductId, dateStr, areaStr)
                    outputHTML += ', "aveData":'
                    outputHTML += '"%s/images/averages/%s_%s_ave_%s.txt"' % (sstDir, monthlyAveProductId, dateStr, areaStr)
                    outputHTML += ', "mean":'
                    outputHTML += str(areaMean.monthlyMean[dateStr][areaStr])
                elif periodStr == 'yearly':
                    outputHTML += '"%s/images/averages/%s_ave_%s_trend.png"' % (sstDir, yearlyAveProductId, areaStr)
                    outputHTML += ', "aveData":'
                    outputHTML += '"%s/images/averages/%s_ave_%s.txt"' % (sstDir, yearlyAveProductId, areaStr)
                    outputHTML += ', "mean":'
                    outputHTML += str(areaMean.yearlyMean[areaStr])
            elif form["runningAve"].value == "true":
                if periodStr == 'monthly':
                    outputHTML += '"%s/images/averages/%s_%s_ave_%s_%02dmoving.png"' % (sstDir, monthlyAveProductId, dateStr, areaStr, int(form["runningInterval"].value))
                    outputHTML += ', "aveData":'
                    outputHTML += '"%s/images/averages/%s_%s_ave_%s.txt"' % (sstDir, monthlyAveProductId, dateStr, areaStr)
                    outputHTML += ', "mean":'
                    outputHTML += str(areaMean.monthlyMean[dateStr][areaStr])
                elif periodStr == 'yearly':
                    outputHTML += '"%s/images/averages/%s_ave_%s_%02dmoving.png"' % (sstDir, yearlyAveProductId, areaStr, int(form["runningInterval"].value))
                    outputHTML += ', "aveData":'
                    outputHTML += '"%s/images/averages/%s_ave_%s.txt"' % (sstDir, yearlyAveProductId, areaStr)
                    outputHTML += ', "mean":'
                    outputHTML += str(areaMean.yearlyMean[areaStr])
            else:
                if periodStr == 'monthly':
                    outputHTML += '"%s/images/averages/%s_%s_ave_%s.png"' % (sstDir, monthlyAveProductId, dateStr, areaStr)
                    outputHTML += ', "aveData":'
                    outputHTML += '"%s/images/averages/%s_%s_ave_%s.txt"' % (sstDir, monthlyAveProductId, dateStr, areaStr)
                    outputHTML += ', "mean":'
                    outputHTML += str(areaMean.monthlyMean[dateStr][areaStr])
                elif periodStr == 'yearly':
                    outputHTML += '"%s/images/averages/%s_ave_%s.png"' % (sstDir, yearlyAveProductId, areaStr)
                    outputHTML += ', "aveData":'
                    outputHTML += '"%s/images/averages/%s_ave_%s.txt"' % (sstDir, yearlyAveProductId, areaStr)
                    outputHTML += ', "mean":'
                    outputHTML += str(areaMean.yearlyMean[areaStr])
            outputHTML += '}'
        elif mapStr == "dec":
            fileName = decGraph % (decileMonthlyProductId, areaStr, dateStr[:6])
            outputFileName = outputDir + "/" + fileName
            if not os.path.exists(outputFileName):
                outputHTML += '{"error":"Requested image is not available at this time."}'
            else:
                outputHTML += '{"img":'
                outputHTML += '"%s/images/%s"' % (sstDir, fileName)
                outputHTML += '}'
        else:
        ####current xml html response
            if periodStr == 'daily':
                fileName = sstGraph % (dailyProductId, mapStr, areaStr, dateStr)
            elif periodStr == 'monthly':
                fileName = aveSstGraph % (monthlyProductId, mapStr, areaStr, dateStr[:6])
            elif periodStr == 'yearly':
                fileName = aveSstGraph % (yearlyProductId, mapStr, areaStr, dateStr[:4])
            elif periodStr == '3monthly':
                fileName = aveSstGraph % (monthly3ProductId, mapStr, areaStr, dateStr[:6])
            elif periodStr == '6monthly':
                fileName = aveSstGraph % (monthly6ProductId, mapStr, areaStr, dateStr[:6])
            elif periodStr == 'weekly':
                fileName = aveSstGraph % (weeklyProductId, mapStr, areaStr, dateStr)
            outputFileName = outputDir + "/" + fileName
            if not os.path.exists(outputFileName):
                subprocess.call(['/data/sst/reynolds/bin/spacial.py', '-d', dateStr, '-r', areaStr, '-t', mapStr, '-p', periodStr], stdout=subprocess.PIPE)
            if not os.path.exists(outputFileName):
                outputHTML += '{"error":"Requested image is not available at this time."}'
            else:
                outputHTML += '{"img":'
                outputHTML += '"%s/images/%s"' % (sstDir, fileName)
                outputHTML += '}'

    else:
        outputHTML += "{}" 

    return outputHTML
