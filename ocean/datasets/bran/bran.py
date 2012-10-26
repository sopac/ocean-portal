#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Nick Summons <n.summons@bom.gov.au>
#          Danielle Madeley <d.madeley@bom.gov.au>

import os
import os.path
import sys
import datetime

import numpy as np

from ocean import util, config
from ocean.config import regionConfig, productName
from ocean.netcdf import plotter
from ocean.netcdf.plotter import COMMON_FILES

import branConfig as bc
import branPlotterNew

server_config = config.get_server_config()
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
        
        # Display error if variable is invalid
        if varName in ['temp', 'salt', 'eta', 'uvtemp', 'uveta']:
            pass
        else:
            responseObj["error"] = "Invalid variable"
            return responseObj

        if ("lat" in form) and ("lon" in form):
            plot_subsurface = True
            # Display error if variable selected for subsurface plot is invalid
            if not (varName == 'temp' or varName == 'salt'):
                responseObj["error"] = "To display a depth cross section, please select either Temperature or Salinity variables."
                return responseObj
        else:
            plot_subsurface = False

        if plot_subsurface:
            lat_cnt = np.float(form["lat"].value)
            lon_cnt = np.mod(np.float(form["lon"].value), 360.0)
            if (lon_cnt >= 0) and (lon_cnt <= 360) and (lat_cnt >= -90) and (lat_cnt <= 90):
                lon_str = '%.2fE' % lat_cnt
                if lat_cnt >= 0:
                    lat_str = '%.2fN' % lat_cnt
                else:
                    lat_str = '%.2fS' % lat_cnt
                regionStr = '_' + lat_str + lon_str
                regionStr = regionStr.replace('.', '')
            else:
                responseObj["error"] = "Invalid lat/lon coordinates"
                return responseObj

            plot_filename = "%s_%s_%s_%s" % (branProduct["monthly"], varName, yearMonthStr, regionStr)
            plot_filename_fullpath = os.path.join(server_config['outputDir'], plot_filename)
            basemap_filename = "%s_%s_%s" % (branProduct["monthly"], varName, yearMonthStr)
            basemap_filename_fullpath = os.path.join(server_config['outputDir'], basemap_filename)

            # Generate basemap if does not exist
            if check_basemap_exists(basemap_filename_fullpath) is False:
                plot_surface_data(varName, yearStr, monthStr, regionStr, basemap_filename_fullpath, basemap_only=True)

            # Determine plot settings
            if varName == 'temp':
                unitStr = ur'\u00b0' + 'C'
                varLongName = 'Surface and Subsurface Temperature Profile'
                cb_ticks = np.arange(16.0, 30.1, 1.0)
            elif varName == 'salt':
                unitStr = 'PSU'
                varLongName = 'Surface and Subsurface Salinity Profile'
                cb_ticks = np.arange(33, 37.1, 0.5)

            title_date_str = datetime.date(year, month, 1).strftime('%B %Y')
            titleStr = varLongName + ': \n' + title_date_str + '\n'

            # Load sub-surface data
            input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', varName, varName + '_' + yearStr + '_' + monthStr + '.nc4')
            lats1, lons1, zlevels1, zonal_data = branPlotterNew.load_BRAN_data(input_data_file, varName, lat_cnt, lat_cnt, lon_cnt - 5.0, lon_cnt + 5.0, depth_min=0.0, depth_max=300.0)
            lats2, lons2, zlevels2, meridional_data = branPlotterNew.load_BRAN_data(input_data_file, varName, lat_cnt - 5.0, lat_cnt + 5.0, lon_cnt, lon_cnt, depth_min=0.0, depth_max=300.0)

            # Load surface data
            input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', varName, varName + '_' + yearStr + '_' + monthStr + '.nc4')
            lats, lons, zlevels, data = branPlotterNew.load_BRAN_data(input_data_file, varName, -999.0, 999.0, -999.0, 999.0)

            # Generate subsurface plot
            branPlotterNew.plot_BRAN_depth_slice(zlevels1, lats2, lons1, zonal_data, meridional_data, lats, lons, data,
                                                 lat_cnt, lon_cnt, output_filename=plot_filename_fullpath + '.png',
                                                 units=unitStr, title=titleStr, cb_ticks=cb_ticks, product_label_str='Bluelink Reanalysis 2.1')
        else:
            # Plot surface data
            plot_filename = "%s_%s_%s_%s" % (branProduct["monthly"], varName, yearMonthStr, regionStr)
            plot_filename_fullpath = os.path.join(server_config['outputDir'], plot_filename)
            basemap_filename = plot_filename
            basemap_filename_fullpath = plot_filename_fullpath
            if check_basemap_and_plot_exists(plot_filename_fullpath) is False:
                # If drawing currents, determine vector plot settings
                if varName in ['uvtemp', 'uveta']:
                    lat_min = regionConfig.regions[regionStr][1]['llcrnrlat']
                    lat_max = regionConfig.regions[regionStr][1]['urcrnrlat']
                    lon_min = regionConfig.regions[regionStr][1]['llcrnrlon']
                    lon_max = regionConfig.regions[regionStr][1]['urcrnrlon']
                    draw_every, arrow_scale = branPlotterNew.get_vector_plot_settings(lat_min, lat_max, lon_min, lon_max)
                    # Display error if chosen region is too large for displaying currents
                    if (draw_every is None) or (arrow_scale is None):
                        responseObj["error"] = "The region is too large for displaying currents.  Please select a smaller region and try again."
                        return responseObj
                else:
                    draw_every, arrow_scale = None, None

                plot_surface_data(varName, yearStr, monthStr, regionStr, basemap_filename_fullpath,
                                               plot_filename_fullpath=plot_filename_fullpath,
                                               basemap_only=False, draw_every=draw_every, arrow_scale=arrow_scale)

        if check_basemap_exists(basemap_filename_fullpath) and check_plot_exists(plot_filename_fullpath):
            responseObj.update(util.build_response_object(
                               COMMON_FILES.keys(),
                               os.path.join(server_config['baseURL'],
                                            server_config['rasterURL'],
                                            basemap_filename),
                               COMMON_FILES.values()))
            responseObj["img"] = os.path.join(server_config['baseURL'],
                                              server_config['rasterURL'],
                                              plot_filename + '.png')
            util.touch_files(os.path.join(server_config['outputDir'],
                                          plot_filename),
                             COMMON_FILES.values())
            util.touch_files(os.path.join(plot_filename_fullpath),
                             [ COMMON_FILES['img'] ])
        else:
            responseObj["error"] = "Requested image is not available at this time."

    return responseObj


