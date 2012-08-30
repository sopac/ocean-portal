import os
import os.path
import sys
import json

import ww3ExtA
import ocean.util as util
from ..util import areaMean
from ..util import productName
from ..netcdf import extractor as xt
import wavecaller as wc
import formatter as frm
import monthconfig as mc
import landerror as le
import GridPointFinder as GPF
#Maybe move these into configuration later
pointExt = "%s_%s_%s_%s_%s"
recExt = "%s_%s_%s_%s_%s_%s"

#get the server dependant path configurations
serverCfg = util.get_server_config()

#get dataset dependant production information
ww3Product = productName.products["ww3"]

#get the plotter
extractor = ww3ExtA.WaveWatch3Extraction()
getGrid = GPF.Extractor()
GridPoints = xt.Extractor()

def process(form):
    responseObj = {} #this object will be encoded into a json string
    if "variable" in form and "lllat" in form and "lllon" in form\
        and "urlat" in form and "urlon" in form and "date" in form\
             and "period" in form:

        varStr = form["variable"].value
        lllatStr = form["lllat"].value
        lllonStr = form["lllon"].value
        urlatStr = form["urlat"].value
        urlonStr = form["urlon"].value
        dateStr = form["date"].value
        periodStr = form["period"].value

        args = {"var": varStr,
                "lllat": lllatStr,
                "lllon": lllonStr,
                "urlat": urlatStr,
                "urlon": urlonStr,
                "date": dateStr,
		"period": periodStr}

        month = dateStr[4:6]
        k1, k2, mthStr = mc.monthconfig(month)

        if lllatStr == urlatStr and lllonStr == urlonStr:
            lats,lons,vari = getGrid.getGridPoint(lllatStr,lllonStr,varStr)
            (latStr,lonStr),(latgrid,longrid) = GridPoints.getGridPoint(lllatStr,lllonStr,lats,lons,vari,strategy = "exhaustive") 
            (latStr, lonStr) = frm.nameformat(latStr,lonStr)
            filename = pointExt % (ww3Product["point"], latStr, lonStr, varStr, month)
        else:
            filename = recExt % (ww3Product["rect"], lllatStr, lllonStr, urlatStr, urlonStr, varStr, month)

        outputFileName = serverCfg["outputDir"] + filename

        if not os.path.exists(outputFileName + ".txt"):
            timeseries, latsLons, latLonValues, gridValues, (gridLat, gridLon) = extractor.extract(lllatStr, lllonStr, varStr, k1, k2)
            extractor.writeOutput(outputFileName + ".txt", latStr, lonStr, timeseries, gridValues, varStr)
        if not os.path.exists(outputFileName + ".txt"):
            responseObj["error"] = "Error occured during the extraction."
        else:
            responseObj['ext'] = os.path.join(serverCfg['baseURL'],
                                              serverCfg['rasterURL'],
                                              filename + '.txt')

        if not os.path.exists(outputFileName + ".png"):
            timeseries, latsLons, latLonValues, gridValues, (gridLat, gridLon) = extractor.extract(lllatStr, lllonStr, varStr, k1, k2)
            try:
                wc.wavecaller(outputFileName, varStr, gridLat, gridLon, gridValues, mthStr)
            except le.LandError:
	        responseObj["error"] = "Invalid data point.  Please try another location."
	    except:
                if serverCfg['debug']:
                    raise
                else:
		    responseObj["error"] = "Error occured during the extraction.  Image could not be generated."	
                    pass
                 
        if os.path.exists(outputFileName + ".png"):
            responseObj['img'] = os.path.join(serverCfg['baseURL'],
                                              serverCfg['rasterURL'],
                                              filename + '.png')

    response = json.dumps(responseObj)

    return response
