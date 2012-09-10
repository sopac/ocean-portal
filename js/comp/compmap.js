/*jslint eqeq: true, undef: true, sloppy: true, sub: true, todo: true, vars: true, white: true, browser: true, windows: true */
/*
 * (c) 2012 Commonwealth of Australia
 * Australian Bureau of Meteorology, COSPPac COMP
 * All Rights Reserved
 */

var ocean = ocean || {};
var map;

$(document).ready(function() {
    map = new OpenLayers.Map("map", {
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
           'changelayer': mapBaseLayerChanged
        }
    });

    ocean.mapObj = map;

    var bathymetryLayer = new OpenLayers.Layer.MapServer("Bathymetry",
        'cgi/getMap', {
            map: "bathymetry",
            layers: ["bathymetry_10000", "bathymetry_9000", "bathymetry_8000",
                     "bathymetry_7000", "bathymetry_6000", "bathymetry_5000",
                     "bathymetry_4000", "bathymetry_3000", "bathymetry_2000",
                     "bathymetry_1000", "bathymetry_200", "bathymetry_0",
                     "land", "maritime", "capitals", "countries"]
        }, {
            wrapDateLine: true
        });

    var sstLayer = new OpenLayers.Layer.MapServer("SST",
        'cgi/getMap', {
            map: "reynolds",
            layers: ["sst_left", "sst_right", "land", "coastline"]
        }, {
            wrapDateLine: true
        });

    /* Add gauge points */
    map.addLayers([bathymetryLayer]);
    map.setBaseLayer(bathymetryLayer);

    function mapBaseLayerChanged(evt) {
        var layerName;
        var legendDiv = $('#legendDiv');

        if (evt)
            layerName = evt.layer.name;

        if (layerName == null || layerName == 'Bathymetry') {
            legendDiv.html("<p><b>Bathymetry (m)</b></p><br/><img src='images/bathymetry_ver.png' height='180'/>");
        }
        else {
            if (ocean.map_scale)
                legendDiv.html('<p><img src="' + ocean.map_scale + '" />');
            else
                legendDiv.html('<p></p>');
        }
    }

    mapBaseLayerChanged(null);
});

function selectCountry(event, args) {
    var selection = event.getValue();
    var record = window.countryStore.getById(selection);
    var zoom = record.get('zoom');
    map.zoomTo(zoom);
    map.panTo(new OpenLayers.LonLat(record.get('long'), record.get('lat')));


    ocean.area = selection;
}

//this is a callback funtion, invoked when Extjs loading is finished
function setupControls() {
    window.countryCombo.on('select', selectCountry, this);
    window.countryCombo.on('change', selectCountry, this);
}

function centerMap() {
    if (map) {
        map.setCenter(new OpenLayers.LonLat(173.00000, -13.11418), 0);
    }
}

function updateMap(layerName, data){
    ocean.map_scale = data.scale;

    if (map.getLayersByName(layerName).length != 0) {
        layer = map.getLayersByName(layerName)[0]
        map.setBaseLayer(layer);
        layer.params["raster"] = [data.mapeast, data.mapeastw, data.mapwest, data.mapwestw];
        layer.redraw(true);
    }
    else{
        var sstLayer = new OpenLayers.Layer.MapServer(layerName,
            "cgi/getMap", {
	    map: 'reynolds',
            layers: ["sst_left", "sst_right", "land", "coastline"],
            raster: [data.mapeast, data.mapeastw, data.mapwest, data.mapwestw]
        }, {
            wrapDateLine: true
        });

        map.addLayer(sstLayer);
        map.setBaseLayer(sstLayer);
    }
}


function updateSeaLevelMap(data){
    ocean.map_scale = data.scale;

    if (map.getLayersByName("Sea Level").length != 0) {
        var layer = map.getLayersByName("Sea Level")[0];
        map.setBaseLayer(layer);
        layer.params["raster"] = [data.mapeast, data.mapeastw, data.mapwest, data.mapwestw];
        layer.redraw(true);
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

        map.addLayer(slLayer);
        map.setBaseLayer(slLayer);
    }
}

Ext.require(['*']);
Ext.onReady(function() {

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
    });

    var countryPanel = Ext.create('Ext.panel.Panel', {
        title: 'Country',
        autoScroll: true,
        items: [countryCombo],
        height: '15%'
    });

    var datasetPanel = Ext.create('Ext.panel.Panel', {
        title: 'Dataset',
        autoScroll: true,
        height: '50%',
        contentEl: 'wrapper'
    });

    var thumbnailPanel = Ext.create('Ext.panel.Panel', {
        title: 'Thumbnail',
        contentEl: 'outputDiv',
        autoScroll: true,
        height: '35%'
    });

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
                Ext.create('Ext.panel.Panel', {contentEl: 'map', height: '100%'})
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
