import os
import os.path
import sys
import json

import ersstPlotter
from ..util import areaMean
from ..util import productName
from ..util import serverConfig

#Maybe move these into configuration later
sstGraph = "%s_%s_%s_%s"
decGraph = "%s_%s_%s_%sdec"
trendGraph = "%s_%s_%s_%s2011lin"

#get the server dependant path configurations
serverCfg = serverConfig.servers[serverConfig.currentServer]

#get dataset dependant production information
ersstProduct = productName.products["ersst"]

#get the plotter
plotter = ersstPlotter.ErsstPlotter()

def process(form): 
    responseObj = {} #this object will be encoded into a json string
    if "map" in form and "date" in form and "period" in form and "area" in form and "baseyear" in form:
        mapStr = form["map"].value
        dateStr = form["date"].value
        areaStr = form["area"].value
        periodStr = form["period"].value
	baseStr = form["baseyear"].value

	**args = {"variable": mapStr,
		  "date": dateStr,
		  "area": areaStr,
		  "period": periodStr,
		  "baseYear": baseStr
		 }
    
        if mapStr == 'anom':
            if "average" in form and form["average"].value == "true":
                dateStr = dateStr[4:6] #extract month value
                if form["trend"].value == "true":
                    if periodStr == 'monthly':
                        responseObj["aveImg"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["monthlyAve"]\
                                              + "_%s_ave_%s_trend.png" % (dateStr, areaStr)
                        responseObj["aveData"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["monthlyAve"]\
                                              + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                        responseObj["mean"] = str(areaMean.monthlyMean[dateStr][areaStr])
		    elif periodStr == '3monthly':
                        responseObj["aveImg"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["3monthlyAve"]\
                                              + "_%s_ave_%s_trend.png" % (dateStr, areaStr)
                        responseObj["aveData"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["3monthlyAve"]\
                                              + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                        responseObj["mean"] = str(areaMean.3monthlyMean[dateStr][areaStr])
		    elif periodStr == '6monthly':
                        responseObj["aveImg"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["6monthlyAve"]\
                                              + "_%s_ave_%s_trend.png" % (dateStr, areaStr)
                        responseObj["aveData"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["6monthlyAve"]\
                                              + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                        responseObj["mean"] = str(areaMean.6monthlyMean[dateStr][areaStr])
		    elif periodStr == '12monthly':
                        responseObj["aveImg"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["12monthlyAve"]\
                                              + "_%s_ave_%s_trend.png" % (dateStr, areaStr)
                        responseObj["aveData"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["12monthlyAve"]\
                                              + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                        responseObj["mean"] = str(areaMean.12monthlyMean[dateStr][areaStr])
                elif form["runningAve"].value == "true":
		    if "runningInterval" in form:
                        runningInterval = int(form["runningInterval"].value)
                        if periodStr == 'monthly':
                            responseObj["aveImg"] = serverCfg["baseURL"]\
                                                  + serverCfg["cacheDir"]\
                                                  + ersstProduct["monthlyAve"]\
                                                  + '_%s_ave_%s_%02drunningMean.png"' % (dateStr, areaStr, runningInterval)
                            responseObj["aveData"] = serverCfg["baseURL"]\
                                                   + serverCfg["cacheDir"]\
                                                   + ersstProduct["monthlyAve"]\
                                                   + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                            responseObj["mean"] = str(areaMean.monthlyMean[dateStr][areaStr])
		    	elif periodStr == '3monthly':
                            responseObj["aveImg"] = serverCfg["baseURL"]\
                                                  + serverCfg["cacheDir"]\
                                                  + ersstProduct["3monthlyAve"]\
                                                  + '_%s_ave_%s_%02drunningMean.png"' % (dateStr, areaStr, runningInterval)
                            responseObj["aveData"] = serverCfg["baseURL"]\
                                                   + serverCfg["cacheDir"]\
                                                   + ersstProduct["3monthlyAve"]\
                                                   + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                            responseObj["mean"] = str(areaMean.3monthlyMean[dateStr][areaStr])
			elif periodStr == '6monthly':
                            responseObj["aveImg"] = serverCfg["baseURL"]\
                                                  + serverCfg["cacheDir"]\
                                                  + ersstProduct["6monthlyAve"]\
                                                  + '_%s_ave_%s_%02drunningMean.png"' % (dateStr, areaStr, runningInterval)
                            responseObj["aveData"] = serverCfg["baseURL"]\
                                                   + serverCfg["cacheDir"]\
                                                   + ersstProduct["6monthlyAve"]\
                                                   + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                            responseObj["mean"] = str(areaMean.6monthlyMean[dateStr][areaStr])
			elif periodStr == '12monthly':
                            responseObj["aveImg"] = serverCfg["baseURL"]\
                                                  + serverCfg["cacheDir"]\
                                                  + ersstProduct["12monthlyAve"]\
                                                  + '_%s_ave_%s_%02drunningMean.png"' % (dateStr, areaStr, runningInterval)
                            responseObj["aveData"] = serverCfg["baseURL"]\
                                                   + serverCfg["cacheDir"]\
                                                   + ersstProduct["12monthlyAve"]\
                                                   + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                            responseObj["mean"] = str(areaMean.12monthlyMean[dateStr][areaStr])
                else:
			if periodStr == 'monthly':
                        responseObj["aveImg"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["monthlyAve"]\
                                              + "_%s_ave_%s_.png" % (dateStr, areaStr)
                        responseObj["aveData"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["monthlyAve"]\
                                              + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                        responseObj["mean"] = str(areaMean.monthlyMean[dateStr][areaStr])
                    elif periodStr == '3monthly':
                        responseObj["aveImg"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["3monthlyAve"]\
                                              + "_%s_ave_%s_.png" % (dateStr, areaStr)
                        responseObj["aveData"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["3monthlyAve"]\
                                              + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                        responseObj["mean"] = str(areaMean.3monthlyMean[dateStr][areaStr])
                    elif periodStr == '6monthly':
                        responseObj["aveImg"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["6monthlyAve"]\
                                              + "_%s_ave_%s_.png" % (dateStr, areaStr)
                        responseObj["aveData"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["6monthlyAve"]\
                                              + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                        responseObj["mean"] = str(areaMean.6monthlyMean[dateStr][areaStr])
                    elif periodStr == '12monthly':
                        responseObj["aveImg"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["12monthlyAve"]\
                                              + "_%s_ave_%s_.png" % (dateStr, areaStr)
                        responseObj["aveData"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]\
                                              + ersstProduct["12monthlyAve"]\
                                              + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                        responseObj["mean"] = str(areaMean.12monthlyMean[dateStr][areaStr])
        elif mapStr == "dec":
	    if periodStr == 'monthly':
                fileName = decGraph % (ersstProduct["monthlyDec"], baseStr, areaStr, dateStr[:6])
	    if periodStr == '3monthly':
		fileName = decGraph % (ersstProduct["3monthlyDec"], baseStr, areaStr, dateStr[:6])
	    if periodStr == '6monthly':
		fileName = decGraph % (ersstProduct["6monthlyDec"], baseStr, areaStr, dateStr[:6])
	    if periodStr == '12monthly':
		fileName = decGraph % (ersstProduct["12monthlyDec"], baseStr, areaStr, dateStr[:6])
            outputFileName = outputDir + "/" + fileName
            if not os.path.exists(outputFileName + ".png"):
		plotter.plot(fileName, **args, baseStr)
	    if not os.path.exists(outputFileName + ".png"):
                responseObj["error"] = "Requested image is not available at this time."
            else:
                responseObj["img"] = serverCfg["baseURL"]\
				   + outputFileName + ".png"
		responseObj["mapeast"] = serverCfg["baseURL"]\
                                       + outputFileName + "_east.png"
                responseObj["mapeastw"] = serverCfg["baseURL"]\
                                       + outputFileName + "_east.pgw"
                responseObj["mapwest"] = serverCfg["baseURL"]\
				       + outputFileName + "_west.png"
                responseObj["mapwestw"] = serverCfg["baseURL"]\
                                       + outputFileName + "_west.pgw"
	elif mapStr == "trend":
	    if periodStr == 'monthly':
                fileName = trendGraph % (ersstProduct["monthlyTre"], areaStr, dateStr[4:6], baseStr)
            if periodStr == '3monthly':
                fileName = trendGraph % (ersstProduct["3monthlyTre"], baseStr, dateStr[4:6], baseStr)
            if periodStr == '6monthly':
                fileName = trendGraph % (ersstProduct["6monthlyTre"], baseStr, dateStr[4:6], baseStr)
            if periodStr == '12monthly':
                fileName = trendGraph % (ersstProduct["12monthlyTre"], baseStr, dateStr[4:6], baseStr)
	    outputFileName = outputDir + "/" + fileName
            if not os.path.exists(outputFileName + ".png"):
                plotter.plot(fileName, **args, baseStr)
            if not os.path.exists(outputFileName + ".png"):
                responseObj["error"] = "Requested image is not available at this time."
            else:
                responseObj["img"] = serverCfg["baseURL"]\
                                   + outputFileName + ".png"
                responseObj["mapeast"] = serverCfg["baseURL"]\
                                       + outputFileName + "_east.png"
                responseObj["mapeastw"] = serverCfg["baseURL"]\
                                       + outputFileName + "_east.pgw"
                responseObj["mapwest"] = serverCfg["baseURL"]\
                                       + outputFileName + "_west.png"
                responseObj["mapwestw"] = serverCfg["baseURL"]\
                                       + outputFileName + "_west.pgw"
    
        else:
        ####current xml html response
            if periodStr == 'monthly':
                fileName = trendGraph % (ersstProduct["monthly"], mapStr, areaStr, dateStr[:6])
            elif periodStr == '3monthly':
                fileName = trendGraph % (ersstProduct["3monthly"], mapStr, areaStr, dateStr[:6])
            elif periodStr == '6monthly':
                fileName = trendGraph % (ersstProduct["6monthly"], mapStr, areaStr, dateStr[:6])
            elif periodStr == '12monthly':
	 	fileName = trendGraph % (ersstProduct["12monthly"], mapStr, areaStr, dateStr[:6])
            outputFileName = serverCfg["outputDir"] + fileName 
            if not os.path.exists(outputFileName + ".png"):
                plotter.plot(fileName, **args, baseStr)
            if not os.path.exists(outputFileName + ".png"):
                responseObj["error"] = "Requested image is not available at this time."
            else:
                responseObj["img"] = serverCfg["baseURL"]\
                                   + outputFileName + ".png"
                responseObj["mapeast"] = serverCfg["baseURL"]\
                                       + outputFileName + "_east.png"
                responseObj["mapeastw"] = serverCfg["baseURL"]\
                                       + outputFileName + "_east.pgw"
                responseObj["mapwest"] = serverCfg["baseURL"]\
                                       + outputFileName + "_west.png"
                responseObj["mapwestw"] = serverCfg["baseURL"]\
                                       + outputFileName + "_west.pgw"

    response = json.dumps(responseObj)
    return response
