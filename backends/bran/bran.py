import os
import os.path
import sys
import datetime
import numpy as np

from ..netcdf import plotter
import branPlotterNew
from ..util import productName
import ocean.util as util
from ..util import regionConfig
import branConfig as bc
from ocean.netcdf.plotter import COMMON_FILES

server_config = util.get_server_config()
branProduct = productName.products["bran"]


def process(form):
    responseObj = {}
    
    if ("map" in form) and ("date" in form) and ("period" in form) and ("area" in form):
        
        varName = form["map"].value
        dateStr = form["date"].value
        regionStr = form["area"].value
        periodStr = form["period"].value
        yearStr = dateStr[0:4]
        year = int(yearStr)
        monthStr = dateStr[4:6]
        month = int(monthStr)
        yearMonthStr = dateStr[0:6]
        
        if ("lat" in form) and ("lon" in form):
            lat_cnt = np.float(form["lat"].value)
            lon_cnt = np.mod(np.float(form["lon"].value),360.0)
            if (lon_cnt >= 0) & (lon_cnt <= 360) & (lat_cnt >= -90) & (lat_cnt <= 90):
                if lat_cnt >= 0:
                    lat_str = str(int(round(abs(lat_cnt), 2)*100)) + 'N'
                else:
                    lat_str = str(int(round(abs(lat_cnt), 2)*100)) + 'S'
                lon_str = str(int(round(lon_cnt, 2)*100)) + 'E'
                regionStr = '_' + lat_str + lon_str
            if not (varName == 'temp' or varName == 'salt'):
                responseObj["error"] = "To display a depth cross section, please select either Temperature or Salinity variables."
                return responseObj
        
        plot_filename = "%s_%s_%s_%s" % (branProduct["monthly"], varName, yearMonthStr, regionStr)
        bgImage_filename = "%s_%s_%s" % (branProduct["monthly"], varName, yearMonthStr)
        plot_filename_fullpath = os.path.join(server_config['outputDir'], plot_filename)
        bgImage_filename_fullpath = os.path.join(server_config['outputDir'], bgImage_filename)
        
        # Generate background image layers if they do not exist
        if not util.check_files_exist(bgImage_filename_fullpath, [COMMON_FILES[k] for k in ['mapeast', 'mapeastw', 'mapwest', 'mapwestw', 'scale']]):
            draw_monthly_mean_surface_plot(varName, yearStr, monthStr, regionStr, bgImage_filename, draw_background_images=True, plot_data=False)

        if not os.path.exists(plot_filename_fullpath + COMMON_FILES['img']):
            if ("lat" in form) and ("lon" in form) and (varName == 'temp' or varName == 'salt'):
                # Plot subsurface data
                if varName == 'temp':
                    unitStr = 'Degrees Celsius'
                    varLongName = 'Subsurface Temperature Profile\n'
                    cb_ticks = np.arange(16.0, 30.1, 1.0)
                elif varName == 'salt':
                    unitStr = 'PSU'
                    varLongName = 'Subsurface Salinity Profile\n'
                    cb_ticks = np.arange(33, 37.1, 0.5)

                title_date_str = datetime.date(year, month, 1).strftime('%B %Y')
                titleStr = title_date_str + ': ' + varLongName
                
                input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', varName, varName + '_' + yearStr + '_' + monthStr + '.nc4')
                lats1, lons1, zlevels1, zonal_data = branPlotterNew.load_BRAN_data(input_data_file, varName, lat_cnt, lat_cnt, lon_cnt - 5.0, lon_cnt + 5.0, depth_min=0.0, depth_max=300.0)
                lats2, lons2, zlevels2, meridional_data = branPlotterNew.load_BRAN_data(input_data_file, varName, lat_cnt - 5.0, lat_cnt + 5.0, lon_cnt, lon_cnt, depth_min=0.0, depth_max=300.0)
                
                # Load surface data
                input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', varName, varName + '_' + yearStr + '_' + monthStr + '.nc4')
                lats, lons, zlevels, data = branPlotterNew.load_BRAN_data(input_data_file, varName, -999.0, 999.0, -999.0, 999.0)
                  
                branPlotterNew.plot_BRAN_depth_slice(zlevels1, lats2, lons1, zonal_data, meridional_data, lats, lons, data,
                                                     lat_cnt, lon_cnt, output_filename=plot_filename_fullpath + '.png',
                                                     units=unitStr, title=titleStr, cb_ticks=cb_ticks, product_label_str='Bluelink Reanalysis 2.1')

            else:
                # Plot surface data
                if varName in ['temp', 'salt', 'eta', 'uvtemp', 'uveta']:
                    draw_monthly_mean_surface_plot(varName, yearStr, monthStr, regionStr, bgImage_filename, 
                                                   plot_filename_fullpath=plot_filename_fullpath, 
                                                   draw_background_images=False, plot_data=True)

        if not (util.check_files_exist(bgImage_filename_fullpath, [COMMON_FILES[k] for k in ['mapeast', 'mapeastw', 'mapwest', 'mapwestw', 'scale']]) and \
            os.path.exists(plot_filename_fullpath + COMMON_FILES['img'])):
            responseObj["error"] = "Requested image is not available at this time."
        else:
            responseObj.update(util.build_response_object(
                               COMMON_FILES.keys(),
                               os.path.join(server_config['baseURL'], server_config['rasterURL'], bgImage_filename),
                               COMMON_FILES.values()))
            responseObj["img"] = os.path.join(server_config['baseURL'], server_config['rasterURL'], plot_filename + '.png')
                
    return responseObj



