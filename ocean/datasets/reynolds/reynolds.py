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
from ocean.datasets import Dataset
from ocean.netcdf.plotter import COMMON_FILES
from ocean.util import areaMean
from ocean.config import productName

import reynoldsPlotter

#Maybe move these into configuration later
sstGraph = '%s_%s_%s_%s'
aveSstGraph = '%s_%s_%s_%save'
decGraph = '%s_%s_%sdec.png'

#get the server dependant path configurations
serverCfg = config.get_server_config()

#get dataset dependant production information
reynoldsProduct = productName.products['reynolds']

CACHE_URL = os.path.join(serverCfg['baseURL'],
                         serverCfg['rasterURL'],
                         serverCfg['cacheDir']['reynolds'])

class reynolds(Dataset):

    __form_params__ = {
        'average': bool,
        'trend': bool,
        'runningInterval': int,
    }
    __form_params__.update(Dataset.__form_params__)


    __variables__ = [
        'mean',
        'dec',
        'anom',
    ]

    __periods__ = [
        'monthly',
        'yearly',
    ]

    def process(self, params):
        response = {}

        mapStr = params['variable']
        dateStr = params['date'].strftime('%Y%m%d')
        areaStr = params['area']
        periodStr = params['period']

        plotter = reynoldsPlotter.ReynoldsPlotter()

        if params.get('average', False): # averages
            dateStr = dateStr[4:6] # extract month value

            if params['trend']:
                if periodStr == 'monthly':
                    response['aveImg'] = CACHE_URL + \
                        reynoldsProduct['monthlyAve'] + \
                        '_%s_ave_%s_trend.png' % (dateStr, areaStr)
                    response['aveData'] = CACHE_URL + \
                        reynoldsProduct['monthlyAve'] + \
                        '_%s_ave_%s.txt' % (dateStr, areaStr)
                    response['mean'] = areaMean.monthlyMean[dateStr][areaStr]

                elif periodStr == 'yearly':
                    response['aveImg'] = CACHE_URL + \
                        reynoldsProduct['yearlyAve'] + \
                        '_ave_%s_trend.png"' % (areaStr)
                    response['aveData'] = CACHE_URL + \
                        reynoldsProduct['yearlyAve'] + \
                        '_ave_%s.txt' % (areaStr)
                    response['mean'] = areaMean.yearlyMean[areaStr]

            elif params['runningAve']:
                if periodStr == 'monthly':
                    if 'runningInterval' in params:
                        runningInterval = params['runningInterval']

                        response['aveImg'] = CACHE_URL + \
                            reynoldsProduct['monthlyAve'] + \
                            '_%s_ave_%s_%02dmoving.png' % (dateStr,
                                                           areaStr,
                                                           runningInterval)
                        response['aveData'] = CACHE_URL + \
                            reynoldsProduct['monthlyAve'] + \
                            '_%s_ave_%s.txt"' % (dateStr, areaStr)
                        response['mean'] = areaMean.monthlyMean[dateStr][areaStr]

                elif periodStr == 'yearly':
                    response['aveImg'] = CACHE_URL + \
                        reynoldsProduct['yearlyAve'] + \
                        '_ave_%s_%02dmoving.png' % (areaStr,
                                                    runningInterval)
                    response['aveData'] = CACHE_URL + \
                        reynoldsProduct['yearlyAve'] + \
                        '_ave_%s.txt' % (areaStr)
                    response['mean'] = areaMean.yearlyMean[areaStr]

            else: # not trend or runningAve
                if periodStr == 'monthly':
                    response['aveImg'] = CACHE_URL + \
                        reynoldsProduct['monthlyAve'] + \
                        '_%s_ave_%s.png"' % (dateStr, areaStr)
                    response['aveData'] = CACHE_URL + \
                        reynoldsProduct['monthlyAve'] + \
                        '_%s_ave_%s.txt"' % (dateStr, areaStr)
                    response['mean'] = areaMean.monthlyMean[dateStr][areaStr]

                elif periodStr == 'yearly':
                    response['aveImg'] = CACHE_URL + \
                        reynoldsProduct['yearlyAve'] + \
                        '_ave_%s.png"' % (areaStr)
                    response['aveData'] = CACHE_URL + \
                        reynoldsProduct['yearlyAve'] + \
                        '_ave_%s.txt"' % (areaStr)
                    response['mean'] = areaMean.yearlyMean[areaStr]

        elif mapStr == 'dec': # deciles
            fileName = decGraph % (reynoldsProduct['monthlyDec'],
                                   areaStr, dateStr[:6])
            outputFileName = os.path.join(serverCfg['outputDir'], fileName)

            if not util.check_files_exist(outputFileName,
                                          COMMON_FILES.values()):
                plotter.plot(fileName, **params)

            if not util.check_files_exist(outputFileName,
                                          COMMON_FILES.values()):
                response['error'] = "Requested image is not available at this time."
            else:
                response.update(util.build_response_object(
                        COMMON_FILES.keys(),
                        os.path.join(serverCfg['baseURL'],
                                     serverCfg['rasterURL'],
                                     fileName),
                        COMMON_FILES.values()))
                util.touch_files(os.path.join(serverCfg['outputDir'],
                                              fileName),
                                 COMMON_FILES.values())
        else:
            if periodStr == 'daily':
                fileName = sstGraph % (reynoldsProduct['daily'],
                                       mapStr, areaStr, dateStr)
            elif periodStr == 'monthly':
                fileName = sstGraph % (reynoldsProduct['monthly'],
                                       mapStr, areaStr, dateStr[:6])
            elif periodStr == 'yearly':
                fileName = aveSstGraph % (reynoldsProduct['yearly'],
                                          mapStr, areaStr, dateStr[:4])
            elif periodStr == '3monthly':
                fileName = aveSstGraph % (reynoldsProduct['3monthly'],
                                          mapStr, areaStr, dateStr[:6])
            elif periodStr == '6monthly':
                fileName = aveSstGraph % (reynoldsProduct['6monthly'],
                                          mapStr, areaStr, dateStr[:6])
            elif periodStr == 'weekly':
                fileName = aveSstGraph % (reynoldsProduct['weekly'],
                                          mapStr, areaStr, dateStr)

            outputFileName = os.path.join(serverCfg['outputDir'], fileName)

            if not util.check_files_exist(outputFileName,
                                          COMMON_FILES.values()):
                plotter.plot(fileName, **params)

            if not util.check_files_exist(outputFileName,
                                          COMMON_FILES.values()):
                response['error'] = "Requested image is not available at this time."
            else:
                response.update(util.build_response_object(
                        COMMON_FILES.keys(),
                        os.path.join(serverCfg['baseURL'],
                                     serverCfg['rasterURL'],
                                     fileName),
                        COMMON_FILES.values()))
                util.touch_files(os.path.join(serverCfg['outputDir'],
                                              fileName),
                                 COMMON_FILES.values())

        return response
