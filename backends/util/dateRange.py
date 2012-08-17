#!/usr/bin/python

import datetime
from dateutil.relativedelta import *

weekDelta = [relativedelta(weekday=MO),
             relativedelta(weekday=TU),
             relativedelta(weekday=WE),
             relativedelta(weekday=TH),
             relativedelta(weekday=FR),
             relativedelta(weekday=SA),
             relativedelta(weekday=SU)
             ]

def getMonths(date, monthRange):
    """
    Get the months using the input date as the last month and count back in time.
    """
    year = int(date[0:4])
    month = int(date[4:6])
    day = int(date[6:8])
  
    mthRange = int(monthRange)

    initDate = datetime.date(year, month, day)

    months = []
    for delta in range(0, mthRange):
        months.append(initDate + relativedelta(months=-delta))
    months.reverse()
    return months 

def getWeekDays(date):
    """
    Get the week days given a date. The date can be any day in a week.
    """
    year = int(date[0:4])
    month = int(date[4:6])
    day = int(date[6:8])
 
    initDate = datetime.date(year, month, day) #which is a Monday
    if (initDate.weekday() != 0):
        initDate = initDate - datetime.timedelta(initDate.weekday())

    weekdays = []
    for weekdayDelta in weekDelta:
        weekday = initDate+weekdayDelta 
        weekdays.append(weekday)

    return weekdays 