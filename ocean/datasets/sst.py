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

serverCfg = config.get_server_config()

class SST(Dataset):

    __form_params__ = {
        'average': bool,
        'trend': bool,
        'runningInterval': int,
    }
    __form_params__.update(Dataset.__form_params__)

    __required_params__ = Dataset.__required_params__ + [
        'date',
        'area',
    ]

    __variables__ = [
        'mean',
        'dec',
        'anom',
    ]

    __plots__ = [
        'map',
    ]

    sstGraph = '%s_%s_%s_%s'
    aveSstGraph = '%s_%s_%s_%save'
    decGraph = '%s_%s_%sdec.png'

    def process(self, params):
        response = {}

        mapStr = params['variable']
        dateStr = params['date'].strftime('%Y%m%d')
        areaStr = params['area']
        periodStr = params['period']

        if params.get('average', False): # averages
            dateStr = dateStr[4:6] # extract month value

            if params['trend']:
                if periodStr == 'monthly':
                    response['aveImg'] = CACHE_URL + \
                        self.product['monthlyAve'] + \
                        '_%s_ave_%s_trend.png' % (dateStr, areaStr)
                    response['aveData'] = CACHE_URL + \
                        self.product['monthlyAve'] + \
                        '_%s_ave_%s.txt' % (dateStr, areaStr)
                    response['mean'] = areaMean.monthlyMean[dateStr][areaStr]

                elif periodStr == 'yearly':
                    response['aveImg'] = CACHE_URL + \
                        self.product['yearlyAve'] + \
                        '_ave_%s_trend.png"' % (areaStr)
                    response['aveData'] = CACHE_URL + \
                        self.product['yearlyAve'] + \
                        '_ave_%s.txt' % (areaStr)
                    response['mean'] = areaMean.yearlyMean[areaStr]

            elif params['runningAve']:
                if periodStr == 'monthly':
                    if 'runningInterval' in params:
                        runningInterval = params['runningInterval']

                        response['aveImg'] = CACHE_URL + \
                            self.product['monthlyAve'] + \
                            '_%s_ave_%s_%02dmoving.png' % (dateStr,
                                                           areaStr,
                                                           runningInterval)
                        response['aveData'] = CACHE_URL + \
                            self.product['monthlyAve'] + \
                            '_%s_ave_%s.txt"' % (dateStr, areaStr)
                        response['mean'] = areaMean.monthlyMean[dateStr][areaStr]

                elif periodStr == 'yearly':
                    response['aveImg'] = CACHE_URL + \
                        self.product['yearlyAve'] + \
                        '_ave_%s_%02dmoving.png' % (areaStr,
                                                    runningInterval)
                    response['aveData'] = CACHE_URL + \
                        self.product['yearlyAve'] + \
                        '_ave_%s.txt' % (areaStr)
                    response['mean'] = areaMean.yearlyMean[areaStr]

            else: # not trend or runningAve
                if periodStr == 'monthly':
                    response['aveImg'] = CACHE_URL + \
                        self.product['monthlyAve'] + \
                        '_%s_ave_%s.png"' % (dateStr, areaStr)
                    response['aveData'] = CACHE_URL + \
                        self.product['monthlyAve'] + \
                        '_%s_ave_%s.txt"' % (dateStr, areaStr)
                    response['mean'] = areaMean.monthlyMean[dateStr][areaStr]

                elif periodStr == 'yearly':
                    response['aveImg'] = CACHE_URL + \
                        self.product['yearlyAve'] + \
                        '_ave_%s.png"' % (areaStr)
                    response['aveData'] = CACHE_URL + \
                        self.product['yearlyAve'] + \
                        '_ave_%s.txt"' % (areaStr)
                    response['mean'] = areaMean.yearlyMean[areaStr]

        elif mapStr == 'dec': # deciles
            fileName = self.decGraph % (self.product['monthlyDec'],
                                        areaStr, dateStr[:6])
            outputFileName = os.path.join(serverCfg['outputDir'], fileName)

            if not util.check_files_exist(outputFileName,
                                          COMMON_FILES.values()):
                self.plotter.plot(fileName, **params)

            if not util.check_files_exist(outputFileName,
                                          COMMON_FILES.values()):
                response['error'] = \
                    "Requested image is not available at this time."
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
                fileName = self.sstGraph % (self.product['daily'],
                                            mapStr, areaStr, dateStr)
            elif periodStr == 'monthly':
                fileName = self.sstGraph % (self.product['monthly'],
                                            mapStr, areaStr, dateStr[:6])
            elif periodStr == 'yearly':
                fileName = self.aveSstGraph % (self.product['yearly'],
                                               mapStr, areaStr, dateStr[:4])
            elif periodStr == '3monthly':
                fileName = self.aveSstGraph % (self.product['3monthly'],
                                               mapStr, areaStr, dateStr[:6])
            elif periodStr == '6monthly':
                fileName = self.aveSstGraph % (self.product['6monthly'],
                                               mapStr, areaStr, dateStr[:6])
            elif periodStr == '12monthly':
                fileName = self.aveSstGraph % (self.product['12monthly'],
                                               mapStr, areaStr, dateStr[:6])
            elif periodStr == 'weekly':
                fileName = self.aveSstGraph % (self.product['weekly'],
                                               mapStr, areaStr, dateStr)

            outputFileName = os.path.join(serverCfg['outputDir'], fileName)

            if not util.check_files_exist(outputFileName,
                                          COMMON_FILES.values()):
                self.plotter.plot(fileName, **params)

            if not util.check_files_exist(outputFileName,
                                          COMMON_FILES.values()):
                response['error'] = \
                    "Requested image is not available at this time."
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
