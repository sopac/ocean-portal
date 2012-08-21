    <!-- this is a test to use different navigate control-->
//    OpenLayers.ImgPath = "http://js.mapbox.com/theme/dark/";
    var ocean = ocean || {};
    var popup;
    var map = new OpenLayers.Map("map", {
        resolutions: [0.087890625,0.0439453125,0.02197265625,0.010986328125,0.0054931640625,0.00274658203125,0.00137329101],
        maxResolution: 0.087890625, 
        minExtent: new OpenLayers.Bounds(-1, -1, -1, -1),
        maxExtent: new OpenLayers.Bounds(-180, -90, 180, 90),
        restrictedExtent: new OpenLayers.Bounds(-254.75303, -51.78606, -144.49137, 20.13191),
        controls: [
            new OpenLayers.Control.PanZoomBar(),
            new OpenLayers.Control.MousePosition(),
            new OpenLayers.Control.LayerSwitcher({"ascending": false}),
            new OpenLayers.Control.KeyboardDefaults(),
            new OpenLayers.Control.ScaleLine({bottomOutUnits:'', bottomInUnits:''}),
            new OpenLayers.Control.Navigation({dragPanOptions: {enableKinetic: true}})
        ],
        eventListeners: {
           "changebaselayer": mapBaseLayerChanged
        }
    });
    ocean.mapObj = map;


    var wmsLayer = new OpenLayers.Layer.WMS("Plain World",
        'cgi/getMap',
        {
	    map: "plainworld",
            layers: "land,urban,ocean,maritime,country_line,major_countries,minor_countries,cities,towns,minor_islands"
        },{
            wrapDateLine: true,
            transitionEffect: 'resize'
        }
    );


////Below are the MapServer layers

    var bathymetryLayer = new OpenLayers.Layer.MapServer("Bathymetry",
        'cgi/getMap', {
            map: "bathymetry",
            layers: ["bathymetry_10000", "bathymetry_9000", "bathymetry_8000",
                     "bathymetry_7000", "bathymetry_6000", "bathymetry_5000",
                     "bathymetry_4000", "bathymetry_3000", "bathymetry_2000",
                     "bathymetry_1000", "bathymetry_200", "bathymetry_0",
                     "land", "maritime", "capitals", "countries"]
//            layers: ["coastline", "populated_places", "ocean"]
        }, {
            wrapDateLine: true
//            maxResolution: 0.0000453613
        });

    var sstLayer = new OpenLayers.Layer.MapServer("SST",
        'cgi/getMap', {
//            map: "sst",
            map: "reynolds",
            layers: ["sst_left", "sst_right", "land", "coastline"]
        }, {
            wrapDateLine: true
//            maxResolution: 0.0000453613
        });

    function centerMap() {
        if (map) {
//            map.setCenter(new OpenLayers.LonLat(-178.48551, -13.11418), 0);
            map.setCenter(new OpenLayers.LonLat(173.00000, -13.11418), 0);
//            gaugesLayer.setVisibility(true);
        }
    }
    
    //Add gauge points
    map.addLayers([bathymetryLayer]);
    map.setBaseLayer(bathymetryLayer)
   // map.panTo(new OpenLayers.LonLat(178.62740, -17.93307));
    function mapBaseLayerChanged(evt) {
        layerName = evt.layer.name;
        var legendDiv = $('#legendDiv')
        if (window.basemapLegend) {
            if (layerName == 'Bathymetry') {
//                legendPanel.update("<p><b>Bathymetry (m)</b></p><br/><img src='images/bathymetry_ver.png' height='200'/>");
                legendDiv.html("<p><b>Bathymetry (m)</b></p><br/><img src='images/bathymetry_ver.png' height='200'/>")
           //     basemapLegend.setSrc('images/bathymetry_ver.png'); 
           //     basemapLegend.setSize(40, 250);
            }     
            else if (layerName == 'SST') {
//                legendPanel.update("<p><b>Temperature (&deg;C)</b></p><br/><img src='images/sst.png' height='200'/>");
                legendDiv.html("<p><b>Temperature (&deg;C)</b></p><br/><img src='images/sst.png' height='200'/>")
           //     basemapLegend.setSrc('images/sst.png');
           //     basemapLegend.setSize(40, 250);
            }
            else {
//                legendPanel.update("<p></p>");
                legendDiv.html("<p></p>")
          //      basemapLegend.html="<p>hello</p>";
          //      basemapLegend.setSrc('images/blank.png');
         //       basemapLegend.setSize(1, 1);
            }
        }
    } 

