#!/usr/bin/python

import os
import subprocess
from ..util import serverConfig


serverCfg = serverConfig.servers[serverConfig.currentServer]

def generateWeekly(weekDays):

    output = serverCfg["dataDir"]["reynolds"] + "weekly/avhrr-only-v2." + weekDays[0].strftime('%Y%m%d') + "ave.nc"
    if not os.path.exists(output):
        command = ['/usr/local/bin/ncea', '-O']
        for date in weekDays:
            filename = serverCfg["dataDir"]["reynolds"] + "daily/" + date.strftime('%Y') + "/" + "avhrr-only-v2." + date.strftime('%Y%m%d') + ".nc"
            command.append(filename)
        command.append(output)
        subprocess.call(command)

def generate3Monthly(months):
    output = serverCfg["dataDir"]["reynolds"] + "3monthly/avhrr-only-v2." + months[-1].strftime('%Y%m') + "ave.nc"
    if not os.path.exists(output):
        command = ['/usr/local/bin/ncea', '-O']
        for month in months:
            filename = serverCfg["dataDir"]["reynolds"] + "monthly/" + month.strftime('%Y') + "/" + "avhrr-only-v2." + month.strftime('%Y%m') + "ave.nc"
            command.append(filename)
        command.append(output)
        subprocess.call(command)

def generate6Monthly(months):
    output = serverCfg["dataDir"]["reynolds"] + "6monthly/avhrr-only-v2." + months[-1].strftime('%Y%m') + "ave.nc"
    if not os.path.exists(output):
        command = ['/usr/local/bin/ncea', '-O']
        for month in months:
            filename = serverCfg["dataDir"]["reynolds"] + "monthly/" + month.strftime('%Y') + "/" + "avhrr-only-v2." + month.strftime('%Y%m') + "ave.nc"
            command.append(filename)
        command.append(output)
        subprocess.call(command)