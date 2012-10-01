/*jslint eqeq: true, forin: true, plusplus: true, undef: true, sloppy: true, sub: true, todo: true, vars: true, white: true, browser: true, windows: true */
/*
 * (c) 2012 Commonwealth of Australia
 * Australian Bureau of Meteorology, COSPPac COMP
 * All Rights Reserved
 */

var ocean = ocean || {};
ocean.controls = ['selectionDiv', 'toggleDiv', 'sliderDiv',
                  'yearMonthDiv', 'datepickerDiv', 'latlonDiv',
                  'tidalGaugeDiv', 'clearlatlonButton' ];
ocean.compare = { limit: 24 };
ocean.processing = false;
ocean.MIN_YEAR = 1949;
ocean.dateFormat = 'yyyymmdd';
ocean.date = new Date();

var LABEL_WIDTH;
var FIELD_WIDTH;

/* set up JQuery UI elements */
$(document).ready(function() {
    /* synchronise the Ext label and field widths with CSS */
    LABEL_WIDTH = $('.controlvar .label').width();
    FIELD_WIDTH = $('.controlvar .field').width() + LABEL_WIDTH;

    /* Hack ExtJS field classes into non-ExtJS fields */
    $('.controlvar .label').addClass('x-form-item x-form-item-label');
    $('.controlvar .field').addClass('x-form-item x-form-text x-form-field x-border-box');

    /* initialise dialogs */
    $('.dialog').dialog({
        autoOpen: false,
        resizable: false
    });

    /* set up the loading dialog */
    $('#loading-dialog').dialog('option', { 'modal': true,
                                            'dialogClass': 'notitle',
                                            'closeOnEscape': false,
                                            'height': 55,
                                            'resizable': false });

    $.getJSON('config/comp/datasets.json', function(data) {
        var dialog = $('#about-datasets');

        $.each(data, function(k, dataset) {
            /* Add to the datasets dialog */
            $('<h1>', { text: dataset.name }).appendTo(dialog);

            var ul = $('<ul>').appendTo(dialog);

            $.each(dataset.variables, function(k, variable) {
                $('<li>', { text: variable.name }).appendTo(ul);
            });

        });
    });

    /* show the tidal gauge name in the title text */
    $('#tidalgauge').hover(function () {
        /* copy the value into the title */
        this.title = this.value;
    });
});

Date.prototype.getMonthString = function() {
    var calMonth = String(this.getMonth() + 1);
    return (calMonth < 10) ?  ('0' + calMonth) : calMonth;
};

function prependOutputSet()
{
    while ($('#outputDiv div.outputgroup').length >= ocean.compare.limit) {
        $('#outputDiv div.outputgroup:last').remove();
    }

    var div = $('<div>', {
        'class': 'outputgroup'
    }).prependTo($('#outputDiv'));

    /* remove button */
    $('<span>', {
        'class': 'close-button ui-icon ui-icon-close',
        title: "Remove",
        click: function () {
            div.fadeTo('fast', 0);
            div.slideUp('fast', function () { div.remove(); });
        }
    }).appendTo(div);

    $('<p>', {
        'class': 'date',
        text: new Date().toLocaleTimeString()
    }).appendTo(div);


    /* scroll to the top of the output div */
    $('#outputDiv').animate({ scrollTop: 0 }, 75);
}

function createOutput(image, dataURL, name, extras)
{
    var div = $('<div>', {
        'class': 'thumbnail'
    });

    if (name)
        $('<h2>', {
            text: name
        }).appendTo(div);

    var a = $('<a>', {
        'class': 'raster',
        href: image,
        title: "Click to open in a new window",
        target: '_blank'
    }).appendTo(div);

    var img = $('<img>', {
        src: image + '?' + $.param({ time: $.now() })
    }).appendTo(a);

    div.hide();
    img.load(function () {
        /* this kludge is required for IE7, where it turns out you can't do
         * slideDown on a block contained in a relative positioned parent
         * unless that block has a defined height */
        if ($.browser.msie && $.browser.version == '7.0')
            div.css('height', div.height());

        div.slideDown();
    });

    img.hover(
        function (e) {
            enlargeImg(this, true);
        },
        function (e) {
            enlargeImg(this, false);
        });

    $('<div>', {
        'class': 'overlay ui-icon ui-icon-newwin'
    }).appendTo(div);

    if (dataURL)
        $('<a>', {
            'class': 'download-data',
            href: dataURL,
            target: '_blank',
            html: '<span class="ui-icon ui-icon-arrowreturnthick-1-s"></span>Download Data'
        }).appendTo(div);

    if (extras)
        $('<span>', {
            html: extras
        }).appendTo(div);

    return div;
}

