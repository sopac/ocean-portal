var ocean = ocean || {};
ocean.controls = ['selectionDiv', 'toggleDiv', 'sliderDiv', 'yearMonthDiv']
ocean.compare = false;
ocean.processing = false;
//ocean.average = false;
//ocean.trend = false;
//ocean.runningAve = false;
//ocean.runningAveLen = 2;
ocean.MIN_YEAR = 1850;
Date.prototype.getMonthString = function() {
    var calMonth = this.getMonth() + 1;
    return (calMonth < 10) ?  ('0' + calMonth) : calMonth + '';
}
ocean.dsConf = {
    reynolds: {url: function() {return "/cgi-bin/portal.py?dataset=reynolds"
                   + "&map=" + this.variable.get('id')
                   + "&date=" + $.datepick.formatDate('yyyymmdd', ocean.date)
                   + "&area=" + ocean.region
                   + "&period=" + ocean.period
                   + "&average=" + ocean.dsConf['reynolds'].aveCheck.average
                   + "&trend=" + ocean.dsConf['reynolds'].aveCheck.trend
                   + "&runningAve=" + ocean.dsConf['reynolds'].aveCheck.runningAve
                   + "&runningInterval=" + ocean.dsConf['reynolds'].runningInterval
                   + "&timestamp=" + new Date().getTime()},
        data: null,
        variable: null,
        aveCheck: {},
        mainCheck: 'average',
        runningInterval: 2,
        callback: function(data) {
            var imgDiv = $('#mainImg')
            if (ocean.compare){
                var imgList = imgDiv.childNodes;
                imgDiv.removeChild(imgDiv.firstChild);
                if (imgList.length >= compareSize) {
                    imgDiv.removeChild(imgDiv.lastChild);
                }
                var img = document.createElement("IMG");
                if(average) {
                    img.src = data.aveImg;
                    img.width = "680";
                    document.getElementById('aveArea').innerHTML = '<div style="display:inline-block; width:341px; text-align:left">Download data from <a href="' + data.aveData + '" target="_blank">here</a></div>'
                                                                 + '<div style="display:inline-block; width:341px; text-align:right"><b>Average(1981-2010)</b> ' + Math.round(data.mean*100)/100 + '\u00B0C</div>'
                }
                else if (data.img != null) {
                    img.src = data.img;
                    img.width = "680";
                    document.getElementById('aveArea').innerHTML = ''
                }
                else {
                    img.src = "images/notavail.png";
                    document.getElementById('aveArea').innerHTML = ''
                }
                    imgDiv.insertBefore(img, imgDiv.firstChild);
            }
            else {
                if (this.variable.get("id") == "anom" && this.aveCheck.average) {
                    imgDiv.html('<img src="' + data.aveImg + '" width="680"/>')
                    $('#aveArea').html('<div style="display:inline-block; width:341px; text-align:left">Download data from <a href="' 
                        + data.aveData + '" target="_blank">here</a></div>'
                        + '<div style="display:inline-block; width:341px; text-align:right"><b>Average(1981-2010)</b> ' 
                        + Math.round(data.mean*100)/100 + '\u00B0C</div>')
                }
                else if (data.img != null) {
                    imgDiv.html('<img src="' + data.img + '?time=' + new Date().getTime() + '" width="680"/>')
                    document.getElementById('aveArea').innerHTML = ''
                }
                else if (data.error != null) {
                    imgDiv.html('<img src="images/notavail.png" />')
                    document.getElementById('aveArea').innerHTML = ''
                }
            }
        }
    },
    ersst: {
    }
}

function AveCheck(id, state) {
    this.id = id;
    this.state = state;
}

