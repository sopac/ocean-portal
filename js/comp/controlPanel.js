/*jslint eqeq: true, forin: true, plusplus: true, undef: true, sloppy: true, sub: true, todo: true, vars: true, white: true, browser: true, windows: true */

var ocean = ocean || {};
ocean.controls = ['selectionDiv', 'toggleDiv', 'sliderDiv', 'yearMonthDiv', 'datepickerDiv', 'latlonDiv', 'tidalGaugeDiv'];
ocean.compare = false;
ocean.processing = false;
//ocean.average = false;
//ocean.trend = false;
//ocean.runningAve = false;
//ocean.runningAveLen = 2;
ocean.MIN_YEAR = 1850;

/* set up JQuery UI elements */
$(document).ready(function() {
    $('.dialog').dialog({ autoOpen: false });

    // Load up the datasets dialog
    html = '';
    $.getJSON('config/comp/datasets.json', function(data) {
        $.each(data, function(k, dataset) {
            html += '<h1>' + dataset.name + '</h1>';
            html += '<ul>';

            $.each(dataset.variables, function(k, variable) {
                html += '<li>' + variable.name + '</li>';
            });

            html += '</ul>';
        });

        $('#about-datasets').html(html);
    });
});

Date.prototype.getMonthString = function() {
    var calMonth = this.getMonth() + 1;
    return (calMonth < 10) ?  ('0' + calMonth) : calMonth + '';
};