function appendOutput()
{
    createOutput.apply(null, arguments).appendTo($('#outputDiv .outputgroup:first'));
}

function prependOutput()
{
    createOutput.apply(null, arguments).prependTo($('#outputDiv .outputgroup:first'));
}

function addPointLayer () {
    var layer = new OpenLayers.Layer.Vector("point-layer",
        {
            wrapDateLine: true,
            style: {
                graphicName: 'cross',
                pointRadius: 10,
                stroke: false
            },
            preFeatureInsert: function(feature) {
                this.removeAllFeatures();
            },
            onFeatureInsert: function(feature) {
                var geometry = feature.geometry;
                var lon = Math.round(geometry.x * 1000) / 1000;
                var lat = Math.round(geometry.y * 1000) / 1000;

                /* correct for wrapping issues from OpenLayers */
                if (lon < -180)
                    lon += 360;

                $('#latitude').val(lat);
                $('#longitude').val(lon);
            }
        });

    ocean.mapObj.addLayer(layer);

    this.panelControls = [
        new OpenLayers.Control.DrawFeature(layer,
            OpenLayers.Handler.Point, {
                displayClass: 'olControlDrawFeaturePoint',
                title: "Select a point on the map"
            }),
        new OpenLayers.Control.Navigation({
                title: "Zoom and pan the map"
            })
    ];

    this.toolbar = new OpenLayers.Control.Panel({
        displayClass: 'olControlEditingToolbar',
        defaultControl: this.panelControls[0],
        div: document.getElementById('mapControlsToolbar')
    });

    this.toolbar.addControls(this.panelControls);
    ocean.mapObj.addControl(this.toolbar);

    /* track changes to the lat/lon and move the feature */
    $('#latitude, #longitude').change(function () {
        var lat = $('#latitude').val();
        var lon = $('#longitude').val();

        layer.removeAllFeatures();

        if (lat != '' && lon != '')
            layer.addFeatures([
                new OpenLayers.Feature.Vector(
                    new OpenLayers.Geometry.Point(lon, lat))
            ]);
    });

    /* update the map with the initial lat/lon */
    $('#latitude').change();
}

function removePointLayer () {
    var layers = map.getLayersByName("point-layer");

    if (layers.length == 0)
        return;

    for (layer in layers) {
        map.removeLayer(layers[layer]);
    }

    if (this.toolbar) {
        map.removeControl(this.toolbar);
        this.toolbar.deactivate();
        this.toolbar.destroy();
    }

    for (control in this.panelControls) {
        map.removeControl(this.panelControls[control]);
        this.panelControls[control].deactivate();
        this.panelControls[control].destroy();
    }

    /* remove event handlers */
    $('#latitude, #longitude').unbind();

    this.toolbar = null;
    this.panelControls = null;
}

