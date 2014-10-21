/*jslint eqeq: true, forin: true, plusplus: true, undef: true, sloppy: true, sub: true, todo: true, vars: true, white: true, browser: true, windows: true */
/*
 * (c) 2012 Commonwealth of Australia
 * Australian Bureau of Meteorology, COSPPac COMP
 * All Rights Reserved
 */

/* Dataset specific overrides */

var ocean = ocean || {};

function override(paramsfunc) {
    return function () {
        /* default parameters */
        out = {
            dataset: getBackendId(ocean.datasetid),
            variable: getBackendId(ocean.datasetid, ocean.variable),
            plot: ocean.plottype,
            date: $.datepicker.formatDate('yymmdd', ocean.date),
            period: ocean.period,
            area: ocean.area,
            timestamp: $.now()
        };

        if (paramsfunc) {
            $.extend(out, paramsfunc(ocean.dataset));
        }

        return out;
    };
}

ocean.dsConf = {
    reynolds: {
        params: override(function (dataset) { return {
            average: dataset.aveCheck.average,
            trend: dataset.aveCheck.trend,
            runningAve: dataset.aveCheck.runningAve,
            runningInterval: dataset.runningInterval
        };}),
        aveCheck: {},
        mainCheck: 'average',
        runningInterval: 2,
        callback: function(data) {
            if (ocean.variable == 'sstanom' &&
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
        onDeselect: null
    },
    ersst: {
        params: override(function (dataset) { return {
            baseYear: 1950,
            average: dataset.aveCheck.average,
            trend: dataset.aveCheck.trend,
            runningAve: dataset.aveCheck.runningAve,
            runningInterval: dataset.runningInterval
        };}),
        aveCheck: {},
        mainCheck: 'average',
        runningInterval: 2,
        callback: function(data) {
            prependOutputSet();

            if (ocean.variable == 'sstanom' &&
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
        onDeselect: null
    },
    bran: {
        params: override(function (dataset) {
            switch (ocean.plottype) {
              case 'xsections':
                  return { lat: $('#latitude').val(),
                           lon: $('#longitude').val() };
                  break;

              default:
                  return {};
            }

            return params;
        }),
        callback: function(data) {
            prependOutputSet();

            if (data.img != null) {
                appendOutput(data.img, null, null, null, data);
                updateMap(data);
            }
        },
        onSelect: null,
        onDeselect: null
    },
    ww3: {
        params: override(function (dataset) { return {
            lllat: $('#latitude').val(),
            lllon: $('#longitude').val(),
            urlat: $('#latitude').val(),
            urlon: $('#longitude').val()
        };}),
        callback: function(data) {
            prependOutputSet();

            if(data.ext != null) {
                appendOutput(data.img, data.ext);
            }
        },
        onSelect: null,
        onDeselect: null
    },
    sealevel: {
        params: override(function (dataset) { return {
            lat: $('#latitude').val(),
            lon: $('#longitude').val(),
            tidalGaugeId: $('#tgId').val()
        };}),
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
        }
    }
};

function appendOutput(image, dataURL, name, extras, data)
{
    var captionText = ""
    if (dataURL) {
        captionText = "<a class='download-data' href=" + dataURL+ " target='_blank'><span class='ui-icon ui-icon-arrowreturnthick-1-s'></span>Download Data</a>"
    }
    if (extras) {
        captionText = captionText + extras
    }
    fotorama.push({img: image, caption: captionText});
    if (fotorama.size > 20) {//TODO extract 20 to the config
        fotorama.shift();
    }
    fotorama.show(fotorama.size - 1);

    if (name) {
        $('<h2>', {
            text: name
        }).appendTo(captionText);
    }

    if (data) {
        updateMap(data);
    }
}