ocean.dsConf = {
    reynolds: {url: function() {return "cgi/portal.py?dataset=reynolds"
                   + "&map=" + this.variable.get('id')
                   + "&date=" + $.datepick.formatDate('yyyymmdd', ocean.date)
                   + "&period=" + ocean.period
//                   + "&area=aus"
                   + "&area=" + ocean.area
                   + "&average=" + ocean.dsConf['reynolds'].aveCheck.average
                   + "&trend=" + ocean.dsConf['reynolds'].aveCheck.trend
                   + "&runningAve=" + ocean.dsConf['reynolds'].aveCheck.runningAve
                   + "&runningInterval=" + ocean.dsConf['reynolds'].runningInterval
                   + "&timestamp=" + new Date().getTime();},
                data: null,
                variable: null,
                aveCheck: {},
                mainCheck: 'average',
                runningInterval: 2,
                callback: function(data) {
                    var imgDiv = $('#imgDiv');
                    var dataDiv = $('#dataDiv');
                    var enlargeDiv = $('#enlargeDiv');
                    if (ocean.compare){
                        var imgList = imgDiv.childNodes;
                        imgDiv.removeChild(imgDiv.firstChild);
                        // if (imgList.length >= compareSize) {
                        //     imgDiv.removeChild(imgDiv.lastChild);
                        // }
                        var img = document.createElement("IMG");

			var average = false;
                        if(average) {
                            img.src = data.aveImg;
                            img.width = "680";
                            document.getElementById('aveArea').innerHTML = '<div style="display:inline-block; width:341px; text-align:left">Download data from <a href="' + data.aveData + '" target="_blank">here</a></div>' + '<div style="display:inline-block; width:341px; text-align:right"><b>Average(1981-2010)</b> ' + Math.round(data.mean*100)/100 + '\u00B0C</div>';
                        }
                        else if (data.img != null) {
                            img.src = data.img;
                            img.width = "150";
                            dataDiv.html('');
                        }
                        else {
                            img.src = "images/notavail.png";
                            dataDiv.html('');
                        }
                    }
                    else {
                        if (this.variable.get("id") == "anom" && this.aveCheck.average && data.aveImg != null) {
                            imgDiv.html('<img src="' + data.aveImg + '" width="150" onmouseover="enlargeImg(this, true)" onmouseout="enlargeImg(this, false)"/>');
                            dataDiv.html('<b>Average(1981-2010)</b> ' + Math.round(data.mean*100)/100 + '\u00B0C<br>' + '<a href="'+ data.aveData + '" target="_blank"><img src="images/download.png"/></a>');

                        }
                        else if (data.img != null) {
                            imgDiv.html('<img src="' + data.img + '?time=' + new Date().getTime() + '" width="150" onmouseover="enlargeImg(this, true)" onmouseout="enlargeImg(this, false)"/>');
                            updateMap("Reynolds", data);
                            dataDiv.html('');
                        }
                    }
                },
                onSelect: function(){
                              $('#variableDiv').show();
                              configCalendar(); 
                          },
                onDeselect: function() {
                    layers = map.getLayersByName("Reynolds")
                    for (layer in layers) {
                        map.removeLayer(layers[layer])
                    }
                    $('#imgDiv').html('');
                },
                selectVariable: function(selection) {
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
                    showControl('selectionDiv');

//                    if (selection === 'anom') {
//                        showControl('toggleDiv')
//                        for (var check in ocean.dsConf['reynolds'].aveCheck) {
//                            checkCmp = Ext.getCmp(check);
//                            checkCmp.fireEvent('beforeshow', checkCmp);
//                        }
//                        showControl('sliderDiv')
//                    }
                }
            },
    ersst: {url: function() {return "cgi/portal.py?dataset=ersst"
                   + "&map=" + this.variable.get('id')
                   + "&date=" + $.datepick.formatDate('yyyymmdd', ocean.date)
                   + "&period=" + ocean.period
                   + "&baseYear=1900"
                   + "&area=" + ocean.area
                   + "&average=" + ocean.dsConf['ersst'].aveCheck.average
                   + "&trend=" + ocean.dsConf['ersst'].aveCheck.trend
                   + "&runningAve=" + ocean.dsConf['ersst'].aveCheck.runningAve
                   + "&runningInterval=" + ocean.dsConf['ersst'].runningInterval
                   + "&timestamp=" + new Date().getTime();},
                data: null,
                variable: null,
                aveCheck: {},
                mainCheck: 'average',
                runningInterval: 2,
                callback: function(data) {
                    var imgDiv = $('#imgDiv');
                    var dataDiv = $('#dataDiv');
                    var enlargeDiv = $('#enlargeDiv');
                    if (this.variable.get("id") == "anom" && this.aveCheck.average && data.aveImg != null) {
                        imgDiv.html('<img src="' + data.aveImg + '" width="150" onmouseover="enlargeImg(this, true)" onmouseout="enlargeImg(this, false)"/>');
                        dataDiv.html('<b>Average(1981-2010)</b> ' + Math.round(data.mean*100)/100 + '\u00B0C<br>' + '<a href="'+ data.aveData + '" target="_blank"><img src="images/download.png"/></a>');

                    }
                    else if (data.img != null) {
                        imgDiv.html('<img src="' + data.img + '?time=' + new Date().getTime() + '" width="150" onmouseover="enlargeImg(this, true)" onmouseout="enlargeImg(this, false)"/>');
                        updateMap("ERSST", data);
                        dataDiv.html('');
                    }
                },
                onSelect: function(){
                              $('#variableDiv').show();
                              configCalendar();
                          },
                onDeselect: function() {
                    layers = map.getLayersByName("ERSST")
                    for (layer in layers) {
                        map.removeLayer(layers[layer])
                    }
                    $('#imgDiv').html('');
                },
                selectVariable: function(selection) {
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
                    showControl('selectionDiv');

//                    if (selection === 'anom') {
//                        showControl('toggleDiv')
//                        for (var check in ocean.dsConf['reynolds'].aveCheck) {
//                            checkCmp = Ext.getCmp(check);
//                            checkCmp.fireEvent('beforeshow', checkCmp);
//                        }
//                        showControl('sliderDiv')
//                    }
                }
           },
    bran: {url: function() {return "cgi/portal.py?dataset=bran"
                                + "&timestamp=" + new Date().getTime();
                           },
            data: null,
            callback: function(data) {
            },
            onSelect: function() {
                      },
            onDeselect: function() {
                            $('#imgDiv').html('');
                            $('#dataDiv').html('');
                        },
            selectVariable: function(selection) {
            }
    },
    ww3: {url: function() {return "cgi/portal.py?dataset=ww3"
                                + "&lllat=" + document.forms['theform'].elements['latitude'].value 
                                + "&lllon=" + document.forms['theform'].elements['longitude'].value
                                + "&urlat=" + document.forms['theform'].elements['latitude'].value
                                + "&urlon=" + document.forms['theform'].elements['longitude'].value
                                + "&variable=" + this.variable.get('id') 
                                + "&timestamp=" + new Date().getTime();
                           },
            data: null,
            panelControls: null,
            toolbar: null,
            callback: function(data) {
                          var imgDiv = $('#imgDiv');
                          var dataDiv = $('#dataDiv');
                          if(data.ext != null) {
                              dataDiv.html('<a href="'+ data.ext + '" target="_blank"><img src="images/download.png"/></a>');
                              imgDiv.html('<img src="' + data.img + '?time=' + new Date().getTime() + '" width="150" onmouseover="enlargeImg(this, true)" onmouseout="enlargeImg(this, false)"/>');
                          }
                      },
            onSelect: function() {var ww3Layer = new OpenLayers.Layer.Vector("WaveWatch III", {
                                                         preFeatureInsert: function(feature) {
                                                             this.removeAllFeatures();
                                                         },
                                                         onFeatureInsert: function(feature) {
                                                             var geometry = feature.geometry;
                                                             document.forms['theform'].elements['latitude'].value = Math.round(geometry.y * 1000)/1000;
                                                             document.forms['theform'].elements['longitude'].value = Math.round(geometry.x * 1000)/1000;
                                                         }
                                                     });
                                  ocean.mapObj.addLayer(ww3Layer);
                                  this.panelControls = [
                                      new OpenLayers.Control.DrawFeature(ww3Layer,
                                                       OpenLayers.Handler.Point,
                                                       {'displayClass': 'olControlDrawFeaturePoint'}),
                                      new OpenLayers.Control.Navigation()
                                  ];
                                  this.toolbar = new OpenLayers.Control.Panel({
                                      displayClass: 'olControlEditingToolbar',
                                      defaultControl: this.panelControls[0]
                                  });
                                  this.toolbar.addControls(this.panelControls);
                                  ocean.mapObj.addControl(this.toolbar);
////                                  var boxControl = new OpenLayers.Control.DrawFeature(ww3Layer,
////                                                       OpenLayers.Handler.Point);
//                                                       OpenLayers.Handler.RegularPolygon, 
//                                                       {
//                                                           handlerOptions: {
//                                                               sides: 4
//                                                           }
//                                                       });
////                                  ocean.mapObj.addControl(boxControl);
////                                  boxControl.activate(); 
                                  $('#variableDiv').show();
                                 },
            onDeselect: function() {
                            var layers = map.getLayersByName("WaveWatch III");
			    var layer;
			    var control;

                            for (layer in layers) {
                                map.removeLayer(layers[layer]);
                            }
                            map.removeControl(this.toolbar);
                            this.toolbar.deactivate();
                            this.toolbar.destroy();

                            for (control in this.panelControls) {
                                map.removeControl(this.panelControls[control]);
                                this.panelControls[control].deactivate();
                                this.panelControls[control].destroy();
                            }
                            $('#imgDiv').html('');
                            $('#dataDiv').html('');
                                   },
            selectVariable: function(selection) {
                                $('#latlonDiv').show();
                            }
    },
    sealevel: {url: function() {return "cgi/portal.py?dataset=sealevel"
                                + "&variable=" + this.variable.get('id')
                                + "&period=" + ocean.period
                                + "&date=" + $.datepick.formatDate('yyyymmdd', ocean.date)
                                + "&area=" + ocean.area
                                + "&lat=" + document.forms['theform'].elements['latitude'].value 
                                + "&lon=" + document.forms['theform'].elements['longitude'].value
                                + "&tidalGaugeId=" + document.forms['theform'].elements['tgId'].value
                                + "&timestamp=" + new Date().getTime();
                           },
            data: null,
            callback: function(data) {
                var imgDiv = $('#imgDiv');
                var dataDiv = $('#dataDiv');
                var enlargeDiv = $('#enlargeDiv');
                if (data.img != null) {
		    var img;

                    imgDiv.html('');
                    for (img in data.img) {
                        imgDiv.html(imgDiv.html() + '<img src="' + data.img[img] + '?time=' + new Date().getTime() + '" width="150" onmouseover="enlargeImg(this, true)" onmouseout="enlargeImg(this, false)"/>');
                    }
                    updateSeaLevelMap(data);
                }
                dataDiv.html('');
                if(data.tid != null) {
                    dataDiv.html('<a href="'+ data.tid + '" target="_blank">Tidal Gauge Data</a><br/>');
                }
                if(data.alt != null) {
                    dataDiv.html(dataDiv.html() + '<a href="'+ data.alt + '" target="_blank">Altimetry Data</a><br/>');
                }
                if(data.rec!= null) {
                    dataDiv.html(dataDiv.html() + '<a href="'+ data.rec + '" target="_blank">Reconstruction Data</a><br/>');
                }
            },
            onSelect: function() {
                          var gaugesLayer = new OpenLayers.Layer.Vector("Tidal gauges", {
                              strategies: [new OpenLayers.Strategy.BBOX({resFactor: 1.1})],
                              protocol: new OpenLayers.Protocol.HTTP({
                                  url: "config/comp/tidalGauges.txt",
                                  format: new OpenLayers.Format.Text()
                              }),
                              'calculateInRange' : function() { return true;}
                          });
//                          gaugesLayer.display(false)
                          ocean.mapObj.addLayer(gaugesLayer);
                          gaugesLayer.redraw(true);
                          var gaugeControl = new OpenLayers.Control.SelectFeature(gaugesLayer, {
                              clickout: true,
                              multiple: false,
                              toggle: true,
                              hover: true,
                              highlightOnly: false
                          });
                          map.addControl(gaugeControl);
                          gaugeControl.activate();
                          gaugesLayer.events.on({
                              'featureselected': function(event) {
                                  gauge = event.feature;
                                  geometry = gauge.geometry.getBounds().getCenterLonLat();
                                  document.forms['theform'].elements['tidalgauge'].value = gauge.attributes.title;
                                  document.forms['theform'].elements['tgId'].value = gauge.attributes.description;
                                  document.forms['theform'].elements['latitude'].value = Math.round(geometry.lat * 1000)/1000;
                                  document.forms['theform'].elements['longitude'].value = Math.round(geometry.lon * 1000)/1000;
                              }
                          });
                          $('#variableDiv').show();
                      },
            onDeselect: function() {
                            var layers = map.getLayersByName("Sea Level");
			    var layer;
			    var control;

                            for (layer in layers) {
                                map.removeLayer(layers[layer]);
                            }

                            layers = map.getLayersByName("Tidal gauges");
                            for (layer in layers) {
                                map.removeLayer(layers[layer]);
                            }

                            var controls = map.getControlsByClass("OpenLayers.Control.SelectFeature");
                            for (control in controls) {
                                map.removeControl(controls[control]);
                                controls[control].deactivate();
                                controls[control].destroy();
                            }
                            $('#imgDiv').html('');
                            $('#dataDiv').html('');
                        },
            selectVariable: function(selection) {
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
                var record = this.data.variables().getById(selection);
                var maxDate = new Date();
                if (record.get("dateRange") != null) {
                    maxDate.setMonth(record.get("dateRange")["maxDate"]["month"] - 1);
                    maxDate.setFullYear(record.get("dateRange")["maxDate"]["year"]);
                    maxDate.setDate(record.get("dateRange")["maxDate"]["date"]);
                }
     
                ocean.date = maxDate;
                updateCalDiv();
                showControl('selectionDiv');
                $('#tidalGaugeDiv').show();
//                $('#latlonDiv').show();
            }
    }

};

