#!/usr/bin/python

import bisect
import datetime

from netCDF4 import Dataset
import numpy as np

import branConfig as rc
import ocean.util as util
from ..util import regionConfig
from ..netcdf import plotter

class BranPlotter ():
    """
    BRAN plotter is specifically designed to plot the BRAN
    netcdf data
    """
    config = None
    serverCfg = None

    def __init__(self):
       """Does nothing"""
       self.config = rc.BranConfig()
       self.serverCfg = util.get_server_config()

    def plot(self, outputFilename, variable, date, area, period):
        """
        Plot the thumbnail image and also the east and west map images.
        """
        cntLabel = False
        if variable == 'tempdec':
            filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/" + "temp_" + date[:4]  + "_" + date[:6]  + "_dec"
            cntLabel = True
        elif variable == 'saltdec':
            filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/" + "salt_" + date[:4]  + "_" + date[:6]  + "_dec"
            cntLabel = True
        elif variable == 'etadec':
            filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/" + "eta_" + date[:4]  + "_" + date[:6]  + "_dec"
            cntLabel = True
        else:
            if period=='daily':
                if variable == 'temp':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/" + "temp_" + date[:4]  + "_" + date[:6] + "_" + date[:8]
                if variable == 'temp_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/temp_ano/" + "temp_ano_" + date[:4]  + "_" + date[:6] + "_" + date[:8]
                if variable == 'salt':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/" + "salt_" + date[:4]  + "_" + date[:6] + "_" + date[:8]
                if variable == 'salt_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/salt_ano/" + "salt_ano_" + date[:4]  + "_" + date[:6] + "_" + date[:8]
                if variable == 'eta':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/" + "eta_" + date[:4]  + "_" + date[:6] + "_" + date[:8]
                if variable == 'eta_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/eta_ano/" + "eta_ano_" + date[:4]  + "_" + date[:6] + "_" + date[:8]
                if variable == 'currents':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/uv/" + "uv_" + date[:4]  + "_" + date[:6] + "_" + date[:8]
            elif period=='weekly':
                if variable == 'temp':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/" + "temp_" + date +  "ave"
                    startDate, endDate = daterange.generateWeekly(date)
                if variable == 'temp_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/temp_ano/" + "temp_ano_" + date +  "ave"
                    startDate, endDate = daterange.generateWeekly(date)
                if variable == 'salt':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/" + "salt_" + date +  "ave"
                    startDate, endDate = daterange.generateWeekly(date)
                if variable == 'salt_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/salt_ano/" + "salt_ano_" + date +  "ave"
                    startDate, endDate = daterange.generateWeekly(date)
                if variable == 'eta':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/" + "eta_" + date +  "ave"
                    startDate, endDate = daterange.generateWeekly(date)
                if variable == 'eta_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/eta_ano/" + "eta_ano_" + date +  "ave"
                    startDate, endDate = daterange.generateWeekly(date)
                if variable == 'currents':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/uv/" + "uv_" + date +  "ave"
                    startDate, endDate = daterange.generateWeekly(date)
            elif period=='monthly':
                if variable == 'temp':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/" + "temp_" + date[:4]  + "_" + date[:6]
                if variable == 'temp_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/temp_ano/" + "temp_ano_" + date[:4]  + "_" + date[:6]
                if variable == 'salt':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/" + "salt_" + date[:4]  + "_" + date[:6]
                if variable == 'salt_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/salt_ano/" + "salt_ano_" + date[:4]  + "_" + date[:6]
                if variable == 'eta':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/" + "eta_" + date[:4]  + "_" + date[:6]
                if variable == 'eta_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/eta_ano/" + "eta_ano_" + date[:4]  + "_" + date[:6]
                if variable == 'currents':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/uv/" + "uv_" + date[:4]  + "_" + date[:6]
            elif period=='3monthly':
                if variable == 'temp':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/" + "temp_" + date[:4]  + "_" + date[:6] + "_3mnth"
                    startDate = daterange.generate3Month(date)
                if variable == 'temp_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/temp_ano/" + "temp_ano_" + date[:4]  + "_" + date[:6] + "_3mnth"
                    startDate = daterange.generate3Month(date)
                if variable == 'salt':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/" + "salt_" + date[:4]  + "_" + date[:6] + "_3mnth"
                    startDate = daterange.generate3Month(date)
                if variable == 'salt_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/salt_ano/" + "salt_ano_" + date[:4]  + "_" + date[:6] + "_3mnth"
                    startDate = daterange.generate3Month(date)
                if variable == 'eta':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/" + "eta_" + date[:4]  + "_" + date[:6] + "_3mnth"
                    startDate = daterange.generate3Month(date)
                if variable == 'eta_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/eta_ano/" + "eta_ano_" + date[:4]  + "_" + date[:6] + "_3mnth"
                    startDate = daterange.generate3Month(date)
                if variable == 'currents':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/uv/" + "uv_" + date[:4]  + "_" + date[:6] + "_3mnth"
                    startDate = daterange.generate3Month(date)
            elif period=='6monthly':
                if variable == 'temp':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/" + "temp_" + date[:4]  + "_" + date[:6] + "_6mnth"
                    startDate = daterange.generate6Month(date)
                if variable == 'temp_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/temp_ano/" + "temp_ano_" + date[:4]  + "_" + date[:6] + "_6mnth"
                    startDate = daterange.generate6Month(date)
                if variable == 'salt':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/" + "salt_" + date[:4]  + "_" + date[:6] + "_6mnth"
                    startDate = daterange.generate6Month(date)
                if variable == 'salt_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/salt_ano/" + "salt_ano_" + date[:4]  + "_" + date[:6] + "_6mnth"
                    startDate = daterange.generate6Month(date)
                if variable == 'eta':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/" + "eta_" + date[:4]  + "_" + date[:6] + "_6mnth"
                    startDate = daterange.generate6Month(date)
                if variable == 'eta_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/eta_ano/" + "eta_ano_" + date[:4]  + "_" + date[:6] + "_6mnth"
                    startDate = daterange.generate6Month(date)
                if variable == 'currents':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/uv/" + "uv_" + date[:4]  + "_" + date[:6] + "_6mnth"
                    startDate = daterange.generate6Month(date)
            elif period=='yearly':
                if variable == 'temp':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/" + "temp_" + date[:4]
                if variable == 'temp_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/temp/temp_ano/" + "temp_ano_" + date[:4]
                if variable == 'salt':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/" + "salt_" + date[:4]
                if variable == 'salt_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/salt/salt_ano/" + "salt_ano_" + date[:4]
                if variable == 'eta':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/" + "eta_" + date[:4]
                if variable == 'eta_ano':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/eta/eta_ano/" + "eta_ano_" + date[:4]
                if variable == 'currents':
                    filename = self.serverCfg["dataDir"]["blue_link"] + "/data/" + period + "/uv/" + "uv_" + date[:4]
            else:
                return -1

        filename = filename + ".nc"
        dataset = Dataset(filename, 'r')
        Var = dataset.variables[self.config.getVariableType(variable)][0][0]
        lats = dataset.variables['lat'][:]
        lons = dataset.variables['lon'][:]

        delon = lons[1]-lons[0]; delat = lats[1]-lats[0]
        lons = (lons - 0.5*delon).tolist()
        lons.append(lons[-1]+delon)
        lons = np.array(lons,np.float64) #TODO check necessariness
        lats = (lats - 0.5*delat).tolist()
        lats.append(lats[-1]+delat)
        lats = np.array(lats,np.float64)

        plot = plotter.Plotter()
        plot.plot(Var, lats, lons, variable, self.config, outputFilename,\
                  regionConfig.regions[area][1]["llcrnrlat"],\
                  regionConfig.regions[area][1]["llcrnrlon"],\
                  regionConfig.regions[area][1]["urcrnrlat"],\
                  regionConfig.regions[area][1]["urcrnrlon"],\
                  centerLabel = cntLabel)
        plot.plotBasemapEast(Var, lats, lons, variable, self.config, outputFilename)
        plot.plotBasemapWest(Var, lats, lons, variable, self.config, outputFilename)

        dataset.close()

        return 0


    def plotSubsurface(self, outputFilename, **args):
        """
        Plot the thumbnail image and also the east and west map images.
        """
        period = args['period']
        variable = args['var']
        date = args['date']
        dateObj = datetime.date(int(date[:4]), int(date[4:6]), int(date[6:]))
        formattedDate = ''
        if period=='monthly':
            formattedDate = dateObj.strftime('%B %Y')
            if variable == 'temp':
                filename = self.serverCfg["dataDir"]["bran"] + period + "/temp/" + "temp_" + date[:4]  + "_" + date[4:6]
            elif variable == 'temp_ano':
                filename = self.serverCfg["dataDir"]["bran"] + period + "/temp/temp_ano/" + "temp_ano_" + date[:4]  + "_" + date[4:6]
        else:
            return -1

        dataset = Dataset(filename + '.nc', 'r')
        data = dataset.variables[self.config.getVariableType(variable)][0, :, :, :]
        lats = dataset.variables['yt_ocean'][:]
        lons = dataset.variables['xt_ocean'][:]
        dep = dataset.variables['zt_ocean'][:]
    #    print filename
        inputLat1 = float(args['xlat1'])
        inputLon1 = float(args['xlon1'])
        if inputLon1 < 0:
            inputLon1 = 360 + inputLon1
        inputLat2 = float(args['xlat2'])
        inputLon2 = float(args['xlon2'])
        if inputLon2 < 0:
            inputLon2 = 360 + inputLon2

        gridLatIndex1 = bisect.bisect_left(lats, inputLat1)
        gridLonIndex1 = bisect.bisect_left(lons, inputLon1)
        gridLonIndex2 = bisect.bisect_left(lons, inputLon2)

        args['formattedDate'] = formattedDate
        subsurface = data[:25, gridLatIndex1, gridLonIndex1:gridLonIndex2]
        plot = plotter.Plotter()
        if args['xlat1'] == args['xlat2']:
            plot.plotlatx(subsurface, dep[0:25], lons[gridLonIndex1:gridLonIndex2], variable, self.config, outputFilename, **args)

        #if args['xlon1'] == args['xlon2']:
        #    plot.plotlonx(data, lats, dep, variable, self.config, outputFilename,\
        #              centerLabel = cntLabel)
        dataset.close()

        return 0

