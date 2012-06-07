"""
Product ID lookup table

Author: Sheng Guo
(c)Climate and Oceans Support Program for the Pacific(COSPPAC), Bureau of Meteorology, Australia
"""

products = {"reynolds": {"daily":     "REY00001",
                         "monthly":   "REY00002",
                         "yearly":    "REY00003",
                         "3monthly":  "REY00004",
                         "6monthly":  "REY00005",
                         "weekly":    "REY00006",
                         "yearlyAve": "REY00101",
                         "monthlyAve":"REY00102",
                         "monthlyDec":"REY00201"
                        },
            "ersst": {"monthly":       "ERA00001", 
		      "3monthly":      "ERA00002",
		      "6monthly":      "ERA00003",
		      "12monthly":     "ERA00004",
		      "monthlyAve":    "ERA00101",
		      "3monthlyAve":   "ERA00102",
		      "6monthlyAve":   "ERA00103",
		      "12monthlyAve":  "ERA00104",
		      "monthlyDec":    "ERA00201",# Decile ID
                      "3monthlyDec":   "ERA00202",
                      "6monthlyDec":   "ERA00203",
                      "12monthlyDec":  "ERA00204",
		      "monthlyTre":    "ERA00301",# Trend ID
                      "3monthlyTre":   "ERA00302",
                      "6monthlyTre":   "ERA00303",
                      "12monthlyTre":  "ERA00304"
                     },
            "bran": {
                    },
            "ww3": {"point":  "WAV00001",
                    "rect": "WAV00002"
                   },
            "sealevel": {"point": "SEA00001",
                         "monthly": "SEA00002"
                        }
}