//*****************************************************
//Initialise Datasets
//*****************************************************
//
//Reynolds
Ext.require(['*']);
Ext.onReady(function() {
    Ext.Loader.setConfig({enabled:true});

    Ext.define('Dataset', {
        extend: 'Ext.data.Model',
        fields: ['name', 'id', 'title', 'dateRange'],
        idProperty: 'id',
        hasMany: {model:'Variable', name: 'variables'},
        proxy: {
            type: 'ajax',
            url: 'config/datasets.json',
            reader: {
                type: 'json'
            }
        }
    });
   
    Ext.define('Variable', {
        extend: 'Ext.data.Model',
        idProperty: 'id',
        fields: ['name', 'id', 'periods', 'areas', 'average'],
        belongsTo: 'Dataset'
    });
        

    Ext.define('Region', {
        extend: 'Ext.data.Model',
        idProperty: 'id',
        fields: ['name', 'id'],
        proxy: {
            type: 'ajax',
            url: 'config/regions.json',
            reader: {
                type: 'json'
            }
        }
    });

    Ext.define('Period', {
        extend: 'Ext.data.Model',
        idProperty: 'id',
        fields: ['name', 'id'],
        proxy: {
            type: 'ajax',
            url: 'config/period.json',
            reader: {
                type: 'json'
            }
        }
    });

    ocean.datasets = Ext.create('Ext.data.Store', {
        autoLoad: true,
        model: 'Dataset'
    });
    ocean.datasets.addListener('load', createCheckBoxes);

    ocean.regions = Ext.create('Ext.data.Store', {
        autoLoad: true,
        model: 'Region'
    });

    ocean.periods = Ext.create('Ext.data.Store', {
        autoLoad: true,
        model: 'Period'
    });

    periodFilter = Ext.create('Ext.util.Filter', {filterFn: filterPeriod});
    function filterPeriod(item){
        if(ocean.dataset.variable) {
            return Ext.Array.contains(ocean.dataset.variable.get('periods'), item.get('id'));
        }
        else {
            return true;
        }
    };

    avePeriodFilter = Ext.create('Ext.util.Filter', {filterFn: aveFilterPeriod});
    function aveFilterPeriod(item){
        if(ocean.dataset.variable.get("average")) {
            return Ext.Array.contains(ocean.dataset.variable.get("average").periods, item.get('id'));
        }
        else {
            return true;
        }
    };

    regionFilter = Ext.create('Ext.util.Filter', {filterFn: filterRegion});
    function filterRegion(item){
        if(ocean.dataset.variable) {
            return Ext.Array.contains(ocean.dataset.variable.get('areas'), item.get('id'));
        }
        else {
            return true;
        }
    };

    ocean.datasetCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'datasetCombo',
        fieldLabel: 'Dataset',
        labelWidth: 50,
        width: 150,
        displayField: 'name',
        valueField: 'id',
        renderTo: 'datasetDiv',
        store: ocean.datasets,
        queryMode: 'local',
        listeners: {
            'select': selectDataset
        }
    });

    ocean.mapCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'variableCombo',
        fieldLabel: 'Variable',
        labelWidth: 50,
        width: 150,
        displayField: 'name',
        valueField: 'id',
        renderTo: 'variableDiv',
        disabled: true,
        queryMode: 'local',
        store: ocean.datasets,
        listeners: {
            'select': selectVariable
        }
    });

    ocean.periodCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'periodCombo',
        fieldLabel: 'Period',
        labelWidth: 50,
        width: 150,
        displayField: 'name',
        valueField: 'id',
        renderTo: 'selectionDiv',
        triggerAction: 'all',
        queryMode: 'local',
        store: ocean.periods,
        lastQuery: '',
        listeners: {
            'select': selectPeriod
        }
    });

    ocean.areaCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'areaCombo',
        fieldLabel: 'Area',
        labelWidth: 50,
        width: 250,
        displayField: 'name',
        valueField: 'id',
        renderTo: 'selectionDiv',
        queryMode: 'local',
        store: ocean.regions,
        lastQuery: '',
        listeners: {
            'select': selectRegion
        }
    });

    ocean.runningAveSlider = Ext.create('Ext.slider.Single', {
        renderTo: 'sliderDiv',
        hideLabel: true,
        id: 'runningAveSlider',
        width: 200,
        minValue: 2,
        maxValue: 15,
        listeners: {
            'changecomplete': selectRunningInterval
        }
    });

    ocean.plotComp = Ext.create('Ext.form.field.Checkbox', {
            boxLabel: 'Plot Comparision',
            renderTo: 'compDiv',
            width: 150,
            name: 'plotComp',
            id: 'plotComp'});
    ocean.plotComp.setDisabled(true);

    ocean.monthStore = Ext.create('Ext.data.Store', {
        fields: ['name', 'id'],
        data: [{'name': 'January', 'id': '01'},
               {'name': 'Feburary', 'id': '02'},
               {'name': 'March', 'id': '03'},
               {'name': 'April', 'id': '04'},
               {'name': 'May', 'id': '05'},
               {'name': 'June', 'id': '06'},
               {'name': 'July', 'id': '07'},
               {'name': 'August', 'id': '08'},
               {'name': 'September', 'id': '09'},
               {'name': 'October', 'id': '10'},
               {'name': 'November', 'id': '11'},
               {'name': 'December', 'id': '12'}]
    });

    ocean.monthCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'monthCombo',
        fieldLabel: 'Month',
        labelWidth: 40,
        width: 140,
        displayField: 'name',
        valueField: 'id',
        renderTo: 'monthDiv',
        queryMode: 'local',
        lastQuery: '',
        store: ocean.monthStore,
        listeners: {
            'select': function(event, args) {
                ocean.date.setMonth(event.getValue() - 1);
            } 
        }
    });

    var currentYear = new Date().getFullYear();
    var minYear = ocean.MIN_YEAR;
    var yearRange = [];
    while(minYear <= currentYear){
        yearRange.push(minYear++);
    }
    ocean.yearCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'yearCombo',
        fieldLabel: 'Year',
        labelWidth: 40,
        width: 140,
        renderTo: 'yearDiv',
        queryMode: 'local',
        lastQuery: '',
        store: yearRange,
        listeners: {
            'select': function(event, args) {
                ocean.date.setFullYear(event.getValue());
            } 
        }
    });

    initialise();
});

