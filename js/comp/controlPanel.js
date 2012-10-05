/*jslint eqeq: true, forin: true, plusplus: true, undef: true, sloppy: true, sub: true, todo: true, vars: true, white: true, browser: true, windows: true */
/*
 * (c) 2012 Commonwealth of Australia
 * Australian Bureau of Meteorology, COSPPac COMP
 * All Rights Reserved
 */

var ocean = ocean || {};
ocean.controls = [
    'plottype',
    'period',
    'date',
    'month',
    'year',
    'tidalgauge',
    'latitude',
    'longitude',
    'dataset',
    'dshelp'
];

ocean.compare = { limit: 24 };
ocean.processing = false;
ocean.date = new Date();

/* set up JQuery UI elements */
$(document).ready(function() {

    /* initialise jQueryUI elements */
    $('.dialog').dialog({
        autoOpen: false,
        resizable: false
    });
    $('button').button();

    $('#enlargeDiv').hide();
    hideControls();

    /* set up the loading dialog */
    $('#loading-dialog').dialog('option', { 'modal': true,
                                            'dialogClass': 'notitle',
                                            'closeOnEscape': false,
                                            'height': 55,
                                            'resizable': false });

    $(".datepicker").datepick({
        // minDate: dateRange.minDate,
        // maxDate: dateRange.maxDate,
        // yearRange: dateRange.minYear + ":" + dateRange.maxYear,
        dateFormat: 'yyyy/mm/dd',
        firstDay: 1,
        renderer: $.extend({},
                  $.datepick.weekOfYearRenderer,
                      {picker: $.datepick.defaultRenderer.picker.
                      replace(/\{link:clear\}/, '').
                      replace(/\{link:close\}/, '')
                   }),
        showOtherMonths: true,
        showOnFocus: false
    }).mousedown(function() {
        $(this).datepick('show');
    });

    /* UI handlers */
    $('#submit').click(function () {
        console.log("CLICKED");
    });

    /* Variable */
    $('#variable').change(function () {
        var varid = $('#variable option:selected').val();

        if (!(varid in ocean.variables)) {
            return;
        }

        ocean.variable = varid;

        if (varid == '--') {
            hideControls();
            return;
        }

        /* filter the options list */
        var plots = ocean.variables[varid].plots;

        filterOpts('plottype', plots);
        showControl('plottype');
        selectFirstIfRequired('plottype');
    });

    /* Plot Type */
    $('#plottype').change(function () {
        var plottype = $('#plottype option:selected').val();

        if (!(plottype in ocean.variables[ocean.variable].plots)) {
            return;
        }

        ocean.plottype = plottype;

        /* filter the period list */
        var periods = ocean.variables[ocean.variable].plots[plottype];

        filterOpts('period', periods);
        showControl('period');
        selectFirstIfRequired('period');
        showControl('dataset');

        /* FIXME: consider exposing these in CSS ? */
        /* plot specific controls */
        switch (plottype) {
            case 'xsections':
            case 'histogram':
            case 'waverose':
                showControl('latitude');
                showControl('longitude');
                addPointLayer();
                break;

            default:
                hideControl('latitude');
                hideControl('longitude');
                removePointLayer();
                break;
        }
    });

    /* Period */
    $('#period').change(function () {
        var period = $('#period option:selected').val();

        if (!period) {
            return;
        }

        ocean.period = period;

        /* FIXME: consider exposing these in CSS ? */
        /* period specific date controls */
        switch (period) {
            case 'daily':
            case 'weekly':
                showControl('date');
                hideControl('month');
                hideControl('year');
                break;

            default:
                hideControl('date');
                showControl('month');
                showControl('year');
                break;
        }

        /* plot specific date controls */
        switch (plottype) {
            case 'histogram':
            case 'waverose':
                hideControl('year');
                break;

            default:
                /* pass */
                break;
        }
    });

    /* Date range is changed */
    $('#date, #month, #year').change(function () {

        if (!(ocean.variable in ocean.variables) ||
            !(ocean.plottype in ocean.variables[ocean.variable].plots) ||
            !(ocean.period in ocean.variables[ocean.variable].plots[ocean.plottype])) {
            return;
        }

        /* filter datasets based on the chosen range */
        datasets = $.grep(
            ocean.variables[ocean.variable].plots[ocean.plottype][ocean.period],
            function(elem) {
                /* FIXME: filter by date range */
                return true;
        });

        /* sort by rank */
        datasets.sort(function (a, b) {
            var ar = 'rank' in ocean.datasets[a] ? ocean.datasets[a].rank : 0;
            var br = 'rank' in ocean.datasets[b] ? ocean.datasets[b].rank : 0;

            return br - ar;
        });

        /* clear previous choices */
        $('#dataset option').remove();

        $.each(datasets, function (i, dataset) {
            $('<option>', {
                value: dataset,
                text: ocean.datasets[dataset].name
            }).appendTo('#dataset');
        });

        /* select first */
        $('#dataset option:first').attr('selected', true);
        $('#dataset').change();
    });

    /* Dataset */
    $('#dataset').change(function () {
        var datasetid = $('#dataset option:selected').val();

        if (!datasetid) {
            return;
        }

        var backendid = getBackendId(datasetid);

        if (!backendid in ocean.dsConf) {
            return;
        }

        if (ocean.dataset && ocean.dataset.onDeselect) {
            ocean.dataset.onDeselect();
        }

        ocean.dataset = ocean.dsConf[backendid];

        /* update about file */
        showControl('dshelp');
        $('#dshelp').attr('href', ocean.datasets[datasetid].help);
        $('#dshelp span').html(ocean.datasets[datasetid].name);

        selectMapLayer("Bathymetry");

        if (ocean.dataset.onSelect) {
            ocean.dataset.onSelect();
        }
    });

    /* show the tidal gauge name in the title text */
    $('#tidalgauge').hover(function () {
        /* copy the value into the title */
        this.title = this.value;
    });

    var groupings = {};

    /* load JSON configuration */
    $.when(
        /* Load and parse vargroups.json */
        $.getJSON('config/comp/vargroups.json').success(function(data) {
            $.each(data, function(k, v) {
                $('<optgroup>', {
                    id: k,
                    label: v.name
                }).appendTo('#variable');

                $.each(v.vars, function(i, var_) {
                    groupings[var_] = k;
                });
            });
        }),

        /* Load and parse datasets.json */
        $.getJSON('config/comp/datasets.json').success(function(data) {
            ocean.datasets = {};
            ocean.variables = {};

            $.each(data, function(i, dataset) {
                ocean.datasets[dataset.id] = dataset;

                $.each(dataset.variables, function(k, variable) {
                    if (!ocean.variables[variable.id]) {
                        ocean.variables[variable.id] = {
                            name: variable.name,
                            plots: {}
                        };
                    }

                    $.each(variable.plottypes, function(k, plottype) {
                        if (!ocean.variables[variable.id].plots[plottype]) {
                            ocean.variables[variable.id].plots[plottype] = {};
                        }

                        $.each(variable.periods, function(k, period) {
                            if (!ocean.variables[variable.id].plots[plottype][period]) {
                                ocean.variables[variable.id].plots[plottype][period] = [];
                            }

                            ocean.variables[variable.id].plots[plottype][period].push(dataset.id);
                        });
                    });
                });

            });
        })
    )
    /* Successfully fetched all JSON */
    .done(function() {
        $.each(ocean.variables, function (k, v) {
            var parent_;

            if (k in groupings) {
                parent_ = $('#variable optgroup#' + groupings[k]);

                if (parent_.length == 0) {
                    parent_ = $('#variable');
                }
            } else {
                parent_ = $('#variable');
            }

            $('<option>', {
                text: v.name,
                value: k
            }).appendTo(parent_);
        });
    })

    /* Failed to load some JSON */
    .fail(function() {
        fatal_error("Failed to load portal configuration.");
    });

});