#        filename = filename + ".nc"
#        dataset = Dataset(filename, 'r')
#        Var = dataset.variables[self.config.getVariableType(variable)][0][0]
#        lats = dataset.variables['lat'][:]
#        lons = dataset.variables['lon'][:]
#
#        delon = lons[1]-lons[0]; delat = lats[1]-lats[0]
#        lons = (lons - 0.5*delon).tolist()
#        lons.append(lons[-1]+delon)
#        lons = np.array(lons,np.float64) #TODO check necessariness
#        lats = (lats - 0.5*delat).tolist()
#        lats.append(lats[-1]+delat)
#        lats = np.array(lats,np.float64)
#
#        plot = plotter.Plotter()
#        plot.plot(Var, lats, lons, variable, self.config, outputFilename,\
#                  regionConfig.regions[area][1]["llcrnrlat"],\
#                  regionConfig.regions[area][1]["llcrnrlon"],\
#                  regionConfig.regions[area][1]["urcrnrlat"],\
#                  regionConfig.regions[area][1]["urcrnrlon"],\
#                  centerLabel = cntLabel)
#        plot.plotBasemapEast(Var, lats, lons, variable, self.config, outputFilename)
#        plot.plotBasemapWest(Var, lats, lons, variable, self.config, outputFilename)
#
#        dataset.close()

        return 0

