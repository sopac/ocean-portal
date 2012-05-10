#!/usr/bin/python

import matplotlib.pyplot as plt


class ReynoldsConfig ():
    """ Reynolds configuration
    """

    variableConfig = None

    def __init__(self):
       """Does nothing"""
       self.variableConfig = {"mean": ("Monthly Average Reynolds Sea Surface Temperature", 
                                       {"colorbounds": [-2, 34],
                                        "colormap": plt.cm.jet,
                                        "unit": ur'\u00b0' + 'C',
                                        "format": '%d'
                                      },
                                      "sst"),
                              "anom": ("Monthly Average Reynolds Sea Surface Temperature Anomaly",
                                       {"colorbounds": [-2, 2],
                                        "colormap": plt.cm.RdBu_r,
                                        "unit": ur'\u00b0' + 'C',
                                        "format": '%5.1f'
                                      },
                                      "anom"),
                              "dec": ("Monthly Average Reynolds Sea Surface Temperature Deciles",
                                      {"colorbounds": [0, 11],
                                       "colormap": plt.cm.RdBu_r,
                                       "unit": ur'\u00b0' + 'C',
                                       "format": '%d',
                                       "labels": ['Lowest on \nrecord', 'Very much \nbelow \naverage \n[1]', 'Below \naverage \n[2-3]', 
                                                  'Average \n[4-7]', 'Above \naverage \n[8-9]', 'Very much \nabove \naverage \n[10]',
                                                  'Highest on \nrecord']
                                      }, 
                                      "decile")
                             }


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


if __name__ == "__main__":
    conf = RyenoldsConfig()
    conf.getTitle('mean')
    conf.getColorBounds('mean')
    conf.getColorMap('mean')
    conf.getUnit('mean')
    conf.getValueFormat('mean')

