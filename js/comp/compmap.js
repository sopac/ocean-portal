/*jslint eqeq: true, undef: true, sloppy: true, sub: true, todo: true, vars: true, white: true, browser: true, windows: true */
/*
 * (c) 2012 Commonwealth of Australia
 * Australian Bureau of Meteorology, COSPPac COMP
 * All Rights Reserved
 */

var ocean = ocean || {};
var map;

function fatal_error(msg)
{
    $('#error-dialog-content').html(msg);
    $('#error-dialog-request').hide();
    $('#error-dialog').dialog('option', { 'modal': true,
                                          'dialogClass': 'notitle',
                                          'closeOnEscape': false });
    $('#error-dialog').dialog('open');
}

window.onerror = function (msg, url, line) {
    fatal_error("Javascript error: " + msg + " &mdash; please " +
                '<a href="javascript:location.reload()">' +
                "reload</a> your browser." + "<br/><small>"
                + url + ":" + line + "</small>");
    return false;
}

$(document).ready(function() {
    /* work out which region file to load */
    if (location.search == '')
        ocean.config = 'pac';
    else
        ocean.config = location.search.slice(1);

    /* request the portals config */
    $.getJSON('config/comp/portals.json')
        .success(function(data, status_, xhr) {
            ocean.configProps = data[ocean.config];

            if (!ocean.configProps) {
                fatal_error("No portal called '" + ocean.config + "'.");
                return;
            }

            $('title').html(ocean.configProps.name + " Ocean Maps Portal");

        })
        .error(function (xhr, status_, error) {
            fatal_error("Error loading portals config " + "&mdash; " + error);
        });
});

function createMap () {
    map = new OpenLayers.Map("map", {
        resolutions: [0.087890625,0.0439453125,0.02197265625,0.010986328125,0.0054931640625,0.00274658203125,0.00137329101],
        maxResolution: 0.087890625,
        maxExtent: new OpenLayers.Bounds(-180, -90, 180, 90),
        // restrictedExtent: ocean.configProps.extents,
        controls: [
            new OpenLayers.Control.PanZoomBar(),
            new OpenLayers.Control.MousePosition(),
            new OpenLayers.Control.LayerSwitcher({
                div: document.getElementById('mapControlsLayers'),
                ascending: false,
                roundedCorner: false
            }),
            new OpenLayers.Control.ScaleLine({
                bottomOutUnits: '',
                bottomInUnits: ''
            }),
            new OpenLayers.Control.Navigation({
                dragPanOptions: { enableKinetic: true },
                documentDrag: true
            })
        ],
        eventListeners: {
           'changelayer': mapBaseLayerChanged
        }
    });

    /* add keyboard controls separately so we can disable them when required */
    var keyboardControls = new OpenLayers.Control.KeyboardDefaults();
    map.addControl(keyboardControls);

    $('input').focusin(function () {
        keyboardControls.deactivate();
    });
    $('input').focusout(function () {
        keyboardControls.activate();
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
            transitionEffect: 'resize',
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
        var layer = new OpenLayers.Layer.MapServer(layerName,
            'cgi/getMap', {
            map: 'raster',
            layers: ['raster_left', 'raster_right', 'land', 'coastline'],
            raster: [data.mapeast, data.mapeastw, data.mapwest, data.mapwestw]
        }, {
            transitionEffect: 'resize',
            wrapDateLine: true
        });

        map.addLayer(layer);
        map.setBaseLayer(layer);
    }
}

Ext.require(['*']);
Ext.onReady(function() {

    var countrylisturl = [ 'config', ocean.config, 'countryList.json' ].join('/');

    Ext.define('Country', {
        extend: 'Ext.data.Model',
        fields: ['name', 'abbr', 'zoom', 'lat', 'long', 'extend'],
        idProperty: 'abbr',
        proxy: {
            type: 'ajax',
            url: countrylisturl,
            reader: {
                type: 'json'
            }
        }
    });

    createMap();

    window.countryStore = new Ext.data.Store({
        autoLoad: true,
        model: 'Country',
        listeners: {
            load: function () {
                window.countryCombo.select(ocean.config);
            }
        }
    });

    function selectCountry(event, args) {
        var selection = event.getValue();
        var record = window.countryStore.getById(selection);

        if (!record)
            return;

        map.zoomTo(record.get('zoom'));
        map.panTo(new OpenLayers.LonLat(record.get('long'), record.get('lat')));

        ocean.area = selection;
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
        width: 180,
        listeners: {
            select: selectCountry,
            change: selectCountry
        }
    });

    Ext.create('Ext.Viewport', {
        layout: {
            type: 'border',
            padding: 2
        },
        items: [{
            xtype: 'panel',
            region: 'west',
            id: 'westDiv',
            collapsible: true,
            title: 'Parameters',
            width: 225,
            border: false,
            layout: 'border',
            items: [{
                xtype: 'panel',
                region: 'north',
                items: [countryCombo]
            }, {
                xtype: 'panel',
                region: 'center',
                autoScroll: true,
                contentEl: 'wrapper'
            }, {
                xtype: 'panel',
                region: 'south',
                height: 100,
                title: 'Map Controls',
                contentEl: 'mapControls'
            }]
        }, {
            xtype: 'panel',
            region: 'center',
            border: false,
            padding: 2,
            height: '100%',
            contentEl: 'map',
            listeners: {
                afterlayout: function() {
                    map.updateSize();
                }
            }
        }, {
            xtype: 'panel',
            region: 'east',
            collapsible: true,
            title: 'Output',
            width: 220,
            autoScroll: true,
            contentEl: 'outputDiv',
            tools: [{
                /* FIXME: how to make them in the style of tool buttons? */
                /* Report Feedback */
                html: $('<a>', {
                    'class': 'ui-icon ui-icon-mail-closed',
                    title: "Report Feedback",
                    href: 'mailto:COSPPac_SoftwareSupport@bom.gov.au'
                }).get(0).outerHTML
            }, {
                /* Help Guide */
                html: $('<a>', {
                    'class': 'ui-icon ui-icon-help',
                    title: "User Guide",
                    href: '/cosppac/comp/ocean-portal/ocean-portal-help.shtml',
                    target: '_blank'
                }).get(0).outerHTML
            }]
        }
       ]
    });
  });
