import os
import os.path
import sys
import json

import ww3Ext
from ..util import areaMean
from ..util import productName
from ..util import serverConfig

#Maybe move these into configuration later
pointExt = "%s_%s_%s_%s_datas"
recExt = "%s_%s_%s_%s_data_%s"

#get the server dependant path configurations
serverCfg = serverConfig.servers[serverConfig.currentServer]

#get dataset dependant production information
ww3Product = productName.products["ww3"]

#get the plotter
extractor = ww3Ext.WaveWatch3Extraction()


def process(form): 
    responseObj = {} #this object will be encoded into a json string
    if "variable" in form and "lllat" in form and "lllon" in form\
        and "urlat" in form and "urlon" in form:
        varStr = form["variable"].value
        lllatStr = form["lllat"].value
        lllonStr = form["lllon"].value
        urlatStr = form["urlat"].value
        urlonStr = form["urlon"].value

        args = {"var": varStr,
                "lllat": lllatStr,
                "lllon": lllonStr,
                "urlat": urlatStr,
                "urlon": urlonStr}

        if lllatStr == urlatStr and lllonStr == urlonStr:
            filename = pointExt % (ww3Product["point"], lllatStr, lllonStr, varStr)
        else:
            filename = recExt % (ww3Product["rect"], lllatStr, lllonStr, urlatStr, urlonStr, varStr)

        outputFileName = serverCfg["outputDir"] + filename 
        if not os.path.exists(outputFileName + ".txt"):
            timeseries, latsLons, latLonValues, gridValues = extractor.extract(lllatStr, lllonStr, varStr)
            extractor.writeOutput(outputFileName + ".txt", latsLons, timeseries, gridValues) 
        if not os.path.exists(outputFileName + ".txt"):
            responseObj["error"] = "Error occured during the extraction."
        else:
            responseObj["ext"] = serverCfg["baseURL"]\
                               + outputFileName + ".txt"

    response = json.dumps(responseObj)
    return response
