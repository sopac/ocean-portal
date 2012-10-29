#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>

regions = {
    'cook': ('pac',
           {'llcrnrlat': -23,
            'llcrnrlon': 193,
            'urcrnrlat': -8,
            'urcrnrlon': 203
           },
           "Cook Islands",
           {}),
    'fsm': ('pac',
           {'llcrnrlat': 5,
            'llcrnrlon': 150,
            'urcrnrlat': 11,
            'urcrnrlon': 164
           },
           "Federated States of Micronesia",
           {}),
    'fiji': ('pac',
           {'llcrnrlat': -20,
            'llcrnrlon': 176.5,
            'urcrnrlat': -15,
            'urcrnrlon': 183
           },
           "Fiji",
           {}),
    'kiribati': ('pac',
           {'llcrnrlat': -12,
            'llcrnrlon': 169,
            'urcrnrlat': 5,
            'urcrnrlon': 210
           },
           "Kiribati",
           {}),
    'marshall': ('pac',
           {'llcrnrlat': 4,
            'llcrnrlon': 160,
            'urcrnrlat': 16,
            'urcrnrlon': 173
           },
           "Marshall Islands",
           {}),
    'nauru': ('pac',
           {'llcrnrlat': -1,
            'llcrnrlon': 166,
            'urcrnrlat': 0,
            'urcrnrlon': 168
           },
           "Nauru",
           {}),
    'niue': ('pac',
           {'llcrnrlat': -20,
            'llcrnrlon': 189,
            'urcrnrlat': -18,
            'urcrnrlon': 191
           },
           "Niue",
           {}),
    'palau': ('pac',
           {'llcrnrlat': 2,
            'llcrnrlon': 131,
            'urcrnrlat': 9,
            'urcrnrlon': 135
           },
           "Palau",
           {}),
    'png': ('pac',
           {'llcrnrlat': -12,
            'llcrnrlon': 128,
            'urcrnrlat': 1,
            'urcrnrlon': 160
           },
           "Papua New Guinea",
           {}),
    'samoa': ('pac',
           {'llcrnrlat': -15,
            'llcrnrlon': 186.5,
            'urcrnrlat': -12,
            'urcrnrlon': 189
           },
           "Samoa",
           {}),
    'wsm_nor': ('pac',                     #Samoa Northern Coast. wsm is the ISO code of Samoa
           {'llcrnrlat': -14,
            'llcrnrlon': 186.5,
            'urcrnrlat': -12,
            'urcrnrlon': 189
           },
           "Samoa Northern Coast",
           {}),
    'wsm_sou': ('pac',                     #Samoa Southern Coast
           {'llcrnrlat': -15,
            'llcrnrlon': 186.5,
            'urcrnrlat': -13.3,
            'urcrnrlon': 189
           },
           "Samoa Southern Coast",
           {}),
    'solomon': ('pac',
           {'llcrnrlat': -12,
            'llcrnrlon': 155,
            'urcrnrlat': -4.8,
            'urcrnrlon': 168
           },
           "Solomon Islands",
           {}),
    'tonga': ('pac',
           {'llcrnrlat': -22,
            'llcrnrlon': 184,
            'urcrnrlat': -15,
            'urcrnrlon': 190
           },
           "Tonga",
           {}),
    'tuvalu': ('pac',
           {'llcrnrlat': -11,
            'llcrnrlon': 177,
            'urcrnrlat': -7,
            'urcrnrlon': 180
           },
           "Tuvalu",
           {}),
    'vanuatu': ('pac',
           {'llcrnrlat': -21,
            'llcrnrlon': 166,
            'urcrnrlat': -13,
            'urcrnrlon': 170
           },
           "Vanuatu",
           {}),
    'aus': ('aus',
           {'llcrnrlat': -50,
            'llcrnrlon': 60,
            'urcrnrlat': 20,
            'urcrnrlon': 170
           },
           "Australia",
           {}),
    'pac': (None,
           {'llcrnrlat': -45,
            'llcrnrlon': 100,
            'urcrnrlat': 45,
            'urcrnrlon': 300
           },
           "Pacific Ocean",
           {}),
    'ind': ('aus',
           {'llcrnrlat': -45,
            'llcrnrlon': 20,
            'urcrnrlat': 45,
            'urcrnrlon': 160
           },
           "Indian Ocean",
           {}),
    'ntr': ('aus',
           {'llcrnrlat': -22,
            'llcrnrlon': 94,
            'urcrnrlat': 0,
            'urcrnrlon': 174
           },
           "Northern Tropics",
           {}),
    'sth': ('aus',
           {'llcrnrlat': -50,
            'llcrnrlon': 94,
            'urcrnrlat': -30,
            'urcrnrlon': 174
           },
           "Southern Region",
           {}),
    'tas': ('aus',
           {'llcrnrlat': -46,
            'llcrnrlon': 150,
            'urcrnrlat': -26,
            'urcrnrlon': 174
           },
           "Tasman Sea",
           {}),
    'cor': ('aus',
           {'llcrnrlat': -26,
            'llcrnrlon': 142,
            'urcrnrlat': -4,
            'urcrnrlon': 174
           },
           "Coral Sea",
           {}),
    'nws': ('aus',
           {'llcrnrlat': -22,
            'llcrnrlon': 94,
            'urcrnrlat': -4,
            'urcrnrlon': 130
           },
           "North West Shelf",
           {}),
    'swr': ('aus',
           {'llcrnrlat': -46,
            'llcrnrlon': 94,
            'urcrnrlat': -22,
            'urcrnrlon': 116
           },
           "South West Region",
           {}),
    'eca': ('aus',
           {'llcrnrlat': -50,
            'llcrnrlon': 140,
            'urcrnrlat': 0,
            'urcrnrlon': 180
           },
           "East Australian Coast",
           {}),
    'wca': ('aus',
           {'llcrnrlat': -50,
            'llcrnrlon': 90,
            'urcrnrlat': 0,
            'urcrnrlon': 130
           },
           "West Australian Coast",
           {}),
    'qld': ('aus',
           {'llcrnrlat': -29.0,
            'llcrnrlon': 136,
            'urcrnrlat': -9.0,
            'urcrnrlon': 160
           },
           "Queensland / Coral Sea",
           {}),
    'nsw': ('aus',
           {'llcrnrlat': -39,
            'llcrnrlon': 147,
            'urcrnrlat': -27,
            'urcrnrlon': 160
           },
           "N.S.W. Coast",
           {}),
    'seaus': ('aus',
           {'llcrnrlat': -46,
            'llcrnrlon': 139,
            'urcrnrlat': -37,
            'urcrnrlon': 151
           },
           "Victoria / Tasmania",
           {}),
    'sa': ('aus',
           {'llcrnrlat': -40.3,
            'llcrnrlon': 128.6,
            'urcrnrlat': -30.5,
            'urcrnrlon': 141.5
           },
           "S.A. / Great Australian Bight",
           {}),
    'nt': ('aus',
           {'llcrnrlat': -16.5,
            'llcrnrlon': 127,
            'urcrnrlat': -7.5,
            'urcrnrlon': 140
           },
           "Northern Territory",
           {}),
    'nwa': ('aus',
           {'llcrnrlat': -23,
            'llcrnrlon': 108,
            'urcrnrlat': -10,
            'urcrnrlon': 131
           },
           "North Western Australia",
           {}),
    'swa': ('aus',
           {'llcrnrlat': -39,
            'llcrnrlon': 108,
            'urcrnrlat': -22,
            'urcrnrlon': 131
           },
           "South Western Australia",
           {}),
    'christmas': ('aus',
           {'llcrnrlat': -13.1,
            'llcrnrlon': 102.8,
            'urcrnrlat': -7.8,
            'urcrnrlon': 109
           },
           "Christmas Island",
           {}),
    'cocos': ('aus',
           {'llcrnrlat': -15,
            'llcrnrlon': 93.7,
            'urcrnrlat': -9,
            'urcrnrlon': 99.7
           },
           "Cocos (Keeling) Island",
           {}),
    'lordhowe': ('aus',
           {'llcrnrlat': -34,
            'llcrnrlon': 156,
            'urcrnrlat': -28.5,
            'urcrnrlon': 162
           },
           "Lord Howe Island",
           {}),
    'norfolk': ('aus',
           {'llcrnrlat': -32,
            'llcrnrlon': 165,
            'urcrnrlat': -26,
            'urcrnrlon': 171
           },
           "Norfolk Island",
           {}),
    'macquarie': ('aus',
           {'llcrnrlat': -57,
            'llcrnrlon': 156,
            'urcrnrlat': -52,
            'urcrnrlon': 162
           },
           "Macquarie Island",
           {}),
}