function enlargeImg(img, show) {
    var enlargeDiv = $('#enlargeDiv');
    if (show) {
        enlargeDiv.html('<img src="' + img.src + ' "width="650"/>');
    }
    else {
        enlargeDiv.html('');
    }
}


function loadingImg(show) {
    var enlargeDiv = $('#loadingDiv');
    if (show) {
        enlargeDiv.html('<img src="' + img.src + ' "width="650"/>');
    }
    else {
        enlargeDiv.html('');
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

//    Ext.define('Category', {
//        extend: 'Ext.data.Model',
//        fields: ['name', 'id', 'dataset'],
//        idProperty: 'id',
//        proxy: {
//            type: 'ajax',
//            url: 'config/categories.json',
//            reader: {
//                type: 'json'
//            }
//        }
//    });

    Ext.define('Dataset', {
        extend: 'Ext.data.Model',
        fields: ['name', 'id', 'title', 'help', 'dateRange'],
        idProperty: 'id',
        hasMany: {model:'Variable', name: 'variables'},
        proxy: {
            type: 'ajax',
            url: 'config/comp/datasets.json',
            reader: {
                type: 'json'
            }
        }
    });
   
    Ext.define('Variable', {
        extend: 'Ext.data.Model',
        idProperty: 'id',
        fields: ['name', 'id', 'periods', 'areas', 'average', 'dateRange'],
        belongsTo: 'Dataset'
    });

    Ext.define('Period', {
        extend: 'Ext.data.Model',
        idProperty: 'id',
        fields: ['name', 'id'],
        proxy: {
            type: 'ajax',
            url: 'config/comp/period.json',
            reader: {
                type: 'json'
            }
        }
    });

//    ocean.categories = Ext.create('Ext.data.Store', {
//        autoLoad: true,
//        model: 'Category'
//    });

    ocean.datasets = Ext.create('Ext.data.Store', {
        autoLoad: true,
        model: 'Dataset'
    });
    ocean.datasets.addListener('load', createCheckBoxes);

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
    }

    avePeriodFilter = Ext.create('Ext.util.Filter', {filterFn: aveFilterPeriod});
    function aveFilterPeriod(item){
        if(ocean.dataset.variable.get("average")) {
            return Ext.Array.contains(ocean.dataset.variable.get("average").periods, item.get('id'));
        }
        else {
            return true;
        }
    }

    regionFilter = Ext.create('Ext.util.Filter', {filterFn: filterRegion});
    function filterRegion(item){
        if(ocean.dataset.variable) {
            return Ext.Array.contains(ocean.dataset.variable.get('areas'), item.get('id'));
        }
        else {
            return true;
        }
    }

//    ocean.categoryCombo = Ext.create('Ext.form.field.ComboBox', {
//        id: 'categoryCombo',
//        fieldLabel: 'Category',
//        labelWidth: 50,
//        width: 100,
//        displayField: 'name',
 //       valueField: 'id',
//        rederTo: 'categoryDiv',
//        store: ocean.categories,
//        queryMode: 'local',
//        listeners: {
//            'select': selectCategory
//        }
//    });

    var hbox = Ext.create('Ext.container.Container', {
        layout: {
            type: 'hbox'
        },
        renderTo: 'datasetDiv',
        width: 185
    });

    ocean.datasetCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'datasetCombo',
        fieldLabel: 'Dataset',
        labelWidth: 50,
        width: 155,
        displayField: 'name',
        valueField: 'id',
        store: ocean.datasets,
        queryMode: 'local',
        listeners: {
            'select': selectDataset
        }
    });
    hbox.add(ocean.datasetCombo);

    hbox.add(Ext.create('Ext.Button', {
        html: '<span class="ui-icon ui-icon-help" title="About Datasets"></span>',
        margin: { left: 2 },
        handler: function() {
            $('#about-datasets').dialog('open');
        }
    }));

    ocean.mapCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'variableCombo',
        fieldLabel: 'Variable',
        labelWidth: 50,
        width: 155,
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
        width: 155,
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

    ocean.runningAveSlider = Ext.create('Ext.slider.Single', {
        renderTo: 'sliderDiv',
        hideLabel: true,
        id: 'runningAveSlider',
        width: 155,
        minValue: 2,
        maxValue: 15,
        listeners: {
            'changecomplete': selectRunningInterval
        }
    });

