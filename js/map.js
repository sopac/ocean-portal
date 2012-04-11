    <!-- this is a test to use different navigate control-->
//    OpenLayers.ImgPath = "http://js.mapbox.com/theme/dark/";
    var popup;
    var map = new OpenLayers.Map("map", {
//        scales: [80000000, 50000000, 20000000, 10000000, 5000000, 2000000, 1000000],
        resolutions: [0.17578125,0.087890625,0.0439453125,0.02197265625,0.010986328125,0.0054931640625,0.00274658203125,0.00137329101],
//        maxResolution: 1.40625,
//        maxResolution: 0.703125,
//        maxResolution: 0.3515625,
//        maxResolution: 0.9,
//        maxResolution: auto,
//        minResolution: auto,
//       numZoomLevels: 7,
        maxResolution: 0.17578125, 
        minExtent: new OpenLayers.Bounds(-1, -1, -1, -1),
        maxExtent: new OpenLayers.Bounds(-180, -90, 180, 90),
//        maxExtent: new OpenLayers.Bounds(0, -90, 360, 90),
//        maxExtent: new OpenLayers.Bounds(-250, -50, -150, 10),
//        numZoomLevels:7,
//        restrictedExtent: new OpenLayers.Bounds(108.24697, -51.78606, 213.50869, 10.13191),
//        restrictedExtent: new OpenLayers.Bounds(108.24697, -51.78606, -156.49131, 10.13191),
        restrictedExtent: new OpenLayers.Bounds(-254.75303, -51.78606, -144.49137, 20.13191),
//        restrictedExtent: new OpenLayers.Bounds(-254.75303, -51.78606, -144.49137, 1.0000),
//        panDuration: 100,
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

    var wmsLayer = new OpenLayers.Layer.WMS("Site map",
        "http://tuscany/cgi-bin/mapserv?map=maps/sitemap.map",
        {
            layers: "land"
        },{
            wrapDateLine: true,
            transitionEffect: 'resize'
        }
    );
//    map.addLayer(wmsLayer);

    var wmsLayer = new OpenLayers.Layer.WMS("Plain World",
        "http://tuscany/cgi-bin/mapserv?map=maps/plainworld.map",
        {
            layers: "land,urban,ocean,maritime,country_line,major_countries,minor_countries,cities,towns,minor_islands"
//            layers: "land,urban,ocean,country_line,major_countries,minor_countries,cities,towns,minor_islands"
        },{
            wrapDateLine: true,
            transitionEffect: 'resize'
        }
    );
//    map.addLayer(wmsLayer);

    var bathymetryLayer = new OpenLayers.Layer.WMS("Bathymetry",
        "http://tuscany/cgi-bin/mapserv?map=maps/bathymetry.map",
        {
            layers: "bathymetry_10000,bathymetry_9000,bathymetry_8000,bathymetry_7000,bathymetry_6000,bathymetry_5000,bathymetry_4000,bathymetry_3000,bathymetry_2000,bathymetry_1000,bathymetry_200,bathymetry_0,coastline,ocean,land"
        },{
            wrapDateLine: true
        });
//    map.addLayer(bathymetryLayer);

////Below are the MapServer layers
    var mapservLayer = new OpenLayers.Layer.MapServer("Plain World",
        "http://tuscany/cgi-bin/mapserv", {
            map: "maps/world.map",
            layers: ["populated_places", "eez"]
        }, {
            'buffer': 4,
//            gutter: '2',
            wrapDateLine: true
        });
//    map.addLayer(mapservLayer);

    var bathymetryLayer = new OpenLayers.Layer.MapServer("Bathymetry",
        "http://tuscany/cgi-bin/mapserv", {
            map: "maps/bathymetry.map",
            layers: ["bathymetry_10000", "bathymetry_9000", "bathymetry_8000",
                     "bathymetry_7000", "bathymetry_6000", "bathymetry_5000",
                     "bathymetry_4000", "bathymetry_3000", "bathymetry_2000",
                     "bathymetry_1000", "bathymetry_200", "bathymetry_0",
                     "coastline", "ocean", "land", "towns"]
//            layers: ["coastline", "populated_places", "ocean"]
        }, {
            wrapDateLine: true
//            maxResolution: 0.0000453613
        });
//    map.addLayer(bathymetryLayer);

    var sstLayer = new OpenLayers.Layer.MapServer("SST",
        "http://tuscany/cgi-bin/mapserv", {
            map: "maps/sst.map",
            layers: ["sst",
                     "coastline", "land"]
        }, {
            wrapDateLine: true
//            maxResolution: 0.0000453613
        });
//    map.addLayer(sstLayer);

    function centerMap() {
        if (map) {
            map.setCenter(new OpenLayers.LonLat(-178.48551, -13.11418), 0);
            gaugesLayer.setVisibility(true);
//            map.setCenter(new OpenLayers.LonLat(-178.48551, -13.11418), 0);
//            map.setCenter(new OpenLayers.LonLat(178.62740, -17.93307), 7);
//            map.setCenter(new OpenLayers.LonLat(167.29775, -11.97161), 2);
        }
    }
    
    var eezLayer = new OpenLayers.Layer.WMS("EEZ",
        "http://tuscany/cgi-bin/mapserv?map=maps/eez.map",
        {
            layers: "maritime"
        },{
            isBaseLayer: false,
            wrapDateLine: true,
            transitionEffect: 'resize'
        }
    );
//    map.addLayer(eezLayer);

    //Add gauge points
    var gaugesLayer = new OpenLayers.Layer.Vector("Tidal gauges", {
        strategies: [new OpenLayers.Strategy.BBOX({resFactor: 1.1})],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "config/tidalGauges.txt",
            format: new OpenLayers.Format.Text()
        }),
        'calculateInRange' : function() { return true;}
    });