function createCheckBoxes(store, records, result, operation, eOpt) {
    data = [];
    records = store.getById('reynolds').variables().getById('anom').get('average').checkboxes; 
    Ext.each(records, function(rec) {
        var name = rec.name;
//        ocean.dsConf['reynolds'].aveCheck.push(new AveCheck(name, false)); 
        ocean.dsConf['reynolds'].aveCheck[name] = false; 
        Ext.create('Ext.form.field.Checkbox', {
            boxLabel: rec.boxLabel,
            renderTo: 'toggleDiv',
            width: 150,
            name: name,
            id: rec.name,
            handler: function(checkbox, checked) {
                if (checkbox.id == ocean.dataset.mainCheck) {
                    ocean.dataset.aveCheck[checkbox.id] = checked;
                    this.setValue(checked);
                    for (var checkboxId in (ocean.dataset.aveCheck)) {
                        if( checkboxId != checkbox.id) {
                            var checkboxCmp = Ext.getCmp(checkboxId);
                            checkboxCmp.setDisabled(!checked);
                            checkboxCmp.setValue(ocean.dataset.aveCheck[checkboxId]);
                        }
                    }
                    
                    periodCombo = Ext.getCmp('periodCombo');
                    periodCombo.clearValue();
                    var store = periodCombo.store;
                    store.clearFilter(true);
                    if(checked) {
                        store.filter([avePeriodFilter]);
                    }
                    else {
                        store.filter([periodFilter]);
                    }
                    if (store.find('id', ocean.period) != -1) {
                        periodCombo.select(ocean.period);
                    }
                    else {
                        periodCombo.select(store.data.keys[0]);
                        ocean.period = store.data.keys[0];
                    } 
                    updateCalDiv();
                }
                else {
                    ocean.dsConf['reynolds'].aveCheck[checkbox.id] = checked;
                    for (var checkboxId in ocean.dsConf['reynolds'].aveCheck) {
                        if( checkboxId != checkbox.id && checkboxId != ocean.dsConf['reynolds'].mainCheck) {
                            var checkboxCmp = Ext.getCmp(checkboxId);
//                            checkboxCmp.setDisabled(!checked);
                            if (checked) {
                                ocean.dsConf['reynolds'].aveCheck[checkboxId] = !checked;
                                checkboxCmp.setValue(!checked);
                            }
                        }
                    }

                }
            },
            listeners: {
                'beforeshow' : function(event, args) {
                    if (this.id == ocean.dsConf['reynolds'].mainCheck) {
                        this.setValue(ocean.dsConf['reynolds'].aveCheck[this.id]);
                    }
                    else {
                        if (ocean.dsConf['reynolds'].aveCheck[ocean.dsConf['reynolds'].mainCheck]){
                            this.setValue(ocean.dsConf['reynolds'].aveCheck[this.id]);
                        }
                        else {
                            this.setDisabled(true);
//                            Ext.getCmp('runningAveSlider').setDisabled(true);
                        }
                    }
                }
            }
        });
    });
    
    dataArray = new Array();
    for (var i=0; i<records.length; i++) {
        thisItem = new Array();
        thisItem["boxLabel"] = records[i].boxLabel;
        thisItem["name"] = records[i].name;
        dataArray.push(thisItem);
    }

    return data;
}