//    ocean.plotComp = Ext.create('Ext.form.field.Checkbox', {
//            boxLabel: 'Plot Comparision',
//            renderTo: 'compDiv',
//            width: 150,
//            name: 'plotComp',
//            id: 'plotComp'});
//    ocean.plotComp.setDisabled(true);

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
        width: 155,
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
        width: 155,
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
            width: 155,
            name: name,
            id: rec.name,
            handler: function(checkbox, checked) {
                if (checkbox.id == ocean.dataset.mainCheck) {
		    var checkboxId;

                    ocean.dataset.aveCheck[checkbox.id] = checked;
                    this.setValue(checked);
                    for (checkboxId in (ocean.dataset.aveCheck)) {
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
                    for (checkboxId in ocean.dsConf['reynolds'].aveCheck) {
                        if( checkboxId != checkbox.id && checkboxId != ocean.dsConf['reynolds'].mainCheck) {
                            checkboxCmp = Ext.getCmp(checkboxId);
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

    var i;
    for (i=0; i<records.length; i++) {
        thisItem = new Array();
        thisItem["boxLabel"] = records[i].boxLabel;
        thisItem["name"] = records[i].name;
        dataArray.push(thisItem);
    }

    return data;
}
 
function selectCategory(event, args) {
}

function selectDataset(event, args) {
    hideControls();
    var selection = event.getValue();
    var record = ocean.datasets.getById(selection);
    ocean.dsConf[selection].data = record;

    if (ocean.dataset != null) {
        ocean.dataset.onDeselect();
    }

    ocean.dataset = ocean.dsConf[selection];
    $('#dstitle').html(record.get('title'));
    $('#dshelp').html('Help File');
    $('#dshelp').attr('href', record.get('help'));
    varCombo = Ext.getCmp('variableCombo');
    varCombo.setDisabled(false);
    varCombo.bindStore(record.variables());
    varCombo.clearValue();

    ocean.dataset.onSelect();
}

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
    });

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
    hideControls();
    var selection = event.getValue();
    var record = ocean.dataset.data.variables().getById(selection);
    ocean.dataset.variable = record;
    ocean.dataset.selectVariable(selection);

}

function selectPeriod(event, args) {
    ocean.period = event.getValue();
    updateCalDiv();
}

function updateCalDiv() {
    if (ocean.period == 'daily' || ocean.period == 'weekly') {
        showControl('datepickerDiv');
        hideControl('yearMonthDiv');
        $("#datepicker").datepick('setDate', new Date(ocean.date));
    }
    else {
        hideControl('datepickerDiv');
        showControl('yearMonthDiv');
        ocean.monthCombo.select(ocean.date.getMonthString());
        ocean.yearCombo.select(ocean.date.getFullYear());
//        $('#yearDiv').val(ocean.date.getFullYear());
    }

}

function selectRunningInterval(slider, value, thumb, args) {
    ocean.dataset.runningInterval = value;
}

function hideControls() {
   var control;
   for (control in ocean.controls) {
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
    hideControl('loadingDiv');
}

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
            beforeSend: function(jqXHR, settings) {
                showControl('loadingDiv');
                hideControl('errorDiv');
            },
            success: function(data, textStatus, jqXHR) {
		hideControl('loadingDiv');
                if (data != null) {
                    if (data.error) {
                        $('#errorDiv').html(data.error);
                        showControl('errorDiv');
                    }
                    else {
                        ocean.dataset.callback(data);
                    }
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert(textStatus);
            },
            complete: function(jqXHR, textStatus) {
                ocean.processing = false;
                hideControl('loadingDiv');
            } 
        });
    }
}
