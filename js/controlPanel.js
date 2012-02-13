var ocean = ocean || {};
ocean.controls = ['selectionDiv', 'toggleDiv', 'sliderDiv', 'yearMonthDiv']

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
        if(ocean.variable) {
            return Ext.Array.contains(ocean.variable.get('periods'), item.get('id'));
        }
        else {
            return true;
        }
    };

    regionFilter = Ext.create('Ext.util.Filter', {filterFn: filterRegion});
    function filterRegion(item){
        if(ocean.variable) {
            return Ext.Array.contains(ocean.variable.get('areas'), item.get('id'));
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
            'select': selectArea
        }
    });

    ocean.runningAveSlider = Ext.create('Ext.slider.Single', {
        renderTo: 'sliderDiv',
        hideLabel: true,
        width: 200,
        minValue: 2,
        maxValue: 15
    });

    ocean.plotComp = Ext.create('Ext.form.field.Checkbox', {
            boxLabel: 'Plot Comparision',
            renderTo: 'compDiv',
            width: 150,
            name: 'plotComp',
            id: 'plotComp'});
    initialise();
});

function createCheckBoxes(store, records, result, operation, eOpt) {
    data = [];
    records = store.getById('reynolds').variables().getById('anom').get('average').checkboxes; 
    Ext.each(records, function(rec) {
        Ext.create('Ext.form.field.Checkbox', {
            boxLabel: rec.boxLabel,
            renderTo: 'toggleDiv',
            width: 150,
            name: rec.name,
            id: rec.name});
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
    ocean.dataset = record;
    document.getElementById('datasettitle').innerHTML = record.get('title')
    varCombo = Ext.getCmp('variableCombo');
    varCombo.setDisabled(false);
    varCombo.bindStore(record.variables());
    varCombo.clearValue();
    
    configCalendar(); 
};

function configCalendar() {
    if(ocean.calendar) {
        var dateRange = ocean.dataset.get('dateRange');
        var minDate = ocean.dataset.get('dateRange').minDate;
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
    var dateRange = ocean.dataset.get('dateRange');
    var minDate = ocean.dataset.get('dateRange').minDate;
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
//        onSelect: setDate,
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
//        rederTo: 'monthDiv',
//        queryMode: 'local',
//        lastQuery: '',
//        store: ocean.dataset.
//        listeners: {
//        }
//    });
}

function selectVariable(event, args) {
    hideControls()
    var selection = event.getValue();
    var record = ocean.dataset.variables().getById(selection);
    ocean.variable = record;
    periodCombo = Ext.getCmp('periodCombo');
    periodCombo.clearValue();
    var store = periodCombo.store;
    store.clearFilter(true);
    store.filter([periodFilter]);
    areaCombo = Ext.getCmp('areaCombo');
    areaCombo.clearValue();
    store = areaCombo.store;
    store.clearFilter(true);
    store.filter([regionFilter]);
    showControl('selectionDiv');

    if (selection === 'anom') {
        showControl('toggleDiv')
        showControl('sliderDiv')
    }
};

function selectPeriod(event, args) {
};

function selectArea(event, args) {
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
    document.getElementById(control).style.display = 'block';
}

function setCompare() {
}

function initialise() {
    document.getElementById('variableDiv').visible = false;
    hideControls();
};

//**********************************************************
//Datepicker setup
//**********************************************************
var average;

function setDate(dateObj) {
//    dateInstance = dateObj
//    if (average) {
//        if (period == 'monthly'){
//            date = $.datepick.formatDate('mm', dateInstance[0]);
//        }
//        else {
//            date = $.datepick.formatDate('yyyy', dateInstance[0]);
//        }
//    }
//    else {
//        date = $.datepick.formatDate('yyyymmdd', dateInstance[0]);
//    }
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