def draw_monthly_mean_surface_plot(varName, yearStr, monthStr, regionStr, bgImage_filename, plot_filename_fullpath=None, draw_background_images=False, plot_data=True):
    
    if varName == 'temp':
        dataVar = 'temp'
        unitStr = 'Degrees Celsius'
        if regionConfig.regions.has_key(regionStr):
            if regionConfig.regions[regionStr][0] == 'pi':
                cb_ticks = np.arange(20.0,32.1,1.0)
            else:
                cb_ticks = np.arange(0.0,32.1,2.0)
        else:
                cb_ticks = np.arange(0.0,32.1,2.0)
        varLongName = 'Surface Temperature'
        cb_tick_fmt="%.0f"
        currents = False
    elif varName == 'uvtemp':
        dataVar = 'temp'
        unitStr = 'Degrees Celsius'
        if regionConfig.regions.has_key(regionStr):
            if regionConfig.regions[regionStr][0] == 'pi':
                cb_ticks = np.arange(20.0,32.1,1.0)
            else:
                cb_ticks = np.arange(0.0,32.1,2.0)
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
        currents = False
    elif varName == 'eta':
        dataVar = 'eta'
        unitStr = 'Metres'
        cb_ticks = np.arange(-0.5,0.51,0.1)
        varLongName = 'Sea Level Height'
        cb_tick_fmt="%.2f"
        currents = False
    elif varName == 'uveta':
        dataVar = 'eta'
        unitStr = 'Metres'
        cb_ticks = np.arange(-0.5,0.51,0.1)
        varLongName = 'Sea Level Height and Currents'
        cb_tick_fmt="%.2f"
        currents = True
    
    # Load surface data
    input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', dataVar, dataVar + '_' + yearStr + '_' + monthStr + '.nc4')
    lats, lons, zlevels, data = branPlotterNew.load_BRAN_data(input_data_file, dataVar, -999.0, 999.0, -999.0, 999.0)

    if draw_background_images:
        # Plot background image layers
        config = bc.BranConfig()
        plot = plotter.Plotter()
        plot.plotBasemapEast(data, lats, lons, dataVar, config, bgImage_filename)
        plot.plotBasemapWest(data, lats, lons, dataVar, config, bgImage_filename)
        plot.plotScale(data, dataVar, config, bgImage_filename)

    if plot_data:
        # Get domain boundaries
        lat_min = regionConfig.regions[regionStr][1]['llcrnrlat']
        lat_max = regionConfig.regions[regionStr][1]['urcrnrlat']
        lon_min = regionConfig.regions[regionStr][1]['llcrnrlon']
        lon_max = regionConfig.regions[regionStr][1]['urcrnrlon']

        # Construct title
        title_date_str = datetime.date(int(yearStr), int(monthStr), 1).strftime('%B %Y')
        regionLongName = regionConfig.regions[regionStr][2]
        title = regionLongName + '\n' + title_date_str + ': ' + varLongName
        
        # Load current data if required
        if currents == True:
            input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', 'u', 'u' + '_' + yearStr + '_' + monthStr + '.nc4')
            lats2, lons2, zlevels, u = branPlotterNew.load_BRAN_data(input_data_file, 'u', lat_min - 1.0, lat_max + 1.0, lon_min - 1.0, lon_max + 1.0)
            input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', 'v', 'v' + '_' + yearStr + '_' + monthStr + '.nc4')
            lats2, lons2, zlevels, v = branPlotterNew.load_BRAN_data(input_data_file, 'v', lat_min - 1.0, lat_max + 1.0, lon_min - 1.0, lon_max + 1.0)
            contourLines=False
        else:
            lats2 = None; lons2 = None
            u = None; v = None
            contourLines = True
        
        # Plot surface data
        branPlotterNew.plot_BRAN_surface_data(lats, lons, data, lat_min, lat_max, lon_min, lon_max,
                                             output_filename=plot_filename_fullpath + '.png', title=title, units=unitStr,
                                             cb_ticks=cb_ticks, cb_tick_fmt=cb_tick_fmt, cmp_name='jet', proj='cyl',
                                             contourLines=contourLines, product_label_str='Bluelink Reanalysis 2.1',
                                             vlat=lats2, vlon=lons2, u=u, v=v)
