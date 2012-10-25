#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Sheng Guo <s.guo@bom.gov.au>
#          Matthew Howie

def monthconfig(month):
    if month == '01':
        k1=0
        k2=31
        name = 'January'
    if month == '02':
        k1=31
        k2=62
        name = 'February'
    if month == '03':
        k1=62
        k2=93
        name = 'March'
    if month == '04':
        k1=93
        k2=124
        name = 'April'
    if month == '05':
        k1=124
        k2=155
        name = 'May'
    if month == '06':
        k1=155
        k2=186
        name = 'June'
    if month == '07':
        k1=186
        k2=217
        name = 'July'
    if month == '08':
        k1=217
        k2=248
        name = 'August'
    if month == '09':
        k1=248
        k2=279
        name = 'September'
    if month == '10':
        k1=279
        k2=310
        name = 'October'
    if month == '11':
        k1=310
        k2=341
        name = 'November'
    if month == '12':
        k1=341
        k2=372
        name = 'December'
    return k1, k2, name
