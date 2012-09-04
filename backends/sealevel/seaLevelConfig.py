#!/usr/bin/python

import matplotlib.pyplot as plt


class SeaLevelConfig ():
    """ Reynolds configuration
    """

    variableConfig = None

    def __init__(self):
        """Does nothing"""
        self.variableConfig = {"alt": ("Sea level Altimetry: ",
                                      {"colorbounds": [-300, 300],
                                       "colormap": plt.cm.RdYlBu_r,
                                       "unit": 'mm',
                                       "format": '%d'
                                      },
                                       "height"),
                               "rec": ("Sea level Reconstruction: ",
                                      {"colorbounds": [-300, 300],
                                       "colormap": plt.cm.RdYlBu_r,
                                       "unit": 'mm',
                                       "format": '%d'
                                      },
                                       "height")
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
    conf.getTitle('alt')
    conf.getColorBounds('alt')
    conf.getColorMap('alt')
    conf.getUnit('alt')
    conf.getValueFormat('alt')