def plot_surface_data(varName, yearStr, monthStr, regionStr, basemap_filename_fullpath, plot_filename_fullpath=None,
                      basemap_only=False, draw_every=1, arrow_scale=10):
    
    if varName == 'temp':
        dataVar = 'temp'
        unitStr = ur'\u00b0' + 'C'
        if regionConfig.regions.has_key(regionStr):
            if regionConfig.regions[regionStr][0] == 'pi':
                cb_ticks = np.arange(20.0,32.1,1.0)
            else:
                cb_ticks = np.arange(0.0,32.1,2.0)
        else:
                cb_ticks = np.arange(0.0,32.1,2.0)
        varLongName = 'Sea Surface Temperature'
        cb_tick_fmt="%.0f"
        currents = False
    elif varName == 'uvtemp':
        dataVar = 'temp'
        unitStr = ur'\u00b0' + 'C'
        if regionConfig.regions.has_key(regionStr):
            if regionConfig.regions[regionStr][0] == 'pi':
                cb_ticks = np.arange(20.0,32.1,1.0)
            else:
                cb_ticks = np.arange(0.0,32.1,2.0)
        else:
            cb_ticks = np.arange(0.0,32.1,2.0)
        varLongName = 'Sea Surface Temperature and Currents'
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

    # Plot background image layers
    config = bc.BranConfig()
    plot = plotter.Plotter()
    plot.plot_basemaps_and_colorbar(lats, lons, data,
                                    output_filename=basemap_filename_fullpath,
                                    units=unitStr, cm_edge_values=cb_ticks,
                                    cb_tick_fmt=cb_tick_fmt,
                                    cb_labels=None, cb_label_pos=None,
                                    cmp_name='jet', extend='both')

    if not basemap_only:
        # Get domain boundaries
        lat_min = regionConfig.regions[regionStr][1]['llcrnrlat']
        lat_max = regionConfig.regions[regionStr][1]['urcrnrlat']
        lon_min = regionConfig.regions[regionStr][1]['llcrnrlon']
        lon_max = regionConfig.regions[regionStr][1]['urcrnrlon']

        # Construct title
        title_date_str = datetime.date(int(yearStr), int(monthStr), 1).strftime('%B %Y')
        regionLongName = regionConfig.regions[regionStr][2]
        title = regionLongName + '\n' + varLongName + ': ' + title_date_str

        input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', dataVar, dataVar + '_' + yearStr + '_' + monthStr + '.nc4')
        lats, lons, zlevels, data = branPlotterNew.load_BRAN_data(input_data_file, dataVar, lat_min - 1.0, lat_max + 1.0, lon_min - 1.0, lon_max + 1.0)

        # Load current data if required
        if currents == True:
            input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', 'u', 'u' + '_' + yearStr + '_' + monthStr + '.nc4')
            lats2, lons2, zlevels, u = branPlotterNew.load_BRAN_data(input_data_file, 'u', lat_min - 1.0, lat_max + 1.0, lon_min - 1.0, lon_max + 1.0)
            input_data_file = os.path.join(server_config['dataDir']['bran'], 'monthly', 'v', 'v' + '_' + yearStr + '_' + monthStr + '.nc4')
            lats2, lons2, zlevels, v = branPlotterNew.load_BRAN_data(input_data_file, 'v', lat_min - 1.0, lat_max + 1.0, lon_min - 1.0, lon_max + 1.0)
            contourLines = False
        else:
            lats2 = None; lons2 = None
            u = None; v = None
            contourLines = True

        # Plot surface data
        plot.plot_surface_data(lats, lons, data,
                               lat_min, lat_max, lon_min, lon_max,
                               output_filename=plot_filename_fullpath + '.png',
                               title=title, units=unitStr,
                               cm_edge_values=cb_ticks, cb_tick_fmt=cb_tick_fmt,
                               cmp_name='jet', proj='cyl',
                               contourLines=contourLines,
                               product_label_str='Bluelink Reanalysis 2.1',
                               vlat=lats2, vlon=lons2, u=u, v=v,
                               draw_every=draw_every, arrow_scale=arrow_scale)

    plot.wait()

def check_basemap_exists(filename_fullpath):
    return util.check_files_exist(filename_fullpath, [COMMON_FILES[k] for k in ['mapeast', 'mapeastw', 'mapwest', 'mapwestw', 'scale']])

def check_plot_exists(filename_fullpath):
    return os.path.exists(filename_fullpath + COMMON_FILES['img'])

def check_basemap_and_plot_exists(filename_fullpath):
    return util.check_files_exist(filename_fullpath, COMMON_FILES.values())
