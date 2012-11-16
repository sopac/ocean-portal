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

    def process_average(self, params):

        response = {}

        mapStr = params['variable']
        dateStr = params['date'].strftime('%Y%m%d')
        areaStr = params['area']
        periodStr = params['period']

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

    def get_filename_format(self, params):
        format = {
            'mean': '%s_%s_%s_mean',
            'dec': '%s_%s_%s_dec',
            'anom': '%s_%s_%s_anom',
        }

        return format[params['variable']]

    def get_product_name(self, params):

        suffix = {
            'dec': 'Dec',
        }

        key = '%s%s' % (params['period'], suffix.get(params['variable'], ''))
        return self.product[key]

    def get_date_format(self, params):
        format = {
            'daily': '%Y%m%d',
            'weekly': '%Y%m%d',
            'monthly': '%Y%m',
            '3monthly': '%Y%m',
            '6monthly': '%Y%m',
            '12monthly': '%Y%m',
            'yearly': '%Y',
        }

        return params['date'].strftime(format[params['period']])

    def process(self, params):
        response = {}

        if params.get('average', False): # averages
            response.update(self.process_average(self, params))
        else:

            fileName = self.get_filename_format(params) % (
                self.get_product_name(params),
                params['area'],
                self.get_date_format(params))
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
