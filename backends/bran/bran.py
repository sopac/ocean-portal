import os
import sys
import json
import datetime
import numpy as np

import branPlotterNew
from ..util import productName
import ocean.util as util
from ..util import regionConfig

#Maybe move these into configuration later
branGraph = "%s_%s_%s_%s"

#get dataset dependant production information
branProduct = productName.products["bran"]


def process(form):
    responseObj = {} #this object will be encoded into a json string

    if ("map" in form) and ("date" in form) and ("period" in form) and ("area" in form):
        varName = form["map"].value
        dateStr = form["date"].value
        regionStr = form["area"].value
        periodStr = form["period"].value

        if (periodStr == 'monthly') & (varName in ['temp', 'salt', 'eta', 'uvtemp', 'uveta']):
           
            outputFilename = branGraph % (branProduct["monthly"], varName, regionStr, dateStr[:6]) + '.png'
            outputFileFullPath = util.get_server_config()["outputDir"] + outputFilename
            
            if not os.path.exists(outputFileFullPath):
                year = dateStr[0:4]
                month = dateStr[4:6]
                title_date_str = datetime.date(int(year), int(month), 1).strftime('%B %Y')
                regionLongName = regionConfig.regions[regionStr][2]
                currents = False
                
                if varName == 'temp':
                    dataVar = 'temp'
                    unitStr = 'Degrees Celsius'
                    if regionConfig.regions[regionStr][0] == 'pi':
                        cb_ticks = np.arange(20.0,32.1,1.0)
                    else:
                        cb_ticks = np.arange(0.0,32.1,2.0)
                    varLongName = 'Surface Temperature'
                    cb_tick_fmt="%.0f"
                elif varName == 'uvtemp':
                    dataVar = 'temp'
                    unitStr = 'Degrees Celsius'
                    if regionConfig.regions[regionStr][0] == 'pi':
                        cb_ticks = np.arange(20.0,32.1,1.0)
                    else:
                        cb_ticks = np.arange(0.0,32.1,2.0)
                    varLongName = 'Surface Temperature and Currents'
                    cb_tick_fmt="%.0f"
                    currents = True
                elif varName == 'salt':
                    dataVar = 'salt'
                    unitStr = 'PSU'
                    cb_ticks = np.arange(33,37.1,0.5)
                    varLongName = 'Sea Surface Salinity'
                    cb_tick_fmt="%.1f"
                elif varName == 'eta':
                    dataVar = 'eta'
                    unitStr = 'Metres'
                    cb_ticks = np.arange(-0.5,0.51,0.1)
                    varLongName = 'Sea Level Anomaly'
                    cb_tick_fmt="%.2f"
                elif varName == 'uveta':
                    dataVar = 'eta'
                    unitStr = 'Metres'
                    cb_ticks = np.arange(-0.5,0.51,0.1)
                    varLongName = 'Sea Level Anomaly and Currents'
                    cb_tick_fmt="%.2f"
                    currents = True
                else:
                    dataVar = varName
                    unitStr = ''
                    cb_ticks = None
                    varLongName = ''
                    cb_tick_fmt="%.1f"
                                
                title = regionLongName + '\n' + title_date_str + ': ' + varLongName
                
                lat_min = regionConfig.regions[regionStr][1]['llcrnrlat']
                lat_max = regionConfig.regions[regionStr][1]['urcrnrlat']
                lon_min = regionConfig.regions[regionStr][1]['llcrnrlon']
                lon_max = regionConfig.regions[regionStr][1]['urcrnrlon']

                input_data_file = os.path.join(util.get_server_config()['dataDir']['bran'], 'monthly', dataVar, dataVar + '_' + year + '_' + month + '.nc4')
                lats, lons, zlevels, data = branPlotterNew.load_BRAN_data(input_data_file, dataVar, lat_min - 1.0, lat_max + 1.0, lon_min - 1.0, lon_max + 1.0)

                if currents == True:
                    input_data_file = os.path.join(util.get_server_config()['dataDir']['bran'], 'monthly', 'u', 'u' + '_' + year + '_' + month + '.nc4')
                    lats2, lons2, zlevels, u = branPlotterNew.load_BRAN_data(input_data_file, 'u', lat_min - 1.0, lat_max + 1.0, lon_min - 1.0, lon_max + 1.0)
                    input_data_file = os.path.join(util.get_server_config()['dataDir']['bran'], 'monthly', 'v', 'v' + '_' + year + '_' + month + '.nc4')
                    lats2, lons2, zlevels, v = branPlotterNew.load_BRAN_data(input_data_file, 'v', lat_min - 1.0, lat_max + 1.0, lon_min - 1.0, lon_max + 1.0)
                    contourLines=False
                else:
                    lats2 = None; lons2 = None
                    u = None; v = None
                    contourLines = True
                
                branPlotterNew.plot_BRAN_surface_data(lats, lons, data, lat_min, lat_max, lon_min, lon_max,
                                                      output_filename=outputFileFullPath, title=title, units=unitStr,
                                                      cb_ticks=cb_ticks, cb_tick_fmt=cb_tick_fmt, cmp_name='jet', proj='cyl',
                                                      contourLines=contourLines, product_label_str='Bluelink Reanalysis 2.1',
                                                      vlat=lats2, vlon=lons2, u=u, v=v)

            if not os.path.exists(outputFileFullPath):
                responseObj["error"] = "Requested image is not available at this time."
            else:
                responseObj["img"] = util.get_server_config()['baseURL'] + outputFileFullPath

    response = json.dumps(responseObj)
    return response