function selectDataset(event, args) {
    hideControls();
    var selection = event.getValue();
    var record = ocean.datasets.getById(selection);
    ocean.dsConf[selection].data = record;
    ocean.dataset = ocean.dsConf[selection];
    $('#datasettitle').html(record.get('title'))
    varCombo = Ext.getCmp('variableCombo');
    varCombo.setDisabled(false);
    varCombo.bindStore(record.variables());
    varCombo.clearValue();
    
    $('#variableDiv').show();
    configCalendar(); 
};

function configCalendar() {
    if(ocean.calendar) {
        var dateRange = ocean.dataset.data.get('dateRange');
        var minDate = ocean.dataset.data.get('dateRange').minDate;
        ocean.calendar.datepick('option', {'minDate': new Date(minDate.year,
                                                               minDate.month - 1,
                                                               minDate.date),
                                           'maxDate': dateRange.maxDate,
                                           'yearRange': dateRange.minYear + ":" + dateRange.maxYear
                                });
    }
    else {
        createCalendars();
    }
}

//Lazy creation of datepick and month and year combobox.
function createCalendars() {
    var dateRange = ocean.dataset.data.get('dateRange');
    var minDate = ocean.dataset.data.get('dateRange').minDate;
    ocean.calendar = $("#datepicker").datepick({
        minDate: new Date(minDate.year,
                          minDate.month - 1,
                          minDate.date),
        maxDate: dateRange.maxDate,
        yearRange: dateRange.minYear + ":" + dateRange.maxYear,
        dateFormat: 'dd M yyyy',
        firstDay: 1,
        showTrigger: '#calImg',
        renderer: $.extend({},
                  $.datepick.weekOfYearRenderer,
                      {picker: $.datepick.defaultRenderer.picker.
                      replace(/\{link:clear\}/, '').
                      replace(/\{link:close\}/, '')
                   }),
        showOtherMonths: true,
        onSelect: updateDate,
//        onShow: beforeShow,
//        onDate: checkPeriod,
//        onChangeMonthYear: monthOrYearChanged,
//        onClose: closed,
        showOnFocus: false
    });
    $( "#datepicker" ).datepick('setDate', -4);
    $( "#datepicker" ).mousedown(function() {
        $(this).datepick('show');
    })
    
//    ocean.monthCombo = Ext.create('Ext.form.field.ComboBox', {
//        id: 'monthCombo',
//        fieldLabel: 'Month',
//        labelWidth: 20,
//        width: 100,
//        height: 30,
//        rederTo: 'monthDiv',
//        queryMode: 'local',
//        lastQuery: '',
//        store: ['Jan', 'Feb']
//    });

//    ocean.yearCombo = Ext.create('Ext.form.field.ComboBox', {
//        id: 'yearCombo',
//        fieldLabel: 'Year',
//        labelWidth: 20,
//        width: 100,
//        rederTo: 'yearDiv',
//        queryMode: 'local',
//        lastQuery: '',
//        store: ['2011', '2012']
//    });
}

