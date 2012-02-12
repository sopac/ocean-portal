var ocean = ocean || {};
var dataset;
var variable;
var month;
var year;

var win;

var controls = ['selectionDiv', 'toggleDiv', 'sliderDiv', 'yearMonthDiv']

Ext.require(['*']);
Ext.onReady(function() {
    Ext.Loader.setConfig({enabled:true});

    Ext.define('Dataset', {
        extend: 'Ext.data.Model',
        fields: ['name', 'id', 'title'],
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

    window.regions = Ext.create('Ext.data.Store', {
        autoLoad: true,
        model: 'Region'
    });

    window.periods = Ext.create('Ext.data.Store', {
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

    window.datasetCombo = Ext.create('Ext.form.field.ComboBox', {
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

    window.mapCombo = Ext.create('Ext.form.field.ComboBox', {
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

    window.periodCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'periodCombo',
        fieldLabel: 'Period',
        labelWidth: 50,
        width: 150,
        displayField: 'name',
        valueField: 'id',
        renderTo: 'selectionDiv',
        triggerAction: 'all',
        queryMode: 'local',
        store: window.periods,
        lastQuery: '',
        listeners: {
            'select': selectPeriod
        }
    });

    window.areaCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'areaCombo',
        fieldLabel: 'Area',
        labelWidth: 50,
        width: 250,
        displayField: 'name',
        valueField: 'id',
        renderTo: 'selectionDiv',
        queryMode: 'local',
        store: window.regions,
        listeners: {
            'select': selectArea
        }
    });

    window.runningAveSlider = Ext.create('Ext.slider.Single', {
        renderTo: 'sliderDiv',
        hideLabel: true,
        width: 200,
        minValue: 2,
        maxValue: 15
    });

    initialise();
});

function createCheckBoxes(store, records, result, operation, eOpt) {
    checkboxes = parseCheckBoxes(store);
    var boxes = [
                {boxLabel: 'Item 1', name: 'cb-col-1'},
                {boxLabel: 'Item 2', name: 'cb-col-2', checked: true},
                {boxLabel: 'Item 3', name: 'cb-col-3'}
            ]
    var bbb = [{"boxLabel": "aaa", "name": "aaaname"}, {"boxLabel": "bbb", "name": "bbbname"}]
}

function parseCheckBoxes(store) {
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
    dataset = record;
    document.getElementById('datasettitle').innerHTML = record.get('title')
    varCombo = Ext.getCmp('variableCombo');
    varCombo.setDisabled(false);
    varCombo.bindStore(record.variables());
    varCombo.clearValue();
    
};

var counter = 0;
function selectVariable(event, args) {
    hideControls()
    var selection = event.getValue();
    var record = dataset.variables().getById(selection);
    variable = record;
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
   for (var control in controls) {
       document.getElementById(controls[control]).style.display = 'none';
   }
}

function showControl(control) {
    document.getElementById(control).style.display = 'block';
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
$(function() {
    $("#datepicker").datepick({
        minDate: new Date(1981, 9 - 1, 1),
        maxDate: '-4D',
        yearRange: '1981:2013',
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
});


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


