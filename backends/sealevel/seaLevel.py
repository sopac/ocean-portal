import os
import os.path
import sys
import json

import seaLevelPlotter
import ocean.util as util
from ..util import productName
from ..util import tidalGaugeConfig

#Maybe move these into configuration later
seaGraph = "%s_%s_%s_%s"
seaChart = "%s_%s_%s"

#get the server dependant path configurations
serverCfg = util.get_server_config()

#get dataset dependant production information
seaLevelProduct = productName.products["sealevel"]

#get the plotter
plotter = seaLevelPlotter.SeaLevelPlotter()

def process(form): 
    responseObj = {} #this object will be encoded into a json string
    responseObj["img"] = [] #img is a list of images
    if "variable" in form and "date" in form and "period" in form and "area" in form:
        variableStr = form["variable"].value
        dateStr = form["date"].value
        areaStr = form["area"].value
        periodStr = form["period"].value

        args = {"var": variableStr,
                "date": dateStr,
                "area": areaStr,
                "period": periodStr}
    
        if periodStr == 'monthly':
            fileName = seaGraph % (seaLevelProduct["monthly"], variableStr, areaStr, dateStr[:6])
        outputFileName = serverCfg["outputDir"] + fileName 
        outputFiles = [ '.png', '_east.png', '_east.pgw',
            '_west.png', '_west.pgw' ]

        if not util.check_files_exist(outputFileName, outputFiles):
            plotter.plot(fileName, **args)

        if not util.check_files_exist(outputFileName, outputFiles):
            responseObj["error"] = "Requested image is not available at this time."
        else:
            responseObj["img"].append(serverCfg["baseURL"]\
                               + outputFileName + ".png")
            responseObj["mapeast"] = serverCfg["baseURL"]\
                                   + outputFileName + "_east.png"
            responseObj["mapeastw"] = serverCfg["baseURL"]\
                                    + outputFileName + "_east.pgw"
            responseObj["mapwest"] = serverCfg["baseURL"]\
                                   + outputFileName + "_west.png"
            responseObj["mapwestw"] = serverCfg["baseURL"]\
                                    + outputFileName + "_west.pgw"

    if "tidalGaugeId" in form:
        tidalGaugeId = form["tidalGaugeId"].value

        args["tidalGaugeId"] = tidalGaugeId
        args["tidalGaugeName"] = tidalGaugeConfig.tidalGauge[tidalGaugeId]["name"]
        args["lat"] = tidalGaugeConfig.tidalGauge[tidalGaugeId]["lat"] 
        args["lon"] = tidalGaugeConfig.tidalGauge[tidalGaugeId]["lon"] 

        #plot altimetry 
        var = "tid"
        args["var"] = var
        fileName = seaChart % (seaLevelProduct["monthly"], tidalGaugeId, var)
        outputFileName = serverCfg["outputDir"] + fileName 
        if not os.path.exists(outputFileName + ".png"):
            plotter.plotTidalGauge(outputFileName, **args)
        if not os.path.exists(outputFileName + ".png"):
            responseObj["error"] = "Requested image is not available at this time."
        else:
            responseObj["img"].append(serverCfg["baseURL"]\
                               + outputFileName + ".png")
            responseObj["tid"] = serverCfg["baseURL"]\
                               + outputFileName + ".txt"
        #plot altimetry 
        var = "alt"
        args["var"] = var
        fileName = seaChart % (seaLevelProduct["monthly"], tidalGaugeId, var)
        outputFileName = serverCfg["outputDir"] + fileName 
        if not os.path.exists(outputFileName + ".png"):
            plotter.plotTimeseries(outputFileName, **args)
        if not os.path.exists(outputFileName + ".png"):
            responseObj["error"] = "Requested image is not available at this time."
        else:
            responseObj["img"].append(serverCfg["baseURL"]\
                               + outputFileName + ".png")
            responseObj["alt"] = serverCfg["baseURL"]\
                               + outputFileName + ".txt"

        #plot reconstruction
        var = "rec"
        args["var"] = var
        fileName = seaChart % (seaLevelProduct["monthly"], tidalGaugeId, var)
        outputFileName = serverCfg["outputDir"] + fileName 
        if not os.path.exists(outputFileName + ".png"):
            plotter.plotTimeseries(outputFileName, **args)
        if not os.path.exists(outputFileName + ".png"):
            responseObj["error"] = "Requested image is not available at this time."
        else:
            responseObj["img"].append(serverCfg["baseURL"]\
                               + outputFileName + ".png")
            responseObj["rec"] = serverCfg["baseURL"]\
                               + outputFileName + ".txt"

        #plot altimery and reconstruction comparison from 1950
        
    response = json.dumps(responseObj)
    return response