function selectVariable(event, args) {
    hideControls()
    var selection = event.getValue();
    var record = ocean.dataset.data.variables().getById(selection);
    ocean.dataset.variable = record;

    //this should be in a callback for the combo
    periodCombo = Ext.getCmp('periodCombo');
    periodCombo.clearValue();
    var store = periodCombo.store;
    store.clearFilter(true);
    store.filter([periodFilter]);
    if (store.find('id', ocean.period) != -1) {
        periodCombo.select(ocean.period);
    }
    else {
        periodCombo.select(store.data.keys[0]);
        ocean.period = store.data.keys[0];
    } 
    updateCalDiv();
//        select the first one

    //this should be in a callback for the combo
    areaCombo = Ext.getCmp('areaCombo');
    areaCombo.clearValue();
    store = areaCombo.store;
    store.clearFilter(true);
    store.filter([regionFilter]);
    if (store.find('id', ocean.region) != -1) {
        areaCombo.select(ocean.region);
    }
    else {
        areaCombo.select(store.data.keys[0]);
        ocean.region = store.data.keys[0];
    } 
    showControl('selectionDiv');

    if (selection === 'anom') {
        showControl('toggleDiv')
//        Ext.each(ocean.dsConf['reynolds'].aveCheck, function(check) {
//            checkCmp = Ext.getCmp(check);
//            checkCmp.fireEvent('beforeshow', checkCmp);
//        });
        for (var check in ocean.dsConf['reynolds'].aveCheck) {
            checkCmp = Ext.getCmp(check);
            checkCmp.fireEvent('beforeshow', checkCmp);
        }
//        checkCmp = Ext.getCmp(ocean.dsConf['reynolds'].aveCheck);
//        checkCmp.fireEvent('beforeshow', checkCmp);
        showControl('sliderDiv')
    }
};

function selectPeriod(event, args) {
    ocean.period = event.getValue();
    updateCalDiv();
};

function updateCalDiv() {
    if (ocean.period == 'daily' || ocean.period == 'weekly') {
        showControl('datepickerDiv');
        hideControl('yearMonthDiv');
        $("#datepicker").datepick('setDate', new Date(ocean.date))
    }
    else {
        hideControl('datepickerDiv');
        showControl('yearMonthDiv');
        ocean.monthCombo.select(ocean.date.getMonthString());
        ocean.yearCombo.select(ocean.date.getFullYear());
//        $('#yearDiv').val(ocean.date.getFullYear());
    }

}

function selectRegion(event, args) {
    ocean.region = event.getValue();
};

function selectRunningInterval(slider, value, thumb, args) {
    ocean.dataset.runningInterval = value;
};

function hideControls() {
   for (var control in ocean.controls) {
//       document.getElementById(ocean.controls[control]).style.display = 'none';
       $('#' + ocean.controls[control]).hide();
   }
}

function showControl(control) {
//    document.getElementById(control).style.display = 'block';
    $('#' + control).show();
}

function hideControl(control) {
    $('#' + control).hide();
}

function setCompare() {
}

function initialise() {
    $('#variableDiv').hide();
    hideControls();
};

//**********************************************************
//Datepicker setup
//**********************************************************
var average;

function updateDate(dateObj) {
    ocean.date = dateObj.length? dateObj[0] : dateObj;
}

function beforeShow(picker, inst) {
//    if (period == 'monthly' || period == '3monthly' || period == '6monthly') {
//        monthOnly(picker, inst);
//    }
//    else if (period == 'yearly') {
//        yearOnly(picker, inst);
//    }
//    else if (period == 'weekly'){
//        weekOnly(picker, inst);
//    }
}

function checkPeriod() {
//    if (period == 'weekly') {
//        return {selectable: false};
//    }
//    else {
//        return {selectable: true};
//    }
}

function monthOrYearChanged(year, month) {
//    if(average || period == 'yearly') {
//        var target = $('#datepicker');
//        if(period == 'yearly') {
//            target.datepick('setDate', $.datepick.newDate(
//                parseInt(year, 10), 1, 1)).
//                datepick('hide');
//        }
//        else {
//            target.datepick('setDate', $.datepick.newDate(
//                parseInt(year, 10), parseInt(month, 10), 1)).
//                datepick('hide');
//        }
//    }
}


//**********************************************************
//Ajax processing
//**********************************************************
function updatePage() {
    if (!ocean.processing) {
        ocean.processing = true;
        $.ajax({
            url:  ocean.dataset.url(),
            dataType: 'json',
            success: function(data, textStatus, jqXHR) {
                ocean.processing = false;
                if (data != null) {
                    ocean.dataset.callback(data);
                }
            },
            beforeSend: function(jqXHR, settings) {
                $('#mainImg').html('<img src="images/loading.gif" />' + $('#mainImg').html());
            }
        });
    }
}
