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
from ocean.plotter import COMMON_FILES
from ocean.util import areaMean
from ocean.config import productName

serverCfg = config.get_server_config()

class SST(Dataset):
    """
    Base class for SST datasets.

    At a minimum dataset class must define:

    class mydataset(SST):
        DATASET = 'mydataset'
        PLOTTER = MyDatasetPlotter
    """

    __form_params__ = {
        'average': bool,
        'trend': bool,
        'runningInterval': int,
        'baseYear': int,
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
        'trend',
    ]

    __plots__ = [
        'map',
    ]

    apply_to = util.Parameterise(Dataset)

    @property
    def CACHE_URL(self):
        return os.path.join(serverCfg['baseURL'],
                            serverCfg['rasterURL'],
                            serverCfg['cacheDir'][self.DATASET])

    def __init__(self):
        self.product = productName.products[self.DATASET]
        self.plotter = self.PLOTTER()

    @apply_to()
    def get_filename_format(self, params={}):
        return '%(product_name)s_%(area)s_%(formatted_date)s_%(variable)s'

    @apply_to(variable='trend')
    def get_filename_format(self, params={}):
        return '%(product_name)s_%(area)s_%(formatted_date)s_%(variable)s_%(baseYear)s'

    def get_product_name(self, params):

        suffix = {
            'dec': 'Dec',
            'trend': 'Tre',
        }

        key = '%s%s' % (params['period'], suffix.get(params['variable'], ''))
        return self.product[key]

    def get_date_format(self, params={}):
        formatted_date = ''
        format = {
            'daily': '{0.year:4d}{0.month:02d}{0.day:02d}',
            'weekly': '{0.year:4d}{0.month:02d}{0.day:02d}',
            '4weeks': '{0.year:4d}{0.month:02d}{0.day:02d}',
            '8weeks': '{0.year:4d}{0.month:02d}{0.day:02d}',
            '12weeks': '{0.year:4d}{0.month:02d}{0.day:02d}',
            'monthly': '{0.year:4d}{0.month:02d}',
            '3monthly': '{0.year:4d}{0.month:02d}',
            '6monthly': '{0.year:4d}{0.month:02d}',
            '12monthly': '{0.year:4d}{0.month:02d}',
            'yearly': '{0.year:4d}',
        }
        if params['variable'] == 'trend':
            if params['period'] == 'yearly':
                formatted_date = 'annual'
            else:
                formatted_date = '{0.month:02d}'.format(params['date'])
        else:
            formatted_date = format[params['period']].format(params['date'])
        return formatted_date

    def process_stats(self, params):
        return {} 

    def process(self, params):
        response = {}

        p = params.copy()
        p.update({
            'product_name': self.get_product_name(params=params),
            'formatted_date': self.get_date_format(params=params),
        })

        fileName = self.get_filename_format(params=params) % p
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

        response.update(self.process_stats(params))
        return response
