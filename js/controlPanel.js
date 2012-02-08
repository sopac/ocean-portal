
var dataset;
var variable;
var month;
var year;

var win;
//var basemapLegend;
////var countryCombo;

var controls = ['selectionDiv', 'toggleDiv']

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
        fields: ['name', 'id', 'periods', 'areas'],
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

    window.runningAveSlider = Ext.create('Ext.slider.Single', {
        renderTo: 'toggleDiv',
        hideLabel: true,
        width: 200,
        minValue: 2,
        maxValue: 15
    });

    initialise();
})

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

//    counter += 1
//    if (counter == 2) {
//        store.clearFilter(true);
//    }
//    store.load().filter();
      store.clearFilter(true);
      store.filter([periodFilter]);
//    store.filter('id', /record.get('periods')/);
//    periodCombo.bindStore(store);
    areaCombo = Ext.getCmp('areaCombo');
    areaCombo.clearValue();
    store = areaCombo.store;
    store.clearFilter(true);
    store.filter([regionFilter]);

    showControl('selectionDiv');
//    areaCombo.bindStore(record.areas());
//    showControl('areaDiv');
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

function setCompare() {
}

function initialise() {
    document.getElementById('variableDiv').visible = false;
    hideControls();
};
