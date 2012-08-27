import os
import os.path
import sys
import json

import reynoldsPlotter
import ocean.util as util
from ocean.netcdf.plotter import COMMON_FILES
from ..util import areaMean
from ..util import productName

#Maybe move these into configuration later
sstGraph = "%s_%s_%s_%s"
aveSstGraph = "%s_%s_%s_%save"
decGraph = "%s_%s_%sdec.png"

#get the server dependant path configurations
serverCfg = util.get_server_config()

#get dataset dependant production information
reynoldsProduct = productName.products["reynolds"]

#get the plotter
plotter = reynoldsPlotter.ReynoldsPlotter()

def process(form): 
    responseObj = {} #this object will be encoded into a json string
    if "map" in form and "date" in form and "period" in form and "area" in form:
        mapStr = form["map"].value
        dateStr = form["date"].value
        areaStr = form["area"].value
        periodStr = form["period"].value

        args = {"map": mapStr,
                "date": dateStr,
                "area": areaStr,
                "period": periodStr}

    
#        if mapStr == 'anom':
        if "average" in form and form["average"].value == "true":
            dateStr = dateStr[4:6] #extract month value
            if form["trend"].value == "true":
                if periodStr == 'monthly':
                    responseObj["aveImg"] = serverCfg["baseURL"]\
                                          + serverCfg["cacheDir"]["reynolds"]\
                                          + reynoldsProduct["monthlyAve"]\
                                          + "_%s_ave_%s_trend.png" % (dateStr, areaStr)
                    responseObj["aveData"] = serverCfg["baseURL"]\
                                          + serverCfg["cacheDir"]["reynolds"]\
                                          + reynoldsProduct["monthlyAve"]\
                                          + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                    responseObj["mean"] = str(areaMean.monthlyMean[dateStr][areaStr])
                elif periodStr == 'yearly':
                    responseObj["aveImg"] = serverCfg["baseURL"]\
                                          + serverCfg["cacheDir"]["reynolds"]\
                                          + reynoldsProduct["yearlyAve"]\
                                          + '_ave_%s_trend.png"' % (areaStr)
                    responseObj["aveData"] = serverCfg["baseURL"]\
                                          + serverCfg["cacheDir"]["reynolds"]\
                                          + reynoldsProduct["yearlyAve"] \
                                          + '"_ave_%s.txt"' % (areaStr)
                    responseObj["mean"] = str(areaMean.yearlyMean[areaStr])
            elif form["runningAve"].value == "true":
                if periodStr == 'monthly':
                    if "runningInterval" in form:
                        runningInterval = int(form["runningInterval"].value)
                        responseObj["aveImg"] = serverCfg["baseURL"]\
                                              + serverCfg["cacheDir"]["reynolds"]\
                                              + reynoldsProduct["monthlyAve"]\
                                              + '_%s_ave_%s_%02dmoving.png"' % (dateStr, areaStr, runningInterval)
                        responseObj["aveData"] = serverCfg["baseURL"]\
                                               + serverCfg["cacheDir"]["reynolds"]\
                                               + reynoldsProduct["monthlyAve"]\
                                               + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                        responseObj["mean"] = str(areaMean.monthlyMean[dateStr][areaStr])
                elif periodStr == 'yearly':
                    responseObj["aveImg"] = serverCfg["baseURL"]\
                                          + serverCfg["cacheDir"]["reynolds"]\
                                          + reynoldsProduct["yearlyAve"]\
                                          + '_ave_%s_%02dmoving.png"' % (areaStr, runningInterval)
                    responseObj["aveData"] = serverCfg["baseURL"]\
                                          + serverCfg["cacheDir"]["reynolds"]\
                                          + reynoldsProduct["yearlyAve"]\
                                          + '_ave_%s.txt' % (areaStr)
                    responseObj["mean"] = str(areaMean.yearlyMean[areaStr])
            else:
                if periodStr == 'monthly':
                    responseObj["aveImg"] = serverCfg["baseURL"]\
                                          + serverCfg["cacheDir"]["reynolds"]\
                                          + reynoldsProduct["monthlyAve"]\
                                          + '_%s_ave_%s.png"' % (dateStr, areaStr)
                    responseObj["aveData"] = serverCfg["baseURL"]\
                                           + serverCfg["cacheDir"]["reynolds"]\
                                           + reynoldsProduct["monthlyAve"]\
                                           + '_%s_ave_%s.txt"' % (dateStr, areaStr)
                    responseObj["mean"] = str(areaMean.monthlyMean[dateStr][areaStr])
                elif periodStr == 'yearly':
                    responseObj["aveImg"] = serverCfg["baseURL"]\
                                          + serverCfg["cacheDir"]["reynolds"]\
                                          + reynoldsProduct["yearlyAve"]\
                                          + '_ave_%s.png"' % (areaStr)
                    responseObj["aveData"] = serverCfg["baseURL"]\
                                           + serverCfg["cacheDir"]["reynolds"]\
                                           + reynoldsProduct["yearlyAve"]\
                                           + '_ave_%s.txt"' % (areaStr)
                    responseObj["mean"] = str(areaMean.yearlyMean[areaStr])
        elif mapStr == "dec":
            fileName = decGraph % (reynoldsProduct["monthlyDec"], areaStr, dateStr[:6])
            outputFileName = serverCfg["outputDir"] + fileName

            if not util.check_files_exist(outputFileName, COMMON_FILES.values()):
                plotter.plot(fileName, **args)

            if not util.check_files_exist(outputFileName, COMMON_FILES.values()):
                responseObj["error"] = "Requested image is not available at this time."
            else:
                responseObj.update(util.build_response_object(
                        COMMON_FILES.keys(),
                        serverCfg['baseURL'] + outputFileName,
                        COMMON_FILES.values()))
        else:
        ####current xml html response
            if periodStr == 'daily':
                fileName = sstGraph % (reynoldsProduct["daily"], mapStr, areaStr, dateStr)
            elif periodStr == 'monthly':
                fileName = sstGraph % (reynoldsProduct["monthly"], mapStr, areaStr, dateStr[:6])
            elif periodStr == 'yearly':
                fileName = aveSstGraph % (reynoldsProduct["yearly"], mapStr, areaStr, dateStr[:4])
            elif periodStr == '3monthly':
                fileName = aveSstGraph % (reynoldsProduct["3monthly"], mapStr, areaStr, dateStr[:6])
            elif periodStr == '6monthly':
                fileName = aveSstGraph % (reynoldsProduct["6monthly"], mapStr, areaStr, dateStr[:6])
            elif periodStr == 'weekly':
                fileName = aveSstGraph % (reynoldsProduct["weekly"], mapStr, areaStr, dateStr)

            outputFileName = serverCfg["outputDir"] + fileName

            if not util.check_files_exist(outputFileName, COMMON_FILES.values()):
                try:
                    plotter.plot(fileName, **args)
                except:
                    if serverCfg['debug']:
                        raise
                    else:
                        pass

            if not util.check_files_exist(outputFileName, COMMON_FILES.values()):
                responseObj['error'] = "Requested image is not available at this time."
            else:
                responseObj.update(util.build_response_object(
                        COMMON_FILES.keys(),
                        serverCfg['baseURL'] + outputFileName,
                        COMMON_FILES.values()))

    response = json.dumps(responseObj)
    return response
