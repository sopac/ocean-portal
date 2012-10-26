#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os
import os.path
import sys

from ocean import util, config
from ocean.netcdf.plotter import COMMON_FILES
from ocean.config import productName, tidalGaugeConfig

import sealevelPlotter

#Maybe move these into configuration later
seaGraph = "%s_%s_%s_%s"
seaChart = "%s_%s_%s"

#get the server dependant path configurations
serverCfg = util.get_server_config()

#get dataset dependant production information
seaLevelProduct = productName.products["sealevel"]

#get the plotter
plotter = sealevelPlotter.SeaLevelPlotter()

def process(form): 
    responseObj = {} #this object will be encoded into a json string
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
        outputFileName = serverCfg['outputDir'] + fileName

        if not util.check_files_exist(outputFileName, COMMON_FILES.values()):
            plotter.plot(fileName, **args)

        if not util.check_files_exist(outputFileName, COMMON_FILES.values()):
            responseObj['error'] = "Requested image is not available at this time."
        else:
            responseObj.update(util.build_response_object(
                    COMMON_FILES.keys(),
                    os.path.join(serverCfg['baseURL'],
                                 serverCfg['rasterURL'],
                                 fileName),
                    COMMON_FILES.values()))

            util.touch_files(os.path.join(serverCfg['outputDir'],
                                          fileName),
                             COMMON_FILES.values())

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
        outputFileName = os.path.join(serverCfg['outputDir'], fileName)

        if not os.path.exists(outputFileName + ".png"):
            plotter.plotTidalGauge(outputFileName, **args)
        if not os.path.exists(outputFileName + ".png"):
            responseObj['error'] = "Requested image is not available at this time."
        else:
            responseObj.update(util.build_response_object(
                [ 'tidimg', 'tidtxt' ],
                os.path.join(serverCfg['baseURL'],
                             serverCfg['rasterURL'],
                             fileName),
                [ '.png', '.txt' ]))
            util.touch_files(os.path.join(serverCfg['outputDir'],
                                          fileName),
                             [ '.png', '.txt' ])

        #plot altimetry 
        var = "alt"
        args["var"] = var
        fileName = seaChart % (seaLevelProduct["monthly"], tidalGaugeId, var)
        outputFileName = os.path.join(serverCfg['outputDir'], fileName)

        if not os.path.exists(outputFileName + ".png"):
            plotter.plotTimeseries(outputFileName, **args)
        if not os.path.exists(outputFileName + ".png"):
            responseObj['error'] = "Requested image is not available at this time."
        else:
            responseObj.update(util.build_response_object(
                [ 'altimg', 'alttxt' ],
                os.path.join(serverCfg['baseURL'],
                             serverCfg['rasterURL'],
                             fileName),
                [ '.png', '.txt' ]))
            util.touch_files(os.path.join(serverCfg['outputDir'],
                                          fileName),
                             [ '.png', '.txt' ])

        #plot reconstruction
        var = "rec"
        args["var"] = var
        fileName = seaChart % (seaLevelProduct["monthly"], tidalGaugeId, var)
        outputFileName = os.path.join(serverCfg['outputDir'], fileName)

        if not os.path.exists(outputFileName + ".png"):
            plotter.plotTimeseries(outputFileName, **args)
        if not os.path.exists(outputFileName + ".png"):
            responseObj['error'] = "Requested image is not available at this time."
        else:
            responseObj.update(util.build_response_object(
                [ 'recimg', 'rectxt' ],
                os.path.join(serverCfg['baseURL'],
                             serverCfg['rasterURL'],
                             fileName),
                [ '.png', '.txt' ]))
            util.touch_files(os.path.join(serverCfg['outputDir'],
                                          fileName),
                             [ '.png', '.txt' ])

        #plot altimery and reconstruction comparison from 1950

    return responseObj