Date.prototype.getMonthString = function() {
    var calMonth = String(this.getMonth() + 1);
    return (calMonth < 10) ?  ('0' + calMonth) : calMonth;
};

/**
 * getBackendId:
 *
 * Get the backend id for a given frontend id.
 *
 * Returns: the backend id for the given frontend id
 */
function getBackendId(datasetid) {
    var dataset = ocean.datasets[datasetid];

    /* FIXME: handle variables too */

    if ('bid' in dataset) {
        return dataset.bid;
    } else {
        return dataset.id;
    }
}

/**
 * getDateRange:
 *
 * Get the date range for a variable.
 *
 * Returns: (minDate, maxDate)
 */
function getDateRange(datasetid, varid)
{
}

/**
 * filterOpts:
 *
 * Filter @comboid so that it only contains options with the ids given in
 * @keys.
 */
function filterOpts(comboid, keys) {
    var select = $('#' + comboid);

    if (!keys) {
        console.warn("filterOpts was provided no keys for " + comboid);
        select.find('optgroup, option').show();
        return;
    }

    select.find('optgroup').hide();
    select.find('option').each(function () {
        var opt = $(this);

        if (opt.val() in keys) {
            opt.parent('optgroup').show();
            opt.show();
        } else {
            opt.hide();
        }
    });
}

/**
 * selectFirstIfRequired:
 *
 * Select the first <option> of a <select> if there is no visible option
 * selected at the moment.
 */
function selectFirstIfRequired(comboid) {
    var combo = $('#' + comboid);

    if (combo.find('option:selected:visible').length == 0) {
        combo.find('option:visible:first').attr('selected', true);
        combo.change();
    }
}

/**
 * addPointLayer:
 *
 * Adds a point selection layer to the map.
 */
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

/**
 * removePointLayer:
 *
 * Removes a point selection layer from the map.
 */
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

function _controlVarParent(control) {
    return $('#' + control).parent('.controlvar');
}

function _showhideControlGroups() {
}

/**
 * showControl:
 *
 * Shows a div.controlvar based on the id of the field within it.
 */
function showControl(control) {
    var parent = _controlVarParent(control);

    parent.show();
    parent.parent('.controlgroup').show();

    $('#' + control).change();
}

/**
 * hideControl:
 *
 * Hides a div.controlvar based on the id of the field within it.
 */
function hideControl(control) {
    var parent = _controlVarParent(control)
    var group = parent.parent('.controlgroup');

    parent.hide();

    /* hide control group if required */
    if (group.children('.controlvar:visible').length == 0) {
        group.hide();
    }
}

/**
 * hideControls:
 *
 * Hides all controls.
 */
function hideControls() {
    $.each(ocean.controls, function (i, control) {
        hideControl(control);
    });
}

/**
 * updatePage:
 *
 * Make a request to the backend based on the currently selected controls.
 */
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
