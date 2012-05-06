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
                                      "anom")
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


if __name__ == "__main__":
    conf = RyenoldsConfig()
    conf.getTitle('mean')
    conf.getColorBounds('mean')
    conf.getColorMap('mean')
    conf.getUnit('mean')
    conf.getValueFormat('mean')

