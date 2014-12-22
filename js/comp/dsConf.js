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
            date: $.datepick.formatDate('yyyymmdd', ocean.date),
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
        selectTideGauge: function(){
            seaLevelModel.selectTideGuage(feature.properties.ID)
        },
        onSelect: function() {
            var seaLevelModel = new $.SeaLevelModel();
            if (ocean.variable != 'gauge') {
                return;
            }
            $.when(
                seaLevelModel.getData()
            ).done(function(tideGauges) { 
                ocean.dsConf.sealevel.overlay = L.geoJson(tideGauges.features, {
                    style: function(feature) {
                        return {color: '#000'};
                    },
                    onEachFeature: function(feature, layer) {
                        layer.bindPopup('<b>' + feature.properties.Description + ' (' + feature.properties.ID + ')</b> <br/><p>' + 'Latitude: ' + feature.geometry.coordinates[1] + ' Longitude: ' + feature.geometry.coordinates[0] + '</p>');
                        layer.on('popupopen', function() {
                            $("#tidalgauge").val(feature.properties.Description);
                            $("#tgId").val(feature.properties.ID);
                        });
                        layer.on('popupclose', function() {
                            $("#tidalgauge").val('');
                            $("#tgId").val('');
                        });
                    },
                    filter: function(feature, layer) {
                        return feature.properties.Region == ocean.configProps.tidalGaugeRegions;
                    }
                }).addTo(map)
            }).fail(function() {
                fatal_error("Failed to load tide gauges.");
            });

//
 //                   $('#tidalgauge').val('');
  //                  $('#tgId').val('');
   //                 $('#latitude').val('');
    //                $('#longitude').val('');
        },
        onDeselect: function() {
            var control;

            map.removeLayer(this.overlay);

//            var controls = map.getControlsByClass(
//                'OpenLayers.Control.SelectFeature');

//            for (control in controls) {
//                map.removeControl(controls[control]);
//                controls[control].deactivate();
//                controls[control].destroy();
//            }
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

