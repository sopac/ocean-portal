#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Jason Smith <jason.smith@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os
import os.path
import sys
import copy

from ocean import util, config
from ocean.util import areaMean
from ocean.config import productName
from ocean.netcdf import extractor as xt
from ocean.datasets import Dataset

import wavecaller as wc
import formatter as frm
import monthconfig as mc
import landerror as le
import ww3ExtA
import GridPointFinder as GPF

#Maybe move these into configuration later
pointExt = '%s_%s_%s_%s_%s'
recExt = '%s_%s_%s_%s_%s_%s'

#get the server dependant path configurations
serverCfg = config.get_server_config()

#get dataset dependant production information
ww3Product = productName.products['ww3']

#get the plotter
extractor = ww3ExtA.WaveWatch3Extraction()
getGrid = GPF.Extractor()
GridPoints = xt.Extractor()

class ww3(Dataset):

    __form_params__ = {
        'lllat': float,
        'lllon': float,
        'urlat': float,
        'urlon': float,
    }
    __form_params__.update(Dataset.__form_params__)

    __required_params__ = Dataset.__required_params__ + [
        'date',
        'lllat',
        'lllon',
    ]

    __periods__ = [
        'monthly',
    ]

    __variables__ = [
        'Hs',
        'Tm',
        'Dm',
    ]

    __plots__ = [
        'ts',
        'waverose',
    ]

    def process(self, params):
        response = {}

        varStr = params['variable']
        lllatStr = params['lllat']
        lllonStr = params['lllon']
        urlatStr = params['urlat']
        urlonStr = params['urlon']
        dateStr = params['date'].strftime('%Y%m%d')
        periodStr = params['period']

        month = dateStr[4:6]
        k1, k2, mthStr = mc.monthconfig(month)

        if lllatStr == urlatStr and lllonStr == urlonStr:
            lats, lons, vari = getGrid.getGridPoint(lllatStr, lllonStr, varStr)
            (latStr,lonStr),(latgrid,longrid) = \
                GridPoints.getGridPoint(lllatStr, lllonStr, lats, lons,
                                        vari,strategy='exhaustive')
            (latStr, lonStr) = frm.nameformat(latStr, lonStr)
            filename = pointExt % (ww3Product['point'], latStr, lonStr,
                                   varStr, month)
        else:
            filename = recExt % (ww3Product['rect'],
                                 lllatStr, lllonStr,
                                 urlatStr, urlonStr,
                                 varStr, month)

        outputFileName = serverCfg['outputDir'] + filename

        timeseries = None

        if not os.path.exists(outputFileName + '.txt'):
            timeseries, latsLons, latLonValues, gridValues, \
                (gridLat, gridLon) = extractor.extract(lllatStr, lllonStr,
                                                       varStr, k1, k2)

            dataVals = copy.copy(gridValues)
            extractor.writeOutput(outputFileName + '.txt',
                                  latStr, lonStr, timeseries, dataVals, varStr)

        if not os.path.exists(outputFileName + '.txt'):
            response['error'] = "Error occured during the extraction."
        else:
            response['ext'] = os.path.join(serverCfg['baseURL'],
                                           serverCfg['rasterURL'],
                                           filename + '.txt')
            os.utime(os.path.join(serverCfg['outputDir'], filename + '.txt'),
                     None)

        if not os.path.exists(outputFileName + ".png"):
            if timeseries is None:
                # only reload the data if we have to
                timeseries, latsLons, latLonValues, gridValues, \
                    (gridLat, gridLon) = extractor.extract(lllatStr, lllonStr,
                                                           varStr, k1, k2)
            try:
                wc.wavecaller(outputFileName, varStr,
                              gridLat, gridLon, lllatStr, lllonStr,
                              gridValues, mthStr)
            except le.LandError:
                response['error'] = "Invalid data point. Please try another location."

        if os.path.exists(outputFileName + '.png'):
            response['img'] = os.path.join(serverCfg['baseURL'],
                                           serverCfg['rasterURL'],
                                           filename + '.png')
            os.utime(os.path.join(serverCfg['outputDir'], filename + '.png'),
                     None)

        return response
