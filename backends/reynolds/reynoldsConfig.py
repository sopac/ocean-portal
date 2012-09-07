#!/usr/bin/python
#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

import matplotlib.pyplot as plt


class ReynoldsConfig ():
    """ Reynolds configuration
    """

    variableConfig = None
    periodPrefix = None
    subDirs = None

    def __init__(self):
        self.variableConfig = {"mean": ("Average Reynolds Sea Surface Temperature: ",
                                        {"colorbounds": [-2, 34],
                                         "colormap": plt.cm.jet,
                                         "unit": ur'\u00b0' + 'C',
                                         "format": '%d'
                                       },
                                       "sst"),
                               "anom": ("Average Reynolds Sea Surface Temperature Anomaly: ",
                                        {"colorbounds": [-2, 2],
                                         "colormap": plt.cm.RdBu_r,
                                         "unit": ur'\u00b0' + 'C',
                                         "format": '%5.1f'
                                       },
                                       "anom"),
                               "dec": ("Average Reynolds Sea Surface Temperature Deciles: ",
                                       {"colorbounds": [0, 11],
                                        "colormap": plt.cm.RdBu_r,
                                        "unit": '',
                                        "format": '%d',
                                        "labels": ['Lowest on \nrecord', 'Very much \nbelow \naverage \n[1]', 'Below \naverage \n[2-3]',
                                                   'Average \n[4-7]', 'Above \naverage \n[8-9]', 'Very much \nabove \naverage \n[10]',
                                                   'Highest on \nrecord']
                                       },
                                       "decile")
                              }

        self.periodPrefix = {'daily': "Daily ",
                             'monthly': "Monthly ",
                             '3monthly': "3 Monthly ",
                             '6monthly': "6 Monthly ",
                             '12monthly': "12 Monthly ",
                             'yearly': "Yearly ",
                            }

        self.subDirs = ['daily',
                        # 'weekly',
                        'monthly',
                        # '3monthly',
                        # '6monthly',
                        'yearly',
                        # 'yearly_trend',
                        'decile',
                       ]

    def getTitle(self, variableName):
        return self.variableConfig[variableName][0]

    def getColorBounds(self, variableName):
        return self.variableConfig[variableName][1]['colorbounds']

    def getColorMap(self, variableName):
        return self.variableConfig[variableName][1]['colormap']

    def getUnit(self, variableName):
        return self.variableConfig[variableName][1]['unit']

    def getValueFormat(self, variableName):
        return self.variableConfig[variableName][1]['format']

    def getVariableType(self, variableName):
        return self.variableConfig[variableName][2]

    def getColorbarLabels(self, variableName):
        labels = []
        try:
            labels = self.variableConfig[variableName][1]['labels']
        except:
            pass
        return labels

    def getPeriodPrefix(self, period):
        return self.periodPrefix[period]

if __name__ == "__main__":
    conf = RyenoldsConfig()
    conf.getTitle('mean')
    conf.getColorBounds('mean')
    conf.getColorMap('mean')
    conf.getUnit('mean')
    conf.getValueFormat('mean')

