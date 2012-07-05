import os
import os.path
import sys
import json

import branPlotter
from ..util import areaMean
from ..util import productName
from ..util import serverConfig

#Maybe move these into configuration later
branGraph = "%s_%s_%s_%s"
avebranGraph = "%s_%s_%s_%save"
decbranGraph = "%s_%s_%sdec.png"

#get the server dependant path configurations
serverCfg = serverConfig.servers[serverConfig.currentServer]

#get dataset dependant production information
branProduct = productName.products["blue_link"]

#get the plotter
plotter = branPlotter.branPlotter()

def process(form):
    responseObj = {} #this object will be encoded into a json string
    if "variable" in form and "date" in form and "period" in form and "area" in form:
        mapStr = form["variable"].value
        dateStr = form["date"].value
        areaStr = form["area"].value
        periodStr = form["period"].value

        args = {"variable": mapStr,
                "date": dateStr,
                "area": areaStr,
                "period": periodStr}

    if "xlat1" in form:
        xlat1= form["xlat1"].value

        args["xlat1"] = xlat1
        args["xlon1"] = xlon1
        args["tidalGaugeName"] = tidalGaugeConfig.tidalGauge[tidalGaugeId]["name"]
        args["xlat2"] = branConfig.bran[xlat1]["xlat2"]
        args["xlon2"] = branConfig.bran[xlon2]["xlon2"]

        #plot subsurface
        if periodStr == 'monthly':
            var = "temp"
            args["variable"] = var
            fileName = seaChart % (branProduct["monthly"], tidalGaugeId, var)
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
            var = "temp_ano"
            args["variable"] = var
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
            var = "temp_dec"
            args["variable"] = var
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
            var = "salt"
            args["variable"] = var
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
            var = "eta"
            args["variable"] = var
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
            var = "uv"
            args["variable"] = var
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

        else:
        ####current xml html response
            if periodStr == 'daily':
                fileName = branGraph % (branProduct["daily"], mapStr, areaStr, dateStr)
            elif periodStr == 'monthly':
                fileName = branGraph % (branProduct["monthly"], mapStr, areaStr, dateStr[:6])
            elif periodStr == 'yearly':
                fileName = branGraph % (branProduct["yearly"], mapStr, areaStr, dateStr[:4])
            elif periodStr == '3monthly':
                fileName = branGraph % (branProduct["3monthly"], mapStr, areaStr, dateStr[:6])
            elif periodStr == '6monthly':
                fileName = branGraph % (branProduct["6monthly"], mapStr, areaStr, dateStr[:6])
            elif periodStr == 'weekly':
                fileName = branGraph % (branProduct["weekly"], mapStr, areaStr, dateStr)
            outputFileName = serverCfg["outputDir"] + fileName
            if not os.path.exists(outputFileName + ".png"):
                plotter.plot(fileName, mapStr, dateStr, areaStr, periodStr)
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