function selectCountry(event, args) {
    var selection = event.getValue();
    var record = window.countryStore.getById(selection);
    var zoom = record.get('zoom');
    map.zoomTo(zoom);
    map.panTo(new OpenLayers.LonLat(record.get('long'), record.get('lat')));


    ocean.area = selection;
};

//this is a callback funtion, invoked when Extjs loading is finished
function setupControls() {
    window.countryCombo.on('select', selectCountry, this);
    window.countryCombo.on('change', selectCountry, this);
//    window.countryCombo.select('pac');
};

function updateMap(data){
    if (map.getLayersByName("Reynolds").length != 0) {
        layer = map.getLayersByName("Reynolds")[0]
        map.setBaseLayer(layer)
        layer.params["raster"] = [data.mapeast, data.mapeastw, data.mapwest, data.mapwestw]
        layer.redraw(true)
    }
    else{
        var sstLayer = new OpenLayers.Layer.MapServer("Reynolds",
            "cgi/getMap", {
	    map: 'reynolds',
            layers: ["sst_left", "sst_right", "land", "coastline"],
            raster: [data.mapeast, data.mapeastw, data.mapwest, data.mapwestw]
        }, {
            wrapDateLine: true
        });

//        var sstLayer = new OpenLayers.Layer.Image("SST",
//            "http://tuscany/dev/data/comp/raster/left.png",
//            new OpenLayers.Bounds(180, -90, 360, 90),
//            new OpenLayers.Size(720, 720),
//            {numZoomLevels: 5});

        map.addLayer(sstLayer)
        map.setBaseLayer(sstLayer)
    }
}


function updateSeaLevelMap(data){
    if (map.getLayersByName("Sea Level").length != 0) {
        layer = map.getLayersByName("Sea Level")[0]
        map.setBaseLayer(layer)
        layer.params["raster"] = [data.mapeast, data.mapeastw, data.mapwest, data.mapwestw]
        layer.redraw(true)
    }
    else{
        var slLayer = new OpenLayers.Layer.MapServer("Sea Level",
            "cgi/getMap", {
	    map: 'sealevel',
            layers: ["sl_left", "sl_right", "land", "coastline"],
            raster: [data.mapeast, data.mapeastw, data.mapwest, data.mapwestw]
        }, {
            wrapDateLine: true
        });

//        var sstLayer = new OpenLayers.Layer.Image("SST",
//            "http://tuscany/dev/data/comp/raster/left.png",
//            new OpenLayers.Bounds(180, -90, 360, 90),
//            new OpenLayers.Size(720, 720),
//            {numZoomLevels: 5});

        map.addLayer(slLayer)
        map.setBaseLayer(slLayer)
    }
}
/*
This file is part of Ext JS 4

Copyright (c) 2011 Sencha Inc

Contact:  http://www.sencha.com/contact

GNU General Public License Usage
This file may be used under the terms of the GNU General Public License version 3.0 as published by the Free Software Foundation and appearing in the file LICENSE included in the packaging of this file.  Please review the following information to ensure the GNU General Public License version 3.0 requirements will be met: http://www.gnu.org/copyleft/gpl.html.

If you are unsure which license is appropriate for your use, please contact the sales department at http://www.sencha.com/contact.

*/
var win;
//var basemapLegend;
//var countryCombo;