//    map.addLayer(gaugesLayer);
    gaugesLayer.setVisibility(false);
    map.addLayers([wmsLayer, bathymetryLayer, sstLayer,gaugesLayer]);


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
        'featureselected': onGaugeSelected
//        'featureunselected': onGaugeUnselected
    });
 
//    map.setCenter(new OpenLayers.LonLat(-178.48551, -13.11418), 2);
//    map.zoomToMaxExtent();
//    map.zoomToScale(1);

    function onGaugeSelected(evnt){
        if(popup) {
            onGaugeUnselected();
        }
        gauge = evnt.feature;
        popup = new OpenLayers.Popup.FramedCloud("gauge popup",
            gauge.geometry.getBounds().getCenterLonLat(),
            new OpenLayers.Size(200,60),
            "<h2>" + gauge.attributes.title + "</h2>"
            + gauge.attributes.description,
            null,
            true,
            onGaugeUnselected
       //     onPopupClose 
        );
        popup.autoSize = false;
        gauge.popup = popup;
        popup.feature = gauge;
        map.addPopup(popup, true);
    };
    
    function onPopupClose(evt) {
        var feature = this.feature;
        if (feature.layer) { // The feature is not destroyed
            gaugeControl.unselect(feature);
        } else { // After "moveend" or "refresh" events on POIs layer all 
            this.destroy();
        }
    }
    
    function onGaugeUnselected(evt) {
        feature = popup.feature;
        if (feature) {
            popup.hide();
        }
        if (feature.popup) {
            popup.feature = null;
            map.removePopup(feature.popup);
            feature.popup.destroy();
            feature.popup = null;
            popup = null;
        }
    }
    
   // map.panTo(new OpenLayers.LonLat(178.62740, -17.93307));
    function mapBaseLayerChanged(evt) {
        layerName = evt.layer.name;
        if (window.basemapLegend) {
            if (layerName == 'Bathymetry') {
                legendPanel.update("<p><b>Bathymetry (m)</b></p><br/><img src='images/bathymetry_ver.png' height='200'/>");
           //     basemapLegend.setSrc('images/bathymetry_ver.png'); 
           //     basemapLegend.setSize(40, 250);
            }     
            else if (layerName == 'SST') {
                legendPanel.update("<p><b>Temperature (&deg;C)</b></p><br/><img src='images/sst.png' height='200'/>");
           //     basemapLegend.setSrc('images/sst.png');
           //     basemapLegend.setSize(40, 250);
            }
            else {
                legendPanel.update("<p></p>");
          //      basemapLegend.html="<p>hello</p>";
          //      basemapLegend.setSrc('images/blank.png');
         //       basemapLegend.setSize(1, 1);
            }
        }
    } 
