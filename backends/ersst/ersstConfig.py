#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np


class ErsstConfig ():
    """ Ersst configuration
    """

    variableConfig = None

    periodPrefix = None

    def __init__(self):
        self.variableConfig = {"mean": ("ER Sea Surface Temperature: ",
                                        {"colorbounds": [-2, 34],
                                         "colormap": plt.cm.jet,
                                         "contourlevels": np.arange(-2,36,2),
                                         "unit": ur'\u00b0' + 'C',
                                         "format": '%d'
                                       },
                                       "sst"),
                               "anom": ("ER Sea Surface Temperature Anomaly: ",
                                        {"colorbounds": [-3, 3],
                                         "colormap": plt.cm.RdBu_r,
                                         "contourlevels": np.arange(-3, 3.5,0.5),
                                         "unit": ur'\u00b0' + 'C',
                                         "format": '%5.1f'
                                       },
                                       "anom"),
                               "dec": ("ER Sea Surface Temperature Decile: ",
                                        {"colorbounds": [0,11],
                                         "colormap": plt.cm.RdBu_r,
                                         "contourlevels": [-1,0,1,3,7,9,10,11],
                                         "colorbarlabels": ['Lowest on \nrecord','Very much \nbelow \naverage \n[1]',
                                         'Below \naverage \n[2-3]','Average \n[4-7]','Above \naverage \n[8-9]',
                                         'Very much \nabove \naverage \n[10]','Highest on \nrecord'],
                                         "unit": ur'\u00b0' + 'C',
                                         "format": '%5.1f'
                                       },
                                       "decile"),
                               "trend": ("ER Sea Surface Temperature Trend: ",
                                        {"colorbounds": [-0.28,0.28],
                                         "colormap": plt.cm.RdBu_r,
                                         "contourlevels": np.arange(-0.28,0.32,0.04),
                                         "unit": ur'\u00b0' + 'C/Decade',
                                         "format": '%5.2f'
                                      },
                                      "linear_trend")
                              }
        self.periodPrefix = {"monthly": "Monthly Average ",
                             "3monthly": "3 Monthly Average ",
                             "6monthly": "6 Monthly Average ",
                             "12monthly": "12 Monthly Average "
                             }

        self.subDirs = ['12monthly',
                        '6monthly',
                        'decile',
                        'trend',
                        'yearly_trend',
                        '3monthly',
                        'averages',
                        'monthly',
                        'yearly'
                       ]

    def getTitle(self, variableName):
        return self.variableConfig[variableName][0]
    
    def getColorBounds(self, variableName):
        return self.variableConfig[variableName][1]['colorbounds']

    def getColorMap(self, variableName):
        return self.variableConfig[variableName][1]['colormap']

    def getContourLevels(self, variableName):
        return self.variableConfig[variableName][1]['contourlevels']

    def getColorbarLabels(self, variableName):
        colorbarlabels = []
        try:
            colorbarlabels = self.variableConfig[variableName][1]['colorbarlabels']        
        except KeyError: 
            pass
        return colorbarlabels

    def getUnit(self, variableName):
        return self.variableConfig[variableName][1]['unit']

    def getValueFormat(self, variableName):
        return self.variableConfig[variableName][1]['format']
 
    def getVariableType(self, variableName):
        return self.variableConfig[variableName][2]

    def getPeriodPrefix(self, period):
        return self.periodPrefix[period]

if __name__ == "__main__":
    conf = ErsstConfig()
    conf.getTitle('mean')
    conf.getColorBounds('mean')
    conf.getContourLevels('mean')
    conf.getColorbarLabels('mean')
    conf.getColorMap('mean')
    conf.getUnit('mean')
    conf.getValueFormat('mean')