Ext.require(['*']);
Ext.onReady(function() {
    //define model and data store
//     Ext.define(':


    //define information window
    if (!win) {
        win = Ext.create('Ext.window.Window', {
            closable: true,
            closeAction: 'hide',
            width: 600,
            height: 350,
            layout: 'border',
            borderStyle: 'padding: 2px',
            items: [{
                region: 'center',
                xtype: 'tabpanel',
                items: [{
                    title: 'General Info'
                }, {
                    title: 'Altimetry'
                }, {
                    title: 'Reconstruction'
                }, {
                    title: 'Tidal Gauge Network'
                }]
            }]
        }); 
    }

//    var regionsGroup = {
//        xtype: 'fieldset',
 //       title: 'Regions',
//        collapsible: true,
//        items: [
//            {xtype: 'radiogroup',
//             fieldLabel: 'Regions',
//             columns: 1,
//             items: [
//                 {boxLabel: 'Cook Islands', name: 'regions', inputValue: 'cookislands'},
//                 {boxLabel: 'Federated States of Micronesia', name: 'regions', inputValue: 'fsm'},
//                 {boxLabel: 'Fiji', name: 'regions', inputValue: 'fiji', checked: true},
//                 {boxLabel: 'Kiribati', name: 'regions', inputValue: 'kiribati'},
//                 {boxLabel: 'Marshall Islands', name: 'regions', inputValue: 'marshall'},
//                 {boxLabel: 'Nauru', name: 'regions', inputValue: 'nauru'},
//                 {boxLabel: 'Niue', name: 'regions', inputValue: 'niue'},
//                 {boxLabel: 'Palau', name: 'regions', inputValue: 'palau'},
//                 {boxLabel: 'Papua New Guinea', name: 'regions', inputValue: 'png'},
//                 {boxLabel: 'Somoa', name: 'regions', inputValue: 'somoa'},
//                 {boxLabel: 'Solomon Islands', name: 'regions', inputValue: 'solomonislands'},
//                 {boxLabel: 'Tonga', name: 'regions', inputValue: 'tonga'},
//                 {boxLabel: 'Tuvalu', name: 'regions', inputValue: 'tuvalu'},
//                 {boxLabel: 'Vanuatu', name: 'regions', inputValue: 'vanuatu'}
//              ]} 
//         ]};               

    Ext.define('Country', {
        extend: 'Ext.data.Model',
        fields: ['name', 'abbr', 'zoom', 'lat', 'long', 'extend'],
        idProperty: 'abbr',
        proxy: {
            type: 'ajax',
            url: 'config/comp/countryList.json',
            reader: {
                type: 'json'
            }
        }
    });  

    window.countryStore = new Ext.data.Store({
        autoLoad: true,
        model: 'Country'
    });    
    window.countryStore.addListener('load', selectDefaultCountry);

    function selectDefaultCountry(store, records, result, operation, eOpt) {
//        window.countryCombo.setValue('pac');
        
        window.countryCombo.select('pac');
    }

    window.countryCombo = Ext.create('Ext.form.field.ComboBox', {
        fieldLabel: 'Select a country/region',
        labelAlign: 'top',
        displayField: 'name',
        valueField: 'abbr',
        store: window.countryStore,
        queryMode: 'local',
        padding: 5,
        height: '60%',
        width: 180
//        listeners: {
//            afterrender: function(combo) {
//                this.setValue('pac')
//            }
//        }
    });
        
    window.basemapLegend = Ext.create('Ext.Img', {
        src: 'images/blank.png',
        width: 1,
        height: 1
    });
    
    countryPanel = Ext.create('Ext.panel.Panel', {
        title: 'Country',
        autoScroll: true,
        items: [countryCombo],
        height: '15%'
    });
   
    datasetPanel = Ext.create('Ext.panel.Panel', {
        title: 'Dataset',
        autoScroll: true,
        height: '50%',
        contentEl: 'wrapper'
    });

    thumbnailPanel = Ext.create('Ext.panel.Panel', {
        title: 'Thumbnail',
        contentEl: 'outputDiv',
        autoScroll: true,
        height: '35%'
    });

//    legendPanel = Ext.create('Ext.panel.Panel', {
//        title: 'Legend',
//        html: '',
//        autoScroll: true,
//        height: '20%'
//    });

    Ext.create('Ext.Viewport', {
        layout: {
            type: 'border',
            padding: 2
        },
        listeners: {
            afterlayout: centerMap
        },
        defaults: {
            split: true
        },
        items: [{
            xtype: 'tabpanel',
            region: 'west',
            id: 'westDiv',
            collapsible: true,
            title: 'Control Panel',
            split: false,
//            width: '28%',
            width: 220,
            items: [{
                title: 'Maps',
                padding: 2,
                items: [
                    countryPanel,
                    datasetPanel,
                    thumbnailPanel
//                    legendPanel
//                    {
//                        title: 'Legend',
//                        items: [
//                            window.basemapLegend
//                        ]
//                    }
                ]}
//            {               
//                title: 'Pilot Projects'
//            }
            ]
        }, {
            region: 'center',
            border: false,
//          title: 'Map Panel',
            padding: 2,
//          width: '72%',
            height: '100%',
            items:[
                Ext.create('Ext.panel.Panel', {contentEl: 'map', height: '100%'}),
//                Ext.create('Ext.panel.Panel', {contentEl: 'imgDiv', height: '20%'})
            ] 
        }
//        {
//            region: 'south',
//            html: '<b>Pacific Ocean Demo Project</b><br/> More information will be available soon.',
//            height: '0%'
//        }
       ]
    });


    setupControls();
});
