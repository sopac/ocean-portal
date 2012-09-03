#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy as np


class branConfig ():
    """ bran configuration
    """

    variableConfig = None

    def __init__(self):
       """Does nothing"""
       self.variableConfig = {"temp": ("Monthly Average BRAN2.1 Temperature ",
                                       {"colorbounds": [-2, 34],
                                        "colormap": plt.cm.jet,
                                        "contourlevels": np.arange(10,31,1),
                                        "unit": ur'\u00b0' + 'C',
                                        "format": '%d'
                                      },
                                      "temp"),
                              "temp_ano": ("Monthly Average BRAN2.1 Temperature Anomaly ",
                                       {"colorbounds": [-1.5, 1.5],
                                        "colormap": plt.cm.RdBu_r,
                                        "contourlevels": np.arange(-1.5,1.5,0.5),
                                        "unit": ur'\u00b0' + 'C',
                                        "format": '%5.1f'
                                      },
                                      "temp"),
                              "temp_dec": ("Monthly Average BRAN2.1 Temperature Deciles",
                                      {"colorbounds": [0, 11],
                                       "colormap": plt.cm.RdBu_r,
                                       "unit": ur'\u00b0' + 'C',
                                       "format": '%d',
                                       "labels": ['Lowest on \nrecord', 'Very much \nbelow \naverage \n[1]', 'Below \naverage \n[2-3]',
                                                  'Average \n[4-7]', 'Above \naverage \n[8-9]', 'Very much \nabove \naverage \n[10]',
                                                  'Highest on \nrecord']
                                      },
                                      "temp_dec"),
                              "salt": ("Monthly Average BRAN2.1 Salinity",
                                       {"colorbounds": [32, 37],
                                        "colormap": plt.cm.jet,
                                        "contourlevels": np.arange(33,37.1,0.5),
                                        "unit": ur'\u00b0' + 'PSU',
                                        "format": '%5.1f'
                                      },
                                      "salt"),
                              "saltanom": ("Monthly Average BRAN2.1 Salinity Anomaly",
                                       {"colorbounds": [-2, 2],
                                        "colormap": plt.cm.RdBu_r,
                                        "unit": ur'\u00b0' + 'PSU',
                                        "format": '%5.1f'
                                      },
                                      "salt_ano"),
                              "salt_dec": ("Monthly Average BRAN2.1 Salinity Deciles",
                                      {"colorbounds": [0, 11],
                                       "colormap": plt.cm.RdBu_r,
                                       "unit": ur'\u00b0' + 'PSU',
                                       "format": '%d',
                                       "labels": ['Lowest on \nrecord', 'Very much \nbelow \naverage \n[1]', 'Below \naverage \n[2-3]',
                                                  'Average \n[4-7]', 'Above \naverage \n[8-9]', 'Very much \nabove \naverage \n[10]',
                                                  'Highest on \nrecord']
                                      },
                                      "salt_dec"),
                              "eta": ("Monthly Average BRAN2.1 Sea Level",
                                       {"colorbounds": [-0.6, 0.6],
                                        "colormap": plt.cm.jet,
                                        "contourlevels": np.arange(-0.6,0.6,0.1),
                                        "unit": ur'\u00b0' + 'M',
                                        "format": '%5.1f'
                                      },
                                      "eta"),
                              "eta_ano": ("Monthly Average BRAN2.1 Sea Level Anomaly",
                                       {"colorbounds": [-2, 2],
                                        "colormap": plt.cm.RdBu_r,
                                        "unit": ur'\u00b0' + 'M',
                                        "format": '%5.1f'
                                      },
                                      "eta_ano"),
                              "eta_dec": ("Monthly Average BRAN2.1 Sea Level Deciles",
                                      {"colorbounds": [0, 11],
                                       "colormap": plt.cm.RdBu_r,
                                       "unit": ur'\u00b0' + 'M',
                                       "format": '%d',
                                       "labels": ['Lowest on \nrecord', 'Very much \nbelow \naverage \n[1]', 'Below \naverage \n[2-3]',
                                                  'Average \n[4-7]', 'Above \naverage \n[8-9]', 'Very much \nabove \naverage \n[10]',
                                                  'Highest on \nrecord']
                                      },
                                      "eta_dec"),
                              "currents": ("Monthly Average BRAN2.1 Currents",
                                       {"colorbounds": [-1, 1],
                                        "colormap": plt.cm.jet,
                                        "unit": ur'\u00b0' + 'M/s',
                                        "format": '%5.1f'
                                      },
                                      "uv"),
                             }


    def getTitle(self, variableName):
        return self.variableConfig[variableName][0]

    def getColorBounds(self, variableName):
        return self.variableConfig[variableName][1]['colorbounds']

    def getColorMap(self, variableName):
        return self.variableConfig[variableName][1]['colormap']

    def getContourLevels(self, variableName):
        return self.variableConfig[variableName][1]['contourlevels'] 

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
    conf = branConfig()
    conf.getTitle('mean')
    conf.getColorBounds('mean')
    conf.getColorMap('mean')
    conf.getUnit('mean')
    conf.getValueFormat('mean')

