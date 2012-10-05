/*jslint eqeq: true, forin: true, plusplus: true, undef: true, sloppy: true, sub: true, todo: true, vars: true, white: true, browser: true, windows: true */
/*
 * (c) 2012 Commonwealth of Australia
 * Australian Bureau of Meteorology, COSPPac COMP
 * All Rights Reserved
 */

/* Dataset specific overrides */

var ocean = ocean || {};

dateformat = 'yymmdd';

ocean.dsConf = {
    reynolds: {
        params: function() {
            return {
                dataset: 'reynolds',
                map: this.variable.get('id'),
                date: $.datepicker.formatDate(dateformat, ocean.date),
                period: ocean.period,
                area: ocean.area,
                average: ocean.dsConf['reynolds'].aveCheck.average,
                trend: ocean.dsConf['reynolds'].aveCheck.trend,
                runningAve: ocean.dsConf['reynolds'].aveCheck.runningAve,
                runningInterval: ocean.dsConf['reynolds'].runningInterval,
                timestamp: $.now()
            };
        },
        aveCheck: {},
        mainCheck: 'average',
        runningInterval: 2,
        callback: function(data) {
            if (this.variable.get("id") == "anom" &&
                this.aveCheck.average && data.aveImg != null)
            {
                appendOutput(data.aveImg, data.aveData,
                             "Average(1981-2010)",
                             Math.round(data.mean*100)/100 + '\u00B0C',
                             data);
            }
            else if (data.img != null) {
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
                updateMap(data);
            }
        },
        onSelect: null,
        onDeselect: null,
    },
    ersst: {
        params: function() {
            return {
                dataset: 'ersst',
                map: this.variable.get('id'),
                date: $.datepicker.formatDate(dateformat, ocean.date),
                period: ocean.period,
                baseYear: 1900,
                area: ocean.area,
                average: ocean.dsConf['ersst'].aveCheck.average,
                trend: ocean.dsConf['ersst'].aveCheck.trend,
                runningAve: ocean.dsConf['ersst'].aveCheck.runningAve,
                runningInterval: ocean.dsConf['ersst'].runningInterval,
                timestamp: $.now()
            };
        },
        aveCheck: {},
        mainCheck: 'average',
        runningInterval: 2,
        callback: function(data) {
            prependOutputSet();

            if (this.variable.get("id") == "anom" &&
                this.aveCheck.average && data.aveImg != null)
            {
                appendOutput(data.aveImg, data.aveData,
                             "Average(1981-2010)",
                             Math.round(data.mean*100)/100 + '\u00B0C',
                             data
                             );

            }
            else if (data.img != null) {
                appendOutput(data.img, null, null, null, data);
                updateMap(data);
            }
        },
        onSelect: null,
        onDeselect: null,
    },
    bran: {
        params: function() {
            var params = {
              dataset: 'bran',
              map: this.variable.get('id'),
              date: $.datepicker.formatDate(dateformat, ocean.date),
              period: ocean.period,
              area: ocean.area,
              timestamp: $.now()
            };

            switch (params.map) {
              case 'temp':
              case 'salt':
                  params.lat = $('#latitude').val();
                  params.lon = $('#longitude').val();
                  break;

              default:
                  break;
            }

            return params;
        },
        callback: function(data) {
            prependOutputSet();

            if (data.img != null) {
                appendOutput(data.img, null, null, null, data);
                updateMap(data);
            }
        },
        onSelect: null,
        onDeselect: null,
    },
    ww3: {
        params: function() {
            return {
                dataset: 'ww3',
                lllat: $('#latitude').val(),
                lllon: $('#longitude').val(),
                urlat: $('#latitude').val(),
                urlon: $('#longitude').val(),
                variable: this.variable.get('id'),
                date: $.datepicker.formatDate(dateformat, ocean.date),
                period: ocean.period,
                timestamp: $.now()
            };
        },
        callback: function(data) {
            prependOutputSet();

            if(data.ext != null) {
                appendOutput(data.img, data.ext);
            }
        },
        onSelect: null,
        onDeselect: null,
    },
    sealevel: {
        params: function() {
            return {
                dataset: 'sealevel',
                variable: this.variable.get('id'),
                period: ocean.period,
                date: $.datepicker.formatDate(dateformat, ocean.date),
                area: ocean.area,
                lat: $('#latitude').val(),
                lon: $('#longitude').val(),
                tidalGaugeId: $('#tgId').val(),
                timestamp: $.now()
            };
        },
        callback: function(data) {
            prependOutputSet();

            if (data.img) {
                appendOutput(data.img, null, null, null, data);
                updateMap(data);
            }

            if (data.tidimg)
                appendOutput(data.tidimg, data.tidtxt, "Tidal Gauge");

            if (data.altimg)
                appendOutput(data.altimg, data.alttxt, "Altimetry");

            if (data.recimg)
                appendOutput(data.recimg, data.rectxt, "Reconstruction");
        },
        onSelect: function() {
            if (ocean.variable != 'gauge') {
                return;
            }

            /* generate a list of filters for the configured tidal
             * gauge regions */
            var filter;
            var filters = $.map(ocean.configProps.tidalGaugeRegions,
                function (elem) {
                    return new OpenLayers.Filter.Comparison({
                        type: OpenLayers.Filter.Comparison.EQUAL_TO,
                        property: 'region',
                        value: elem
                    });

                    return new OpenLayers.Strategy.Filter({
                        filter: filter
                    });
                });

            if (filters.length > 1)
                filter = new OpenLayers.Filter.Logical({
                    type: OpenLayers.Filter.Logical.OR,
                    filters: filters
                });
            else if (filters.length == 1)
                filter = filters[0];
            else
                console.error("Abort: should not be reached");

            var gaugesLayer = new OpenLayers.Layer.Vector(
                "Tidal gauges", {
                wrapDateLine: true,
                strategies: [
                    new OpenLayers.Strategy.Fixed(),
                    new OpenLayers.Strategy.Filter({ filter: filter })
                ],
                protocol: new OpenLayers.Protocol.HTTP({
                    url: 'config/comp/tidalGauges.txt',
                    format: new OpenLayers.Format.Text({
                        extractStyles: false
                    })
                }),
                style: {
                    pointRadius: 5,
                    strokeWidth: 1,
                    strokeColor: 'white',
                    fillColor: 'black',
                    fillOpacity: 0.8
                }
            });

            ocean.mapObj.addLayer(gaugesLayer);
            gaugesLayer.redraw(true);

            var gaugeControl = new OpenLayers.Control.SelectFeature(
                gaugesLayer, {
                clickout: true,
                onSelect: function (gauge) {
                    gauge.attributes.selected = true;

                    geometry = gauge.geometry.getBounds().getCenterLonLat();
                    $('#tidalgauge').val(gauge.attributes.title);
                    $('#tgId').val(gauge.attributes.id);
                    $('#latitude').val(Math.round(geometry.lat * 1000)/1000);
                    $('#longitude').val(Math.round(geometry.lon * 1000)/1000);

                    /* highlight the selected feature */
                    gauge.style = {
                        pointRadius: 6,
                        strokeWidth: 2,
                        strokeColor: 'red',
                        fillColor: 'black',
                        fillOpacity: 0.8
                    };
                    gaugesLayer.drawFeature(gauge);
                },
                onUnselect: function (gauge) {
                    gauge.attributes.selected = false;

                    $('#tidalgauge').val('');
                    $('#tgId').val('');
                    $('#latitude').val('');
                    $('#longitude').val('');

                    /* unhighlight the feature */
                    gauge.style = null;
                    gaugesLayer.drawFeature(gauge);
                }
            });

            var gaugeHover = new OpenLayers.Control.SelectFeature(
                gaugesLayer, {
                hover: true,
                highlightOnly: true,
                eventListeners: {
                    featurehighlighted: function (e) {
                        var gauge = e.feature;
                        var col = gauge.attributes.selected ? 'red' : 'white';

                        gaugesLayer.drawFeature(gauge, {
                            label: gauge.attributes.title,
                            labelAlign: 'rb',
                            labelXOffset: 15,
                            labelYOffset: 10,
                            fontColor: 'red',
                            fontWeight: 'bold',
                            pointRadius: 5,
                            strokeWidth: 2,
                            strokeColor: 'red',
                            fillColor: 'black',
                            fillOpacity: 0.9
                        });
                    },
                    featureunhighlighted: function (e) {
                        var gauge = e.feature;

                        gaugesLayer.drawFeature(gauge);
                    }
                }
            });

            map.addControl(gaugeHover);
            map.addControl(gaugeControl);

            gaugeHover.activate();
            gaugeControl.activate();
        },
        onDeselect: function() {
            var control;

            layers = map.getLayersByName("Tidal gauges");
            for (layer in layers) {
                map.removeLayer(layers[layer]);
            }

            var controls = map.getControlsByClass(
                'OpenLayers.Control.SelectFeature');

            for (control in controls) {
                map.removeControl(controls[control]);
                controls[control].deactivate();
                controls[control].destroy();
            }
        },
    }
};

