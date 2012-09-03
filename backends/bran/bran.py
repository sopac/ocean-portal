import os
import os.path
import sys
import json
import datetime
import numpy as np

from ..netcdf import plotter
import branPlotterNew
from ..util import productName
import ocean.util as util
from ..util import regionConfig
import branConfig as bc
from ocean.netcdf.plotter import COMMON_FILES

#Maybe move these into configuration later
branGraph = "%s_%s_%s_%s"
branGraph2 = "%s_%s_%s_%s_depthprf_%s"

server_config = util.get_server_config()

#get dataset dependant production information
branProduct = productName.products["bran"]


def process(form):
    responseObj = {}
    
    if ("map" in form) and ("date" in form) and ("period" in form) and ("lat" in form) and ("lon" in form):
        varName = form["map"].value
        dateStr = form["date"].value
        regionStr = form["area"].value
        periodStr = form["period"].value
        lat_cnt = np.float(form["lat"].value)
        lon_cnt = np.float(form["lon"].value)
        periodStr = form["period"].value
        year = dateStr[0:4]
        month = dateStr[4:6]

        if (periodStr == 'monthly') & (varName in ['temp', 'salt']):
            
            outputFilename = branGraph % (branProduct["monthly"], varName, regionStr, dateStr[:6])
            outputFileFullPath = os.path.join(server_config['outputDir'], outputFilename)

            if lat_cnt >= 0:
                lat_str = str(int(round(abs(lat_cnt), 2)*100)) + 'N'
            else:
                lat_str = str(int(round(abs(lat_cnt), 2)*100)) + 'S'
            lon_str = str(int(round(lon_cnt, 2)*100)) + 'E'
            loc_str = lat_str + lon_str

            outputFilename2 = branGraph2 % (branProduct["monthly"], varName, regionStr, dateStr[:6], loc_str)
            outputFileFullPath2 = os.path.join(server_config['outputDir'], outputFilename2)
            
            if not util.check_files_exist(outputFileFullPath, COMMON_FILES.values()):
                draw_monthly_mean_surface_plot(varName, dateStr, regionStr, outputFilename, outputFileFullPath)
                           
            if varName == 'temp':
                unitStr = 'Degrees Celsius'
                varLongName = 'Subsurface Temperature Profile\n'
                cb_ticks = np.arange(16.0, 30.1, 1.0)
            elif varName == 'salt':
                unitStr = 'PSU'
                varLongName = 'Subsurface Salinity Profile\n'
                cb_ticks = np.arange(33, 37.1, 0.5)

            title_date_str = datetime.date(int(year), int(month), 1).strftime('%B %Y')
            titleStr = title_date_str + ': ' + varLongName
            
            input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', varName, varName + '_' + year + '_' + month + '.nc4')
        
            lats1, lons1, zlevels1, zonal_data = branPlotterNew.load_BRAN_data(input_data_file, varName, lat_cnt, lat_cnt, lon_cnt - 5.0, lon_cnt + 5.0, depth_min=0.0, depth_max=300.0)
            lats2, lons2, zlevels2, meridional_data = branPlotterNew.load_BRAN_data(input_data_file, varName, lat_cnt - 5.0, lat_cnt + 5.0, lon_cnt, lon_cnt, depth_min=0.0, depth_max=300.0)
            branPlotterNew.plot_BRAN_depth_slice(zlevels1, lats2, lons1, zonal_data, meridional_data, output_filename=outputFileFullPath2 + '.png',
                                                 units=unitStr, title=titleStr, cb_ticks=cb_ticks, product_label_str='Bluelink Reanalysis 2.1')
                
            if not util.check_files_exist(outputFileFullPath, COMMON_FILES.values()):
                responseObj["error"] = "Requested image is not available at this time."
            else:
                responseObj.update(util.build_response_object(
                        COMMON_FILES.keys(),
                        os.path.join(server_config['baseURL'],
                                     server_config['rasterURL'],
                                     outputFilename),
                        COMMON_FILES.values()))
                responseObj["img"] = os.path.join(server_config['baseURL'], server_config['rasterURL'], outputFilename2 + '.png')

    elif ("map" in form) and ("date" in form) and ("period" in form) and ("area" in form):
        varName = form["map"].value
        dateStr = form["date"].value
        regionStr = form["area"].value
        periodStr = form["period"].value

        if (periodStr == 'monthly') & (varName in ['temp', 'salt', 'eta', 'uvtemp', 'uveta']):
           
            outputFilename = branGraph % (branProduct["monthly"], varName, regionStr, dateStr[:6])
            outputFileFullPath = os.path.join(server_config['outputDir'],
                                              outputFilename)
            
            if not util.check_files_exist(outputFileFullPath, COMMON_FILES.values()):
                draw_monthly_mean_surface_plot(varName, dateStr, regionStr, outputFilename, outputFileFullPath)

            if not util.check_files_exist(outputFileFullPath, COMMON_FILES.values()):
                responseObj["error"] = "Requested image is not available at this time."
            else:
                responseObj.update(util.build_response_object(
                        COMMON_FILES.keys(),
                        os.path.join(server_config['baseURL'],
                                     server_config['rasterURL'],
                                     outputFilename),
                        COMMON_FILES.values()))
    response = json.dumps(responseObj)
    return response
    
    

def draw_monthly_mean_surface_plot(varName, dateStr, regionStr, outputFilename, outputFileFullPath):

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
        varLongName = 'Sea Level Height'
        cb_tick_fmt="%.2f"
    elif varName == 'uveta':
        dataVar = 'eta'
        unitStr = 'Metres'
        cb_ticks = np.arange(-0.5,0.51,0.1)
        varLongName = 'Sea Level Height and Currents'
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

    input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', dataVar, dataVar + '_' + year + '_' + month + '.nc4')
    lats, lons, zlevels, data = branPlotterNew.load_BRAN_data(input_data_file, dataVar, lat_min - 1.0, lat_max + 1.0, lon_min - 1.0, lon_max + 1.0)

    if currents == True:
        input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', 'u', 'u' + '_' + year + '_' + month + '.nc4')
        lats2, lons2, zlevels, u = branPlotterNew.load_BRAN_data(input_data_file, 'u', lat_min - 1.0, lat_max + 1.0, lon_min - 1.0, lon_max + 1.0)
        input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', 'v', 'v' + '_' + year + '_' + month + '.nc4')
        lats2, lons2, zlevels, v = branPlotterNew.load_BRAN_data(input_data_file, 'v', lat_min - 1.0, lat_max + 1.0, lon_min - 1.0, lon_max + 1.0)
        contourLines=False
    else:
        lats2 = None; lons2 = None
        u = None; v = None
        contourLines = True
    
    config = bc.branConfig()
    plot = plotter.Plotter()
    plot.contourBasemapEast(data, lats, lons, dataVar, config, outputFilename)
    plot.contourBasemapWest(data, lats, lons, dataVar, config, outputFilename)
    plot.plotScale(data, dataVar, config, outputFilename)
    branPlotterNew.plot_BRAN_surface_data(lats, lons, data, lat_min, lat_max, lon_min, lon_max,
                                          output_filename=outputFileFullPath + '.png', title=title, units=unitStr,
                                          cb_ticks=cb_ticks, cb_tick_fmt=cb_tick_fmt, cmp_name='jet', proj='cyl',
                                          contourLines=contourLines, product_label_str='Bluelink Reanalysis 2.1',
                                          vlat=lats2, vlon=lons2, u=u, v=v)
