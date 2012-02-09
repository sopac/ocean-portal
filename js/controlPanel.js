
var dataset;
var variable;
var month;
var year;

var win;
//var basemapLegend;
////var countryCombo;

var controls = ['selectionDiv', 'toggleDiv', 'sliderDiv']

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

    window.datasets = Ext.create('Ext.data.Store', {
        autoLoad: true,
        model: 'Dataset'
    });
    window.datasets.addListener('load', createCheckBoxes);

    window.regions = Ext.create('Ext.data.Store', {
        autoLoad: true,
        model: 'Region'
    });

    window.periods = Ext.create('Ext.data.Store', {
        autoLoad: true,
        model: 'Period'
//        filters: [
//            Ext.create('Ext.util.Filter', {
//                filterFn: filterPeriod
//        })]
    });

    periodFilter = Ext.create('Ext.util.Filter', {filterFn: filterPeriod});
    function filterPeriod(item){
        if(variable) {
            return Ext.Array.contains(variable.get('periods'), item.get('id'));
        }
        else {
            return true;
        }
    };

    regionFilter = Ext.create('Ext.util.Filter', {filterFn: filterRegion});
    function filterRegion(item){
        if(variable) {
            return Ext.Array.contains(variable.get('areas'), item.get('id'));
        }
        else {
            return true;
        }
    };
//    window.datasets.load();
//    window.regions.load();
//    window.periods.load();

//    window.datasets = new ext.data.store({
//        model: 'dataset'
//    });

    window.datasetCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'datasetCombo',
        fieldLabel: 'Dataset',
        labelWidth: 50,
        width: 150,
        displayField: 'name',
        valueField: 'id',
        renderTo: 'datasetDiv',
        store: window.datasets,
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
        store: window.datasets,
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
//        renderTo: 'areaDiv',
        queryMode: 'local',
        store: window.regions,
        listeners: {
            'select': selectArea
        }
    });

//    window.averageCheckboxGroup = Ext.create('Ext.form.CheckboxGroup', {
////        fieldLabel: '',
//        renderTo: 'toggleDiv',
//        width: 300,
//        height: 300,
//        items: [{"boxLabel": "aaa", "name": "aaaname"}, {"boxLabel": "bbb", "name": "bbbname"}]
//    }); 

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
////    window.averageCheckboxGroup = Ext.create('Ext.form.CheckboxGroup', {
////        fieldLabel: '',
////        renderTo: 'toggleDiv',
//        layout: 'vbox',
//
////        columns: 1,
////        width: 300,
////        height: 70,
//        items: [{"boxLabel": "aaa", "name": "aaaname"}, {"boxLabel": "bbb", "name": "bbbname"}]
////        items: checkboxes
////    }); 
////    window.averageCheckboxGroup.show();

    //can't put here otherwise the rendering will have disabled 1 in front of the slider
//    window.runningAveSlider = Ext.create('Ext.slider.Single', {
//        renderTo: 'sliderDiv',
//        hideLabel: true,
//        width: 200,
//        minValue: 2,
//        maxValue: 15
//    });
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
    var record = window.datasets.getById(selection);
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