ocean.dsConf = {
    reynolds: {params: function() { return {
                    dataset: 'reynolds',
                    map: this.variable.get('id'),
                    date: $.datepick.formatDate(ocean.dateFormat, ocean.date),
                    period: ocean.period,
                    area: ocean.area,
                    average: ocean.dsConf['reynolds'].aveCheck.average,
                    trend: ocean.dsConf['reynolds'].aveCheck.trend,
                    runningAve: ocean.dsConf['reynolds'].aveCheck.runningAve,
                    runningInterval: ocean.dsConf['reynolds'].runningInterval,
                    timestamp: $.now()
                }; },
                aveCheck: {},
                mainCheck: 'average',
                runningInterval: 2,
                setData: function(data) {
                    this.data = data;
                    dateRange = this.data.get('dateRange');
                    minDate = $.datepick.parseDate(ocean.dateFormat, dateRange.minDate);
                    maxDate = $.datepick.parseDate(ocean.dateFormat, dateRange.maxDate);
                    var minYear = parseInt(dateRange["minYear"], 10);
                    var maxYear = parseInt(dateRange["maxYear"], 10);

                    dateRange.yearFilter = Ext.create('Ext.util.Filter', {filterFn: function (item) {
                        var year = item.data.field1;
                        var filter = item.store.filters.items[0];
                            return year >= filter.minYear && year <= filter.maxYear;
                        },
                        minYear: minYear,
                        maxYear: maxYear});

                },
                callback: function(data) {
                        if (this.variable.get("id") == "anom" &&
                            this.aveCheck.average && data.aveImg != null)
                        {
                            appendOutput(data.aveImg, data.aveData,
                                         "Average(1981-2010)",
                                         Math.round(data.mean*100)/100 + '\u00B0C');
                        }
                        else if (data.img != null) {
                            prependOutputSet();
                            appendOutput(data.img);
                            updateMap("Reynolds", data);
                        }
                },
                onSelect: function(){
                              showControl('variableDiv');
                              configCalendar();
                          },
                onDeselect: function() {
                    layers = map.getLayersByName("Reynolds");
                    for (layer in layers) {
                        map.removeLayer(layers[layer]);
                    }
                },
                selectVariable: function(selection) {
                                    updatePeriodCombo();
                                    dateRange = this.data.get('dateRange');
                                    updateYearCombo(dateRange.yearFilter);
                                    minDate = $.datepick.parseDate(ocean.dateFormat, dateRange.minDate);
                                    maxDate = $.datepick.parseDate(ocean.dateFormat, dateRange.maxDate);
                                    if (ocean.date != null) {
                                        if (ocean.date < minDate) {
                                            ocean.date = minDate;
                                        }
                                        else if (ocean.date > maxDate) {
                                            ocean.date = maxDate;
                                        }
                                    }
                                    else {
                                        ocean.date = maxDate;
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
//                update
            },
    ersst: {params: function() {return {
                    dataset: 'ersst',
                    map: this.variable.get('id'),
                    date: $.datepick.formatDate(ocean.dateFormat, ocean.date),
                    period: ocean.period,
                    baseYear: 1900,
                    area: ocean.area,
                    average: ocean.dsConf['ersst'].aveCheck.average,
                    trend: ocean.dsConf['ersst'].aveCheck.trend,
                    runningAve: ocean.dsConf['ersst'].aveCheck.runningAve,
                    runningInterval :ocean.dsConf['ersst'].runningInterval,
                    timestamp: $.now()
                }; },
                data: null,
                aveCheck: {},
                mainCheck: 'average',
                runningInterval: 2,
                setData: function(data) {
                    this.data = data;
                    dateRange = this.data.get('dateRange');
                    minDate = $.datepick.parseDate(ocean.dateFormat, dateRange.minDate);
                    maxDate = $.datepick.parseDate(ocean.dateFormat, dateRange.maxDate);
                    var minYear = parseInt(dateRange["minYear"], 10);
                    var maxYear = parseInt(dateRange["maxYear"], 10);
                    dateRange.yearFilter = Ext.create('Ext.util.Filter', {filterFn: function (item) {
                        var year = item.data.field1;
                        var filter = item.store.filters.items[0];
                            return year >= filter.minYear && year <= filter.maxYear;
                        },
                        minYear: minYear,
                        maxYear: maxYear});
                },
                callback: function(data) {
                    prependOutputSet();

                    if (this.variable.get("id") == "anom" &&
                        this.aveCheck.average && data.aveImg != null)
                    {
                        appendOutput(data.aveImg, data.aveData,
                                     "Average(1981-2010)",
                                     Math.round(data.mean*100)/100 + '\u00B0C'
                                     );

                    }
                    else if (data.img != null) {
                        appendOutput(data.img);
                        updateMap("ERSST", data);
                    }
                },
                onSelect: function(){
                              showControl('variableDiv');
                              configCalendar();
                          },
                onDeselect: function() {
                    var layers = map.getLayersByName("ERSST");
                    var layer;

                    for (layer in layers) {
                        map.removeLayer(layers[layer]);
                    }
                },
                selectVariable: function(selection) {
                                    updatePeriodCombo();
                                    dateRange = this.data.get('dateRange');
                                    updateYearCombo(dateRange.yearFilter);
                                    minDate = $.datepick.parseDate(ocean.dateFormat, dateRange.minDate);
                                    maxDate = $.datepick.parseDate(ocean.dateFormat, dateRange.maxDate);
                                    if (ocean.date != null) {
                                        if (ocean.date < minDate) {
                                            ocean.date = minDate;
                                        }
                                        else if (ocean.date > maxDate) {
                                            ocean.date = maxDate;
                                        }
                                    }
                                    else {
                                        ocean.date = maxDate;
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
    bran: {params: function() {
                  var params = {
                    dataset: 'bran',
                    map: this.variable.get('id'),
                    date: $.datepick.formatDate(ocean.dateFormat, ocean.date),
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
                data: null,
                setData: function(data) {
                    this.data = data;
                    dateRange = this.data.get('dateRange');
                    minDate = $.datepick.parseDate(ocean.dateFormat, dateRange.minDate);
                    maxDate = $.datepick.parseDate(ocean.dateFormat, dateRange.maxDate);
                    var minYear = parseInt(dateRange["minYear"], 10);
                    var maxYear = parseInt(dateRange["maxYear"], 10);
                    dateRange.yearFilter = Ext.create('Ext.util.Filter', {filterFn: function (item) {
                        var year = item.data.field1;
                        var filter = item.store.filters.items[0];
                            return year >= filter.minYear && year <= filter.maxYear;
                        },
                        minYear: minYear,
                        maxYear: maxYear});
                },
                callback: function(data) {
                    prependOutputSet();

                    if (data.img != null) {
                        appendOutput(data.img);
                        updateMap("BRAN", data);
                    }
                },
                onSelect: function()
                {
                    showControl('variableDiv');
                    configCalendar();
                },
                onDeselect: function() {
                    var layers = map.getLayersByName("BRAN");
                    var layer;

                    for (layer in layers) {
                        map.removeLayer(layers[layer]);
                    }

                    removePointLayer();
                    hideControl('clearlatlonButton');
                },
                selectVariable: function(selection) {
                    updatePeriodCombo();
                    dateRange = this.data.get('dateRange');
                    updateYearCombo(dateRange.yearFilter);
                    minDate = $.datepick.parseDate(ocean.dateFormat, dateRange.minDate);
                    maxDate = $.datepick.parseDate(ocean.dateFormat, dateRange.maxDate);
                    if (ocean.date != null) {
                        if (ocean.date < minDate) {
                            ocean.date = minDate;
                        }
                        else if (ocean.date > maxDate) {
                            ocean.date = maxDate;
                        }
                    }
                    else {
                        ocean.date = maxDate;
                    }

                    switch (selection) {
                        /* these variables support cross sections */
                        case 'temp':
                        case 'salt':
                            removePointLayer();
                            addPointLayer();
                            showControl('latlonDiv');
                            break;

                        default:
                            removePointLayer();
                            hideControl('latlonDiv');
                            break;
                    }

                    updateCalDiv();
                    showControl('selectionDiv');
                    showControl('clearlatlonButton');
                }
    },
    ww3: {params: function() { return {
                dataset: 'ww3',
                lllat: $('#latitude').val(),
                lllon: $('#longitude').val(),
                urlat: $('#latitude').val(),
                urlon: $('#longitude').val(),
                variable: this.variable.get('id'),
                date: $.datepick.formatDate(ocean.dateFormat, ocean.date),
                period: ocean.period,
                timestamp: $.now()
            }; },
            data: null,
            panelControls: null,
            toolbar: null,
            setData: function(data) {
                this.data = data;
            },
            callback: function(data) {
                prependOutputSet();

                if(data.ext != null) {
                    appendOutput(data.img, data.ext);
                }
            },
            onSelect: function() {
                showControl('variableDiv');
            },
            onDeselect: function() {
                var layers = map.getLayersByName("WaveWatch III");
                var layer;

                for (layer in layers) {
                    map.removeLayer(layers[layer]);
                }

                removePointLayer();
                showControl('yearDiv');
            },
            selectVariable: function(selection) {
                updatePeriodCombo();
                updateCalDiv();
                showControl('selectionDiv');
                hideControl('yearDiv');
                showControl('latlonDiv');

                removePointLayer();
                addPointLayer();
            }
    },
    sealevel: {params: function() { return {
                dataset: 'sealevel',
                variable: this.variable.get('id'),
                period: ocean.period,
                date: $.datepick.formatDate(ocean.dateFormat, ocean.date),
                area: ocean.area,
                lat: $('#latitude').val(),
                lon: $('#longitude').val(),
                tidalGaugeId: $('#tgId').val(),
                timestamp: $.now()
            }; },
            data: null,
            setData: function(data) {
                this.data = data;
                var items = this.data.variables().data.items;
                for (var itemIndex in items) {
                    var record = items[itemIndex];
                    var dateRange = record.get("dateRange")
                    var minDate = $.datepick.parseDate(ocean.dateFormat, dateRange["minDate"]);
                    var maxDate = $.datepick.parseDate(ocean.dateFormat, dateRange["maxDate"]);
                    var minYear = parseInt(dateRange["minYear"], 10);
                    var maxYear = parseInt(dateRange["maxYear"], 10);

                    dateRange.yearFilter = Ext.create('Ext.util.Filter', {filterFn: function (item) {
                        var year = item.data.field1;
                        var filter = item.store.filters.items[0]
//                        if(ocean.date != null) {
//                            return Ext.Array.contains(ocean.dataset.variable.get('periods'), item.data.field1);
//                        }
//                        else {
                            return year >= filter.minYear && year <= filter.maxYear;
//                        }
                        },
                        minYear: minYear,
                        maxYear: maxYear});
                }
            },
            callback: function(data) {
                prependOutputSet();

                if (data.img) {
                    appendOutput(data.img);
                    updateMap("Sea Level", data);
                }

                if (data.tidimg)
                    appendOutput(data.tidimg, data.tidtxt, "Tidal Gauge");

                if (data.altimg)
                    appendOutput(data.altimg, data.alttxt, "Altimetry");

                if (data.recimg)
                    appendOutput(data.recimg, data.rectxt, "Reconstruction");
            },
            onSelect: function() {
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

                showControl('variableDiv');
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
                        },
            selectVariable: function(selection) {
                                updatePeriodCombo();

                                var record = this.data.variables().getById(selection);
                                dateRange = record.get("dateRange")
                                updateYearCombo(dateRange.yearFilter);
                                minDate = $.datepick.parseDate(ocean.dateFormat, dateRange["minDate"]);
                                maxDate = $.datepick.parseDate(ocean.dateFormat, dateRange["maxDate"]);
                                if (ocean.date != null) {
                                    if (ocean.date < minDate) {
                                        ocean.date = minDate
                                    }
                                    else if (ocean.date > maxDate) {
                                        ocean.date = maxDate
                                    }
                                }
                                else {
                                    ocean.date = maxDate;
                                }
                                showControl('selectionDiv');
                                updateCalDiv();
                                $('#tidalGaugeDiv').show();
                            }
    }


};

function enlargeImg(img, show) {
    var enlargeDiv = $('#enlargeDiv');

    if (show) {
        enlargeDiv.stop(true, true);
        $('#enlargeDiv img').remove();
        var eimg = $('<img>', {
            src: img.src,
            'class' : 'imagepreview'
        }).appendTo(enlargeDiv);

        /* fix broken positioning in IE7 */
        if ($.browser.msie && $.browser.version == '7.0') {
            var eimgraw = eimg.get(0);

            var offset = eimg.offset();
            eimg.offset({
                top: offset.top + enlargeDiv.height() / 2 - eimgraw.height / 2,
                left: offset.left + enlargeDiv.width() / 2 - eimgraw.width / 2
            });
        }

        enlargeDiv.fadeIn(100);
        enlargeDiv.show();
    }
    else {
        enlargeDiv.stop(true, true);
        enlargeDiv.delay(100);
        enlargeDiv.fadeOut(150, function () {
            enlargeDiv.html('');
            enlargeDiv.hide();
        });
    }
}

function AveCheck(id, state) {
    this.id = id;
    this.state = state;
}

Ext.require(['*']);
Ext.onReady(function() {
    Ext.Loader.setConfig({enabled:true});

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

    var hbox = Ext.create('Ext.container.Container', {
        layout: {
            type: 'hbox'
        },
        renderTo: 'datasetDiv',
        width: 200
    });

    ocean.datasetCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'datasetCombo',
        fieldLabel: 'Dataset',
        labelWidth: LABEL_WIDTH,
        width: FIELD_WIDTH,
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

    Ext.create('Ext.Button', {
        html: '<span class="ui-icon ui-icon-close" title="Clear Latitude/Longitude"></span>',
        margin: { top: 3, bottom: 3 },
        renderTo: 'clearlatlonButton',
        handler: function() {
            /* clear the latitude/longitude */
            $('#latitude').val('');
            $('#longitude').val('');
            /* trigger a change */
            $('#latitude').change();
        }
    });

    ocean.mapCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'variableCombo',
        fieldLabel: 'Variable',
        labelWidth: LABEL_WIDTH,
        width: FIELD_WIDTH,
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
        labelWidth: LABEL_WIDTH,
        width: FIELD_WIDTH,
        displayField: 'name',
        valueField: 'id',
        renderTo: 'selectionDiv',
        triggerAction: 'all',
        queryMode: 'local',
        store: ocean.periods,
        lastQuery: '',
        listeners: {
            'change': selectPeriod
        }
    });

    ocean.runningAveSlider = Ext.create('Ext.slider.Single', {
        renderTo: 'sliderDiv',
        hideLabel: true,
        id: 'runningAveSlider',
        width: FIELD_WIDTH,
        minValue: 2,
        maxValue: 15,
        listeners: {
            'changecomplete': selectRunningInterval
        }
    });

    Ext.create('Ext.Button', {
        renderTo: 'submitbuttonDiv',
        text: 'Submit',
        handler: function() {
            updatePage();
        }
    });

    ocean.monthStore = Ext.create('Ext.data.Store', {
        fields: ['name', 'id'],
        data: [{'name': 'January', 'id': '01'},
               {'name': 'February', 'id': '02'},
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
        labelWidth: LABEL_WIDTH,
        width: FIELD_WIDTH,
        displayField: 'name',
        valueField: 'id',
        renderTo: 'monthDiv',
        queryMode: 'local',
        lastQuery: '',
        store: ocean.monthStore,
        listeners: {
            'select': function(event, args) {
                ocean.date.setMonth(parseInt(event.getValue(), 10) - 1, 1);
            }
        }
    });

    var currentYear = new Date().getFullYear();
    var minYear = ocean.MIN_YEAR;
    var yearRange = range(minYear, currentYear);
    ocean.yearCombo = Ext.create('Ext.form.field.ComboBox', {
        id: 'yearCombo',
        fieldLabel: 'Year',
        labelWidth: LABEL_WIDTH,
        width: FIELD_WIDTH,
        renderTo: 'yearDiv',
        queryMode: 'local',
        autoScroll: true,
        lastQuery: '',
        store: yearRange,
        listeners: {
            'select': function(event, args) {
                ocean.date.setFullYear(event.getValue(),
                                       ocean.monthCombo.getValue() - 1,
                                       1);
            }
        }
    });

    $('#variableDiv').hide();
    $('#enlargeDiv').hide();
    hideControls();
});

function createCheckBoxes(store, records, result, operation, eOpt) {
    data = [];
    records = store.getById('reynolds').variables().getById('anom').get('average').checkboxes; 
    Ext.each(records, function(rec) {
        var name = rec.name;
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

                    var periodCombo = Ext.getCmp('periodCombo');
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
////                    updateCalDiv();
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
    ocean.dsConf[selection].setData(record);

    if (ocean.dataset != null) {
        ocean.dataset.onDeselect();
    }

    ocean.dataset = ocean.dsConf[selection];
    $('#dstitle').html(record.get('title'));
    $('#dshelp').html('About File');
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
        ocean.calendar.datepick('option', {'minDate': dateRange.minDate,
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
        minDate: dateRange.minDate,
        maxDate: dateRange.maxDate,
        yearRange: dateRange.minYear + ":" + dateRange.maxYear,
        dateFormat: ocean.dateFormat,
        firstDay: 1,
        showTrigger: '#calImg',
        renderer: $.extend({},
                  $.datepick.weekOfYearRenderer,
                      {picker: $.datepick.defaultRenderer.picker.
                      replace(/\{link:clear\}/, '').
                      replace(/\{link:close\}/, '')
                   }),
        showOtherMonths: true,
        onSelect: function (dateObj) {
            ocean.date = dateObj.length? dateObj[0] : null
        },
        showOnFocus: false
    });
    $( "#datepicker" ).mousedown(function() {
        $(this).datepick('show');
    });
}

function selectVariable(event, args) {
    hideControls();
    var selection = event.getValue();
    var record = ocean.dataset.data.variables().getById(selection);
    ocean.dataset.variable = record;
    ocean.dataset.selectVariable(selection);

}

function selectPeriod(event, args) {
    if (event.getValue() != null) {
        ocean.period = event.getValue();
        updateCalDiv();
    }
}

function range(start, end) {
    var rangeArray = [];
    while(start <= end){
        rangeArray.push(start++);
    }
    return rangeArray
}

function updateYearCombo(yearFilter) {
    var yearCombo = Ext.getCmp('yearCombo');
    //yearCombo.setAutoScroll('auto');
//    yearCombo.getPicker().setAutoScroll(true);
    yearCombo.clearValue();
    var store = yearCombo.store;
    store.clearFilter(true);
    store.filter([yearFilter]);
//    yearCombo.picker.height = 300;
//    yearCombo.updateLayout();
    //yearCombo.getPicker().doComponentLayout();
//    yearCombo.doComponentLayout();
}

function updatePeriodCombo() {
    var periodCombo = Ext.getCmp('periodCombo');
    periodCombo.clearValue();
    var store = periodCombo.store;
    store.clearFilter(true);
    store.filter([periodFilter]);
    if (store.find('id', ocean.period) != -1) {
        periodCombo.setValue(ocean.period)
    }
    else {
        periodCombo.setValue(store.data.keys[0])
    } 
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

        if (ocean.period == 'yearly')
            hideControl('monthDiv');
        else /* monthly, 3 monthly, 6 monthly */
            showControl('monthDiv');

        ocean.monthCombo.select(ocean.date.getMonthString());
        ocean.yearCombo.select(ocean.date.getFullYear());
    }
}

function selectRunningInterval(slider, value, thumb, args) {
    ocean.dataset.runningInterval = value;
}

function hideControls() {
   var control;
   for (control in ocean.controls) {
       $('#' + ocean.controls[control]).hide();
   }
}

function showControl(control) {
    $('#' + control).show();
}

function hideControl(control) {
    $('#' + control).hide();
}

//**********************************************************
//Ajax processing
//**********************************************************
function updatePage() {
    if (!ocean.processing) {

        if (!ocean.dataset)
            return;

        if (!ocean.dataset.variable)
            return;

        function show_error(params, text)
        {
            var url = 'cgi/portal.py?' + $.param(params);

            $('#error-dialog-content').html(text);
            $('#error-dialog-request').prop('href', url);
            $('#error-dialog').dialog('open');
        }

        $.ajax({
            url: 'cgi/portal.py',
            data: ocean.dataset.params(),
            dataType: 'json',
            beforeSend: function(jqXHR, settings) {
                ocean.processing = true;
                $('#loading-dialog').dialog('open');
                $('#error-dialog').dialog('close');
            },
            success: function(data, textStatus, jqXHR) {
                if (data == null || $.isEmptyObject(data))
                {
                    show_error(ocean.dataset.params(), "returned no data");
                }
                else
                {
                    if (data.error)
                        show_error(ocean.dataset.params(), data.error);
                    else
                        ocean.dataset.callback(data);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (textStatus == 'parsererror')
                    show_error(ocean.dataset.params(),
                               "Unable to parse server response.");
                else
                    show_error(ocean.dataset.params(), errorThrown);
            },
            complete: function(jqXHR, textStatus) {
                ocean.processing = false;
                $('#loading-dialog').dialog('close');
            }
        });
    }
}
